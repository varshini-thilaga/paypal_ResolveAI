import asyncio
import logging
import time
from typing import Optional, Dict, Any
import httpx
from pydantic import SecretStr

from backend.app.core.config import Settings
from backend.app.core.security import PaymentAuthorizationManager, mask_secret

logger = logging.getLogger("resolveai.paypal")


class PayPalClientError(Exception):
    """Base exception for PayPal client errors with sensitive data sanitization."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class PaymentOperationUnauthorizedError(PayPalClientError):
    """Raised when a payment-changing operation lacks mandatory authorization."""
    pass


class PayPalClient:
    """
    Robust PayPal Sandbox Integration Client.
    
    Features:
    - OAuth 2.0 client credentials token acquisition & automatic token caching.
    - Zero credential exposure in logs or serializations.
    - Read operations (orders, captures, disputes).
    - Mandatory multi-step authorization guard on payment-changing operations (refunds).
    """

    def __init__(self, settings: Settings, auth_manager: Optional[PaymentAuthorizationManager] = None):
        self.settings = settings
        self.base_url = settings.PAYPAL_BASE_URL.rstrip("/")
        self.client_id = settings.PAYPAL_CLIENT_ID
        self._client_secret: SecretStr = settings.PAYPAL_CLIENT_SECRET
        self.auth_manager = auth_manager or PaymentAuthorizationManager(
            secret_key=settings.SESSION_SECRET.get_secret_value()
        )

        self._cached_token: Optional[str] = None
        self._token_expires_at: float = 0.0
        self._lock = asyncio.Lock()

    def is_configured(self) -> bool:
        """Checks whether client has non-empty credentials configured."""
        secret_val = self._client_secret.get_secret_value()
        return bool(self.client_id and secret_val and "placeholder" not in self.client_id.lower())

    async def get_access_token(self, force_refresh: bool = False) -> str:
        """
        Retrieves a valid OAuth 2.0 Bearer access token.
        Utilizes cached token if still valid (with a 60-second safety margin).
        """
        async with self._lock:
            now = time.time()
            # Reuse cached token if valid for at least 60 more seconds
            if not force_refresh and self._cached_token and self._token_expires_at > (now + 60):
                return self._cached_token

            secret_val = self._client_secret.get_secret_value()
            if not self.client_id or not secret_val:
                raise PayPalClientError("PayPal credentials not configured. Please supply PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET in .env.")

            logger.info("Requesting new OAuth 2.0 token from PayPal sandbox (%s)", self.base_url)

            token_url = f"{self.base_url}/v1/oauth2/token"
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.post(
                        token_url,
                        data={"grant_type": "client_credentials"},
                        auth=(self.client_id, secret_val),
                        headers={
                            "Accept": "application/json",
                            "Accept-Language": "en_US"
                        }
                    )

                if response.status_code != 200:
                    err_msg = f"OAuth 2.0 token request failed with status {response.status_code}"
                    logger.error("PayPal OAuth failure: %s (Client ID: %s)", err_msg, mask_secret(self.client_id))
                    raise PayPalClientError(err_msg, status_code=response.status_code)

                data = response.json()
                token = data.get("access_token")
                expires_in = data.get("expires_in", 3600)

                if not token:
                    raise PayPalClientError("PayPal returned 200 OK but access_token was missing in payload")

                self._cached_token = token
                self._token_expires_at = time.time() + float(expires_in)

                logger.info("Successfully refreshed PayPal OAuth 2.0 token. Valid for %d seconds.", expires_in)
                return self._cached_token

            except httpx.RequestError as exc:
                logger.error("Network error connecting to PayPal OAuth: %s", type(exc).__name__)
                raise PayPalClientError(f"Network error connecting to PayPal: {type(exc).__name__}")

    def get_token_status(self) -> Dict[str, Any]:
        """Provides status of the OAuth 2.0 token cache without exposing the token."""
        now = time.time()
        is_valid = bool(self._cached_token and self._token_expires_at > now)
        remaining = int(self._token_expires_at - now) if is_valid else 0
        return {
            "token_valid": is_valid,
            "token_expires_in_seconds": remaining if is_valid else 0,
            "environment": self.settings.PAYPAL_ENV,
            "base_url": self.base_url,
            "client_id_masked": mask_secret(self.client_id)
        }

    async def _send_authenticated_request(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        custom_headers: Optional[Dict[str, str]] = None
    ) -> httpx.Response:
        """Helper to send authenticated REST requests to PayPal API."""
        token = await self.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if custom_headers:
            headers.update(custom_headers)

        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=20.0) as client:
            return await client.request(method, url, json=json_data, headers=headers)

    # -------------------------------------------------------------
    # Read-Only APIs (Orders, Captures, Disputes)
    # -------------------------------------------------------------

    async def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """Lookup order details by PayPal order ID."""
        resp = await self._send_authenticated_request("GET", f"/v2/checkout/orders/{order_id}")
        if resp.status_code != 200:
            raise PayPalClientError(f"Failed to fetch order {order_id}: {resp.status_code}", resp.status_code)
        return resp.json()

    async def get_capture_details(self, capture_id: str) -> Dict[str, Any]:
        """Lookup capture payment details by capture ID."""
        resp = await self._send_authenticated_request("GET", f"/v2/payments/captures/{capture_id}")
        if resp.status_code != 200:
            raise PayPalClientError(f"Failed to fetch capture {capture_id}: {resp.status_code}", resp.status_code)
        return resp.json()

    async def get_dispute_details(self, dispute_id: str) -> Dict[str, Any]:
        """Lookup PayPal dispute details by dispute ID."""
        resp = await self._send_authenticated_request("GET", f"/v1/customer-disputes/{dispute_id}")
        if resp.status_code != 200:
            raise PayPalClientError(f"Failed to fetch dispute {dispute_id}: {resp.status_code}", resp.status_code)
        return resp.json()

    # -------------------------------------------------------------
    # Payment-Changing APIs (Protected by Explicit Authorization Step)
    # -------------------------------------------------------------

    async def execute_refund(
        self,
        capture_id: str,
        idempotency_key: str,
        authorization_token: str,
        amount: Optional[str] = None,
        currency: Optional[str] = "USD",
        note_to_payer: Optional[str] = "Refund issued per ResolveAI policy"
    ) -> Dict[str, Any]:
        """
        Executes a full or partial refund against a captured payment.
        
        CRITICAL GUARDRAIL:
        This operation CANNOT be called automatically without an explicit,
        verified authorization token generated from the separate authorization step.
        """
        # Step 1: Verify explicit authorization token
        is_authorized = self.auth_manager.verify_and_consume_token(
            auth_token_str=authorization_token,
            expected_operation="REFUND",
            expected_target_id=capture_id,
            expected_amount=amount
        )

        if not is_authorized:
            logger.warning(
                "REFUND BLOCKED: Attempted refund on capture %s without valid authorization step.",
                capture_id
            )
            raise PaymentOperationUnauthorizedError(
                "Payment-changing operation refused: Missing, expired, or invalid authorization token. "
                "Refunds strictly require an explicit, separate authorization step."
            )

        # Step 2: Build payload
        payload: Dict[str, Any] = {}
        if amount:
            payload["amount"] = {
                "value": amount,
                "currency_code": currency or "USD"
            }
        if note_to_payer:
            payload["note_to_payer"] = note_to_payer

        # Step 3: Execute with PayPal-Request-Id header for idempotency
        headers = {
            "PayPal-Request-Id": idempotency_key
        }

        logger.info("Executing authorized refund for capture %s (Idempotency: %s)", capture_id, idempotency_key)
        resp = await self._send_authenticated_request(
            method="POST",
            path=f"/v2/payments/captures/{capture_id}/refund",
            json_data=payload if payload else None,
            custom_headers=headers
        )

        if resp.status_code not in (200, 201):
            err_data = resp.json() if resp.headers.get("content-type") == "application/json" else {}
            err_msg = err_data.get("message", f"Refund failed with status {resp.status_code}")
            logger.error("Refund failed on capture %s: %s", capture_id, err_msg)
            raise PayPalClientError(f"PayPal refund rejected: {err_msg}", resp.status_code)

        return resp.json()
