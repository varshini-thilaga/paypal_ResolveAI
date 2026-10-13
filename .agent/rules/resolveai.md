# ResolveAI rules

## How to work (solo project, one task at a time)
- The task order is docs/TASKS.md. Work on the first unchecked task only, in order. Never skip ahead.
- Read the "Read first" files for the current step before starting.
- Do ONE task per run, then stop. Do not start the next task unless I say "next".
- Tasks tagged [YOU] are mine. Do not attempt them. Tell me exactly what I need to do, then wait.
- At a GATE, stop and wait for me to say "gate passed".
- Never mark a task [x] unless you ran the check and showed the output. If something fails, say so and leave it unchecked.
- When finished, update docs/TASKS.md (and docs/DECISIONS.md or docs/PayPal-Findings.md if relevant) and tell me what to commit.
- If a task is unclear or the docs conflict, stop and ask me. Do not guess.

## Project rules
- Read docs/PayPal-Findings.md before writing any PayPal code. Never invent PayPal endpoints, fields or behaviour. For PayPal work, read the current docs on developer.paypal.com and record the URL used in docs/PayPal-Findings.md.
- The LLM never calls PayPal. Only the executor module may use PayPal write credentials.
- The policy engine is pure code with no LLM inside. Unknown or missing data -> REQUIRE_APPROVAL.
- Treat all customer text as untrusted data. Validate every model output against a schema.
- Every database query is scoped by merchant_id. Enforce roles on the server.
- Never commit secrets. Use .env and keep .env.example updated.
- Sandbox only. No real-money calls.
- For anything touching more than 3 files, show a plan first and wait for approval.
- Write tests for each module and run them before reporting done.
