import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from backend.app.core.config import Settings
from backend.app.core.security import PaymentAuthorizationManager, mask_secret
from backend.app.services.paypal_client import (
    PayPalClient,
    PayPalClientError,
    PaymentOperationUnauthorizedError
)
from backend.app.main import app


def test_settings_and_masking():
    """Verify settings read env variables and prevent secret exposure."""
    settings = Settings(
        PAYPAL_CLIENT_ID="BAAz3rXJ4hxKiyOQgPWr6UNFBEbcGq4TMwAsvh5zK49_ckOT_476KvcowWgBnS3LPnGKFbUf01-n8PrcOA",
        PAYPAL_CLIENT_SECRET="EJ8GCg9eUDI_lNF1cocG-TvfyMgUSFmBHxTGGMV421YgZgRarR8qMXs-HnrxGWjVkKTLwGT3WLGLgtZ6",
        PAYPAL_BASE_URL="https://api-m.sandbox.paypal.com",
        PAYPAL_ENV="sandbox"
    )

    assert settings.PAYPAL_ENV == "sandbox"
    assert settings.PAYPAL_BASE_URL == "https://api-m.sandbox.paypal.com"
    assert settings.PAYPAL_CLIENT_ID.startswith("BAAz")

    # Verify secret string representation is masked
    assert "EJ8G" not in str(settings.PAYPAL_CLIENT_SECRET)
    assert "EJ8G" not in repr(settings.PAYPAL_CLIENT_SECRET)

    # Verify mask helper
    masked = mask_secret(settings.PAYPAL_CLIENT_ID)
    assert masked.startswith("BAAz")
    assert masked.endswith("rcOA")
    assert "..." in masked


def test_payment_authorization_guardrail():
    """Verify two-step authorization tokens are enforced, validated, and single-use."""
    manager = PaymentAuthorizationManager(secret_key="test-secret-key-123")

    # Step 1: Generate explicit authorization token
    auth_data = manager.generate_authorization_token(
        operation="REFUND",
        target_id="CAPTURE-98765",
        amount="25.00",
        ttl_seconds=60,
        authorized_by="reviewer_jane"
    )
    token = auth_data["authorization_token"]
    assert token is not None

    # Step 2: Mismatched operation should fail
    assert not manager.verify_and_consume_token(
        auth_token_str=token,
        expected_operation="ACCEPT_CLAIM",
        expected_target_id="CAPTURE-98765",
        expected_amount="25.00"
    )

    # Step 3: Mismatched target ID should fail
    assert not manager.verify_and_consume_token(
        auth_token_str=token,
        expected_operation="REFUND",
        expected_target_id="CAPTURE-DIFFERENT",
        expected_amount="25.00"
    )

    # Step 4: Correct match succeeds
    assert manager.verify_and_consume_token(
        auth_token_str=token,
        expected_operation="REFUND",
        expected_target_id="CAPTURE-98765",
        expected_amount="25.00"
    )

    # Step 5: Replay attack fails (token can only be consumed once)
    assert not manager.verify_and_consume_token(
        auth_token_str=token,
        expected_operation="REFUND",
        expected_target_id="CAPTURE-98765",
        expected_amount="25.00"
    )


@pytest.mark.asyncio
async def test_paypal_client_token_caching():
    """Verify PayPal client caches OAuth token and reuses it."""
    settings = Settings(
        PAYPAL_CLIENT_ID="mock-client-id",
        PAYPAL_CLIENT_SECRET="mock-secret",
        PAYPAL_BASE_URL="https://api-m.sandbox.paypal.com",
        PAYPAL_ENV="sandbox"
    )
    client = PayPalClient(settings=settings)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "access_token": "mock-access-token-xyz",
        "token_type": "Bearer",
        "expires_in": 3600
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        # First call retrieves token via API
        token1 = await client.get_access_token()
        assert token1 == "mock-access-token-xyz"
        assert mock_post.call_count == 1

        # Second call returns cached token without network request
        token2 = await client.get_access_token()
        assert token2 == "mock-access-token-xyz"
        assert mock_post.call_count == 1


@pytest.mark.asyncio
async def test_execute_refund_requires_authorization():
    """Verify refund cannot be executed without valid authorization token."""
    settings = Settings(
        PAYPAL_CLIENT_ID="mock-client-id",
        PAYPAL_CLIENT_SECRET="mock-secret",
        PAYPAL_BASE_URL="https://api-m.sandbox.paypal.com",
        PAYPAL_ENV="sandbox"
    )
    client = PayPalClient(settings=settings)

    # Attempting refund with missing or invalid token MUST raise PaymentOperationUnauthorizedError
    with pytest.raises(PaymentOperationUnauthorizedError) as exc_info:
        await client.execute_refund(
            capture_id="CAPTURE-12345",
            idempotency_key="idemp-key-1",
            authorization_token="invalid-or-missing-token",
            amount="50.00"
        )
    assert "Missing, expired, or invalid authorization token" in str(exc_info.value)


def test_api_health_endpoint():
    """Verify GET /api/paypal/health responds properly and exposes zero secrets."""
    client = TestClient(app)
    response = client.get("/api/paypal/health")
    assert response.status_code == 200
    data = response.json()

    assert data["environment"] == "sandbox"
    assert data["base_url"] == "https://api-m.sandbox.paypal.com"
    # Ensure sensitive fields are not in response payload
    assert "client_secret" not in data
    assert "access_token" not in data
    assert "authorization" not in data


def test_api_two_step_authorization_and_refund_flow():
    """Verify full Step 1 (Authorize) -> Step 2 (Execute) workflow via REST endpoints."""
    client = TestClient(app)

    # 1. Direct execute without token fails with 403 Forbidden
    unauth_resp = client.post("/api/paypal/refunds/execute", json={
        "capture_id": "CAPTURE-TEST-99",
        "authorization_token": "not-a-valid-token",
        "amount": "15.00",
        "currency": "USD",
        "idempotency_key": "idemp-001"
    })
    assert unauth_resp.status_code == 403
    assert "Missing, expired, or invalid authorization token" in unauth_resp.json()["detail"]

    # 2. Step 1: Explicitly request authorization
    auth_resp = client.post("/api/paypal/authorize-step", json={
        "operation": "REFUND",
        "target_id": "CAPTURE-TEST-99",
        "amount": "15.00",
        "currency": "USD",
        "reason": "Damaged goods return authorized per merchant policy",
        "reviewer_id": "owner_1"
    })
    assert auth_resp.status_code == 200
    auth_data = auth_resp.json()
    assert auth_data["status"] == "AUTHORIZED"
    auth_token = auth_data["authorization_token"]
    assert auth_token is not None
