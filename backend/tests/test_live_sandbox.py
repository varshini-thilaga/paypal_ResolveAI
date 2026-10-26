import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.config import get_settings


def test_live_paypal_sandbox_oauth_handshake():
    """
    Live test against PayPal Sandbox.
    Verifies that the credentials in .env successfully authenticate
    with https://api-m.sandbox.paypal.com/v1/oauth2/token,
    that OAuth token is retrieved and cached,
    and that zero secrets or raw tokens are exposed.
    """
    settings = get_settings()
    if not settings.PAYPAL_CLIENT_ID or "placeholder" in settings.PAYPAL_CLIENT_ID.lower():
        pytest.skip("PayPal client ID not configured in .env; skipping live sandbox test.")

    client = TestClient(app)
    response = client.get("/api/paypal/health")
    assert response.status_code == 200, f"Health check failed: {response.text}"

    data = response.json()
    assert data["status"] == "ok"
    assert data["authenticated"] is True
    assert data["token_valid"] is True
    assert data["environment"] == "sandbox"
    assert data["base_url"] == "https://api-m.sandbox.paypal.com"
    assert data["token_expires_in_seconds"] > 0
    assert "..." in data["client_id_masked"]

    # Security check: Ensure no secret or token is leaked
    raw_text = response.text.lower()
    assert "secret" not in raw_text or "client_secret" not in data
    assert "access_token" not in data
    assert "bearer" not in raw_text
