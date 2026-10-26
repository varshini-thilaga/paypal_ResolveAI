import hmac
import hashlib
import time
import secrets
from typing import Dict, Any, Optional


def mask_secret(value: Optional[str], visible_prefix: int = 4, visible_suffix: int = 4) -> str:
    """
    Safely mask a secret string for display/logging without leaking sensitive data.
    """
    if not value:
        return "<EMPTY>"
    if len(value) <= (visible_prefix + visible_suffix):
        return "***"
    return f"{value[:visible_prefix]}...{value[-visible_suffix:]}"


class PaymentAuthorizationManager:
    """
    Security manager requiring an explicit, multi-stage authorization step
    prior to executing any money-movement or payment-changing actions (e.g. refunds).
    """

    def __init__(self, secret_key: str):
        self._secret = secret_key.encode("utf-8")
        # In-memory store of consumed nonces to prevent replay attacks
        self._consumed_nonces: set[str] = set()

    def generate_authorization_token(
        self,
        operation: str,
        target_id: str,
        amount: Optional[str] = None,
        ttl_seconds: int = 300,
        authorized_by: str = "merchant_reviewer"
    ) -> Dict[str, Any]:
        """
        Generates an explicit, time-limited cryptographic authorization token
        for a specific payment-changing operation (e.g. refunding capture_id).
        """
        nonce = secrets.token_hex(16)
        expires_at = int(time.time()) + ttl_seconds
        payload = f"{operation}:{target_id}:{amount or '0.00'}:{authorized_by}:{expires_at}:{nonce}"
        signature = hmac.new(self._secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()

        return {
            "authorization_token": f"{payload}::{signature}",
            "operation": operation,
            "target_id": target_id,
            "amount": amount,
            "authorized_by": authorized_by,
            "expires_at": expires_at,
            "ttl_seconds": ttl_seconds
        }

    def verify_and_consume_token(
        self,
        auth_token_str: str,
        expected_operation: str,
        expected_target_id: str,
        expected_amount: Optional[str] = None
    ) -> bool:
        """
        Verifies that an authorization token is authentic, unexpired, matches the exact
        operation/target/amount, and has not been used previously (single-use guarantee).
        """
        if not auth_token_str or "::" not in auth_token_str:
            return False

        try:
            payload, signature = auth_token_str.split("::", 1)
            parts = payload.split(":")
            if len(parts) != 6:
                return False

            op, target, amt, authorized_by, expires_str, nonce = parts

            # 1. Operation match check
            if op != expected_operation or target != expected_target_id:
                return False

            if expected_amount and amt != expected_amount:
                return False

            # 2. Expiration check
            if int(expires_str) < int(time.time()):
                return False

            # 3. Replay attack check
            if nonce in self._consumed_nonces:
                return False

            # 4. Signature check
            expected_sig = hmac.new(self._secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected_sig, signature):
                return False

            # Mark nonce as consumed
            self._consumed_nonces.add(nonce)
            return True

        except Exception:
            return False
