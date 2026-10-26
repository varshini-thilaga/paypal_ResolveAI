from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class PayPalHealthCheckResponse(BaseModel):
    """Sanitized health check response that NEVER exposes credentials or tokens."""
    status: str = Field(description="Connection status: ok or error")
    environment: str = Field(description="PayPal environment mode")
    base_url: str = Field(description="Target base URL")
    authenticated: bool = Field(description="Whether OAuth 2.0 handshake succeeded")
    token_valid: bool = Field(description="Whether a valid OAuth 2.0 token is cached")
    token_expires_in_seconds: Optional[int] = Field(default=None, description="Time until cached token expires")
    client_id_masked: str = Field(description="Masked Client ID for identity verification")


class AuthorizationStepRequest(BaseModel):
    """Step 1 Request: Explicit authorization required prior to any money movement."""
    operation: str = Field(default="REFUND", description="Operation type (e.g. REFUND, ACCEPT_CLAIM)")
    target_id: str = Field(description="Capture ID or Dispute ID to authorize")
    amount: Optional[str] = Field(default=None, description="Requested monetary amount (empty for full refund)")
    currency: Optional[str] = Field(default="USD", description="Currency code (USD default)")
    reason: str = Field(description="Business or policy reason for authorization")
    reviewer_id: str = Field(default="merchant_admin", description="Merchant reviewer approving the step")


class AuthorizationStepResponse(BaseModel):
    """Step 1 Response: Returns single-use time-limited authorization token."""
    status: str = "AUTHORIZED"
    authorization_token: str = Field(description="Cryptographic single-use token needed for execution")
    operation: str
    target_id: str
    amount: Optional[str]
    currency: Optional[str]
    expires_at: int
    ttl_seconds: int
    note: str = "This token is required to execute the action in Step 2 within ttl_seconds."


class ExecuteRefundRequest(BaseModel):
    """Step 2 Request: Execution of refund requiring authorization token from Step 1."""
    capture_id: str = Field(description="PayPal Capture ID to refund")
    authorization_token: str = Field(description="Token obtained from Step 1 authorization")
    amount: Optional[str] = Field(default=None, description="Refund amount if partial; None for full refund")
    currency: Optional[str] = Field(default="USD", description="Currency code")
    note_to_payer: Optional[str] = Field(default="Refund issued per ResolveAI policy review", description="Customer note")
    idempotency_key: str = Field(description="Unique idempotency key to prevent double-refunds")


class RefundResultResponse(BaseModel):
    """Execution response for refund."""
    status: str
    refund_id: Optional[str] = None
    capture_id: str
    amount: Optional[str] = None
    currency: Optional[str] = None
    idempotency_key: str
    message: str
