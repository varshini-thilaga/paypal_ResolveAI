# ResolveAI
Policy-governed post-purchase resolution agent for PayPal merchants.
LLM reasons, rules decide, humans approve high-risk cases.

## Where to look
- Start here (prompts and workflow): START-HERE.md
- Task list in run order (solo): docs/TASKS.md
- Rules for agents: .agent/rules/resolveai.md
- Spec: docs/01 to docs/09
- PayPal verified behaviour: docs/PayPal-Findings.md
- Decisions log: docs/DECISIONS.md
- Original Word files and full Markdown copies: docs/source/

## Run locally
```bash
# 1. Install dependencies
pip install -r backend/requirements.txt

# 2. Configure .env with your PayPal sandbox credentials (see .env.example)

# 3. Run FastAPI backend server
python -m uvicorn backend.app.main:app --reload --port 8000

# 4. Run test suite
python -m pytest backend/tests/
```
