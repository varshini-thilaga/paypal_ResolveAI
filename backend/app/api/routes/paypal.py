from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from backend.app.api.deps import get_paypal_client, get_auth_manager
from backend.app.core.security import PaymentAuthorizationManager
from backend.app.services.paypal_client import PayPalClient, PayPalClientError, PaymentOperationUnauthorizedError
from backend.app.schemas.paypal import (
    PayPalHealthCheckResponse,
    AuthorizationStepRequest,
    AuthorizationStepResponse,
    ExecuteRefundRequest,
    RefundResultResponse,
)

router = APIRouter(prefix="/paypal", tags=["PayPal Sandbox"])


@router.get("/health", response_model=PayPalHealthCheckResponse)
async def check_paypal_health(
    paypal_client: PayPalClient = Depends(get_paypal_client)
) -> PayPalHealthCheckResponse:
    """
    Verifies connection to PayPal Sandbox and checks OAuth 2.0 token acquisition.
    NOTE: Never exposes client secrets or bearer access tokens in the response.
    """
    token_status = paypal_client.get_token_status()
    try:
        # Attempt to retrieve/refresh OAuth 2.0 token
        await paypal_client.get_access_token()
        token_status = paypal_client.get_token_status()
        return PayPalHealthCheckResponse(
            status="ok",
            environment=token_status["environment"],
            base_url=token_status["base_url"],
            authenticated=True,
            token_valid=token_status["token_valid"],
            token_expires_in_seconds=token_status["token_expires_in_seconds"],
            client_id_masked=token_status["client_id_masked"]
        )
    except PayPalClientError as err:
        return PayPalHealthCheckResponse(
            status=f"error: {str(err)}",
            environment=token_status["environment"],
            base_url=token_status["base_url"],
            authenticated=False,
            token_valid=False,
            token_expires_in_seconds=0,
            client_id_masked=token_status["client_id_masked"]
        )


@router.post("/authorize-step", response_model=AuthorizationStepResponse)
async def authorize_payment_step(
    request: AuthorizationStepRequest,
    auth_manager: PaymentAuthorizationManager = Depends(get_auth_manager)
) -> AuthorizationStepResponse:
    """
    STEP 1: Explicit Authorization Step.
    
    Any refund or payment-changing action MUST first be explicitly authorized.
    This creates a single-use cryptographic token required for execution.
    """
    token_info = auth_manager.generate_authorization_token(
        operation=request.operation,
        target_id=request.target_id,
        amount=request.amount,
        ttl_seconds=300,
        authorized_by=request.reviewer_id
    )

    return AuthorizationStepResponse(
        status="AUTHORIZED",
        authorization_token=token_info["authorization_token"],
        operation=request.operation,
        target_id=request.target_id,
        amount=request.amount,
        currency=request.currency,
        expires_at=token_info["expires_at"],
        ttl_seconds=token_info["ttl_seconds"]
    )


@router.post("/refunds/execute", response_model=RefundResultResponse)
async def execute_refund(
    request: ExecuteRefundRequest,
    paypal_client: PayPalClient = Depends(get_paypal_client)
) -> RefundResultResponse:
    """
    STEP 2: Execution Step.
    
    Executes a refund using the authorization token created during Step 1.
    If the authorization token is missing, expired, or invalid, the execution is blocked.
    """
    try:
        result = await paypal_client.execute_refund(
            capture_id=request.capture_id,
            idempotency_key=request.idempotency_key,
            authorization_token=request.authorization_token,
            amount=request.amount,
            currency=request.currency,
            note_to_payer=request.note_to_payer
        )
        return RefundResultResponse(
            status=result.get("status", "COMPLETED"),
            refund_id=result.get("id"),
            capture_id=request.capture_id,
            amount=request.amount,
            currency=request.currency,
            idempotency_key=request.idempotency_key,
            message="Refund successfully processed in PayPal Sandbox."
        )
    except PaymentOperationUnauthorizedError as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(err)
        )
    except PayPalClientError as err:
        raise HTTPException(
            status_code=err.status_code or status.HTTP_502_BAD_GATEWAY,
            detail=str(err)
        )


@router.get("/orders/{order_id}")
async def get_order(
    order_id: str,
    paypal_client: PayPalClient = Depends(get_paypal_client)
) -> Dict[str, Any]:
    """Read-only order lookup in PayPal sandbox."""
    try:
        return await paypal_client.get_order_details(order_id)
    except PayPalClientError as err:
        raise HTTPException(status_code=err.status_code or 500, detail=str(err))


@router.get("/disputes/{dispute_id}")
async def get_dispute(
    dispute_id: str,
    paypal_client: PayPalClient = Depends(get_paypal_client)
) -> Dict[str, Any]:
    """Read-only dispute lookup in PayPal sandbox."""
    try:
        return await paypal_client.get_dispute_details(dispute_id)
    except PayPalClientError as err:
        raise HTTPException(status_code=err.status_code or 500, detail=str(err))
