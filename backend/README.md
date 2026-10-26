# ResolveAI Backend — PayPal Sandbox Integration

FastAPI backend service implementing policy-governed post-purchase resolution and PayPal Sandbox REST integration.

## Architecture & Security Principles

1. **Zero Credential Exposure:**
   - Client ID and Client Secret are read exclusively from environment variables (`.env`).
   - Secrets are encapsulated in `SecretStr` models to prevent exposure in logs, stack traces, or exception dumps.
   - API endpoints never return access tokens or client secrets.
   - `.env` is strictly excluded by `.gitignore`.

2. **Backend OAuth 2.0 Token Flow:**
   - Implements automated client credentials grant flow against `https://api-m.sandbox.paypal.com/v1/oauth2/token`.
   - In-memory asynchronous token caching with pre-expiry automatic refresh.

3. **Mandatory Multi-Stage Authorization for Payment Actions:**
   - The LLM or autonomous scripts can **never** execute money-movement actions directly.
   - Any payment-altering operation (e.g. refund) requires an explicit, separate authorization step:
     - **Step 1 (`POST /api/paypal/authorize-step`):** Evaluates business rules / reviewer approval and issues a single-use, time-limited cryptographic authorization token.
     - **Step 2 (`POST /api/paypal/refunds/execute`):** Validates the token against target ID, operation type, and amount, guarantees single-use consumption, and enforces idempotency with `PayPal-Request-Id`.

## Setup & Running

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and fill in your PayPal Sandbox credentials:
```bash
cp .env.example .env
```

Ensure the following variables are defined in `.env`:
```env
PAYPAL_ENV=sandbox
PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com
PAYPAL_CLIENT_ID=your_paypal_sandbox_client_id_here
PAYPAL_CLIENT_SECRET=your_paypal_sandbox_client_secret_here
APP_URL=http://localhost:8000
```

### 3. Run the Backend Server
```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```
Interactive API docs are available at `http://localhost:8000/docs`.

### 4. Run Test Suite
```bash
python -m pytest backend/tests/
```
