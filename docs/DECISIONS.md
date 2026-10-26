# Decisions
| # | Decision | Choice | Reason | Status |
|---|---|---|---|---|
| 1 | Frontend | (e.g. Next.js + TypeScript) | | pending |
| 2 | Backend | FastAPI (Python) | High performance, async REST client, robust typing with Pydantic, and clean integration with AI/decision ecosystem | decided |
| 3 | Database | (Postgres or SQLite first) | | pending |
| 4 | Auth | (library or managed service) | | pending |
| 5 | Job queue | | | pending |
| 6 | File storage | | | pending |
| 7 | Email | | | pending |
| 8 | LLM used inside the app for classification, vision and drafting | (not yet chosen) | | pending |
| 9 | Hosting | | | pending |

Decision 8 is separate from the tools used to build the project (ChatGPT, Antigravity). The finished app needs its own LLM. Choose it before Phase 6.

---
## Stack suggestions from the plan (Merged Plan section 11)
These are suggestions; choose what your team can ship fastest. The principle is to **reuse proven components for auth, storage and email** and spend your effort on the agent and PayPal logic.

| **Layer**       | **Suggestion**                                                                | **Why / note**                                                                                                     |
|-----------------|-------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|
| Frontend        | Next.js (React, TypeScript) with Tailwind and a component library             | One codebase for landing, auth, merchant portal and customer portal                                                |
| Backend         | FastAPI (Python) or Next.js API routes with TypeScript                        | FastAPI if the team prefers Python for the AI and policy code; one TypeScript stack if you want fewer moving parts |
| Database        | PostgreSQL (or SQLite for the first days)                                     | Relational data with audit requirements                                                                            |
| Auth            | A vetted auth library or managed auth service                                 | Do not hand-roll password storage or sessions                                                                      |
| Background jobs | A simple queue or worker (for example Celery, BullMQ, or a DB-polling worker) | Webhook processing and LLM calls should not block requests                                                         |
| File storage    | S3-compatible object storage or the database provider’s storage               | Photos and evidence documents                                                                                      |
| Email           | A transactional email service; log-to-console in development                  | Verification, magic links, notifications                                                                           |
| LLM             | Claude API with structured output and vision                                  | Classification, claim extraction, photo analysis, message drafting, policy compilation                             |
| PayPal          | REST APIs (Orders/Payments for refunds, Disputes, Webhooks) in sandbox        | Direct REST gives control; PayPal MCP is optional for prototyping                                                  |
| Webhook testing | A tunnelling tool plus PayPal’s webhook simulator                             | PayPal must reach a public HTTPS URL                                                                               |
| Hosting         | Any platform with HTTPS and environment secrets                               | Needed for webhooks in the final demo                                                                              |
