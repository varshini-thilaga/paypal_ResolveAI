> Source: Merged Plan, section 12. Section numbers mentioned in the text refer to `docs/source/ResolveAI_Merged_Plan.md`.

# 12. Phase-by-phase implementation plan

Phases are ordered so that you **have a working demo as early as possible** and add polish afterwards. Each phase lists the pages it delivers, the tasks, and a “done when” check. Timings assume a team of about four people and are indicative; section 13 shows how to compress them.

## Phase 0 — Foundations and verification

**Suggested timing:** Day 1 \| **Priority:** Must

**Goal**

Remove every PayPal unknown and set up the project so nothing later is blocked.

**PayPal sandbox work (do by hand first, using Postman or curl)**

- Create a PayPal developer account, one sandbox **business** (merchant) account, one sandbox **personal** (buyer) account and a REST app. Pick a country with full REST support. Store the client ID and secret in environment variables.

- Get an access token; create and capture an order as the buyer; note the order ID and capture ID.

- Issue a full refund and a partial refund; repeat a refund with the same request ID and record what happens.

- Add tracking information to a transaction.

- Open an item-not-received dispute from the buyer account in Resolution Center; GET it and record the status, stage, requested evidence and the links that appear.

- Try provide-evidence and make-offer at the correct stage; try them at the wrong stage and record the errors.

- Try creating a dispute via API; if the scope is missing, note it and use the buyer UI instead.

- Expose a stub webhook endpoint through a tunnel, subscribe to dispute events, fire the simulator, and implement signature verification.

- Re-check the current PayPal Agent Toolkit tool list.

**Project setup**

- Create the repository, folder structure, linting, formatting and an .env.example; add secrets to .gitignore.

- Pick the stack (section 11), assign roles and create a task board with one card per phase task.

- Write PayPal-Findings.md with exact payloads, stage-to-action mapping, evidence types, file limits and any surprises.

**Done when**

- You have personally seen refund, tracking and dispute-open work in the sandbox, and evidence submission either work or be documented as blocked with a fallback.

- PayPal-Findings.md exists and every row of section 5 is marked confirmed or changed.

## Phase 1 — Design system and public website (landing)

**Suggested timing:** Days 1–2 (parallel with Phase 0) \| **Priority:** Should (a minimal landing page is Must)

**Goal**

Give the product a credible public face and a reusable UI kit for every later screen.

**Design system**

- Colour palette, typography scale, spacing, buttons, inputs, cards, badges (status colours), tables, modals, toasts, empty states, skeleton loaders.

- Four layout shells: **public**, **auth**, **merchant app** (sidebar + top bar), **customer portal** (minimal, mobile-first).

- Responsive behaviour and basic accessibility (labels, focus states, contrast, keyboard navigation).

**Landing page ( / ) sections**

- **Hero:** one-line promise (resolve complaints before they become PayPal disputes) with two buttons: “Try the demo” and “Get started”.

- **Problem strip:** evidence scattered across PayPal, carrier, inbox and policy.

- **How it works:** understand → decide within your rules → act with approval.

- **Three scenario cards:** lost package auto-refund, damaged item needing approval, dispute evidence submission, each with a short animated or static case timeline.

- **Trust section:** rules decide, humans approve high-risk cases, full audit trail, sandbox-first.

- **Who it is for:** small PayPal merchants. **FAQ.** **Footer** with legal links.

**Other public pages**

- /how-it-works, /security (explain the guardrails in section 8 in plain language), /demo (entry to the pre-seeded merchant), /privacy and /terms placeholders, 404 and error pages.

- Do not invent pricing or customer logos. If you need a pricing area, label it “Free during beta” or leave it out.

**Done when**

- The landing page and supporting pages render well on phone and desktop.

- The UI kit is used by at least one page in each of the four shells.

## Phase 2 — Authentication and accounts

**Suggested timing:** Days 2–3 \| **Priority:** Must

**Goal**

Let merchants sign up and sign in securely, with roles and tenant isolation in place from the start.

**Pages**

- **/signup:** name, email, password, business name; creates a user, a merchant and an owner membership.

- **/login**, **/logout**, **/verify-email**, **/forgot-password**, **/reset-password**, **/accept-invite**.

**Tasks**

- Use a vetted auth library or managed service. Hash passwords with a standard algorithm; never store plain text.

- Email verification and password reset with expiring single-use tokens.

- Secure session cookies (http-only, secure, same-site), CSRF protection on state-changing requests, and rate limiting on login and signup.

- Route guards: unauthenticated users are redirected from /app/\* to /login.

- Roles (owner, reviewer, viewer) enforced **server-side** on every endpoint, not only hidden in the UI.

- Tenant isolation: every query filtered by the signed-in user’s merchant ID; add a test that user A cannot read merchant B’s case.

- Seed accounts: a demo owner, a demo reviewer and a platform admin.

**Done when**

- A new user can sign up, verify, log in and reach onboarding.

- A reviewer cannot open /app/policies for editing; a user from merchant A cannot read merchant B’s data.

## Phase 3 — Merchant onboarding and integrations

**Suggested timing:** Day 3 \| **Priority:** Should

**Goal**

Guide a new merchant from an empty account to a connected, safe starting configuration.

**Onboarding wizard ( /app/onboarding )**

- **Step 1 Business profile:** name, support email, currency, timezone, store URL.

- **Step 2 Connect PayPal:** for the hackathon, use server-held sandbox credentials for each demo merchant (or a form to paste sandbox credentials, stored encrypted). Show a connection-status check. Describe PayPal’s partner / third-party permission onboarding as the production path, after confirming its requirements.

- **Step 3 Store data:** use the seeded mock store; optionally add CSV order import.

- **Step 4 Carrier tracking:** mock carrier by default; an aggregator is optional.

- **Step 5 Policy:** choose a starter template (details come in Phase 11).

- **Step 6 Mode:** Shadow (recommend only), Approval for everything, or Auto within rules. Default to Shadow or Approval.

- **Step 7 Webhook health:** show whether PayPal events are arriving.

**Integrations page ( /app/integrations )**

- Status, last-checked time and a “test connection” button for PayPal, carrier, store and webhooks.

**Done when**

- A new merchant can finish the wizard and see all integrations green in the sandbox.

- Credentials are encrypted at rest and never returned to the browser.

## Phase 4 — Core domain, data and connectors

**Suggested timing:** Days 2–4 \| **Priority:** Must

**Goal**

Build the data layer and the read-only connectors so a case can produce a correct Evidence Pack.

**Tasks**

- Create migrations for the tables in section 9 and a seed script.

- **Store DB:** orders, items, fulfilments and invoices, with realistic seeded scenarios: delivered, in transit, lost, damaged, repeat refunder.

- **Mock carrier service:** an endpoint that returns scripted tracking status and sub-status, plus a control to change status and emit a webhook. Implement the “no scan for N days” stalled-shipment logic.

- **PayPal read connector:** order, capture and dispute lookups. Store capture IDs at checkout rather than depending on later searches.

- **Evidence Pack builder:** normalised JSON that combines the order, payment, tracking, history, messages and attachments with a source reference on every item.

- **Case state machine** with an audit-event writer on every transition.

**Done when**

- For each of five seeded scenarios, the Evidence Pack prints correctly and every item shows its source.

- State transitions are logged.

## Phase 5 — Customer portal and intake

**Suggested timing:** Days 3–4 \| **Priority:** Must

**Goal**

Give customers a simple way to raise a problem and follow it, with no account needed.

**Pages**

- **/c/\[merchant\]/report:** order number + email check; problem type quick-select; free-text description; photo upload; desired outcome (refund, replacement, other).

- **/case/\[token\]:** magic-link status page with a timeline, messages from the merchant, and a place to upload more evidence or answer questions.

**Tasks**

- Verify that the order number and email match before creating the case; otherwise show a neutral error.

- Generate a random magic token; store only its hash.

- Validate uploads (type, size), strip image metadata and store outside the web root.

- Send emails: received, needs more information, resolved, escalated.

- Rate-limit the form. Treat all customer text as untrusted data everywhere.

- Stretch: email forwarding ingest and an embeddable chat widget.

**Done when**

- A customer can submit a complaint with a photo, a case is created and linked to the order, and a confirmation email with a magic link is sent.

## Phase 6 — Reasoning layer, policy engine, risk score and cost advisor

**Suggested timing:** Days 3–5 \| **Priority:** Must

**Goal**

Turn an Evidence Pack into a safe, explainable decision.

**Tasks**

- **Classifier prompt and schema:** case type, claims, desired outcome, language and urgency. Customer text goes in a clearly delimited data field. Validate output against the schema and fall back to approval if invalid.

- **Policy engine:** implement the JSON rule schema from section 7.1 as a pure function with global caps and a default of REQUIRE_APPROVAL. Unit-test every rule path.

- **Risk scorer:** implement the signals in section 7.2 with a visible per-signal breakdown.

- **Cost advisor:** implement the three-path comparison in section 7.3 with merchant-editable fee settings.

- **Decision record:** persist proposed action, gate, rule fired, policy version, score breakdown, cost comparison and evidence references.

- Run the classifier several times on borderline cases and use disagreement as a score signal.

**Done when**

- Twenty seeded cases produce the expected gate and rule trace.

- Unit tests pass, including “unknown data → approval” and “over cap → blocked”.

## Phase 7 — Merchant portal: shell and screens

**Suggested timing:** Days 4–6 \| **Priority:** Must (minimum: Home, Cases, Case detail, Approvals)

**Goal**

Give merchants one place to see, understand and act on every case.

**App shell**

- Sidebar (Home, Cases, Approvals, Disputes, Policies, Analytics, Audit, Integrations, Team, Settings), top bar with merchant name, mode badge, kill-switch indicator and user menu. Hide or disable items by role.

**Screens**

- **Home ( /app ):** KPIs (open cases, awaiting approval, auto-resolved, refunds today, disputes due soon with countdown, estimated hours saved), approval queue preview and recent activity.

- **Cases ( /app/cases ):** table with filters (status, type, source, amount), search and sort by urgency or deadline.

- **Case detail ( /app/cases/\[id\] ):** header (status, order, amount); customer message and photos; evidence cards with sources; recommended action; rule trace; score breakdown; cost comparison; message-draft editor; Approve / Edit / Reject buttons; timeline and audit entries.

- **Approvals ( /app/approvals ):** queue sorted by deadline and risk.

- **Disputes ( /app/disputes ):** PayPal cases with stage, due date and an evidence checklist (have / missing).

- **Audit ( /app/audit ):** searchable log with export.

- **Team ( /app/team )** and **Settings ( /app/settings ):** invites, roles, caps, mode and kill switch.

**Notes**

- Build screens against the real API and seeded data, not hard-coded mock data, so they keep working as backend phases land.

- Add loading, empty and error states to every screen.

**Done when**

- A reviewer can open any seeded case and understand, from one screen, what happened, why the agent recommends an action and what each button will do.

## Phase 8 — Action executor and the refund path (Demo case 1)

**Suggested timing:** Days 4–5 \| **Priority:** Must

**Goal**

Execute the first real PayPal action safely: the automatic refund for a lost package.

**Tasks**

- Build the **executor** as the only module that holds write credentials.

- Actions: refund (full or partial), send message, add tracking. Idempotency key derived from case and action; send PayPal’s request-ID header.

- Pre-checks: amount does not exceed the remaining captured amount, currency matches, caps not exceeded, kill switch off, dry-run honoured, stage allowed.

- Retries reuse the same request ID; a timeout never causes a second refund.

- Wire AUTO_EXECUTE decisions to the executor; then send the customer email; then close the case.

- Show the refund ID and outcome on the case detail screen and in the audit log.

- Tests: double-click, retry after a lost response, over-refund attempt, kill switch on.

**Done when**

- End to end in the sandbox: complaint “package never arrived” → evidence → rule fires → refund executes → customer emailed → audit trail shows facts, rule, score and refund ID.

## Phase 9 — Approval flow and the damaged-item case (Demo case 2)

**Suggested timing:** Day 5 \| **Priority:** Must

**Goal**

Show the human-in-the-loop path with photo evidence and a lower-confidence decision.

**Tasks**

- **Vision analysis:** send the uploaded photo to the vision model and extract: visible damage, consistency with the ordered item, image quality. Feed these into the score as signals, never as the sole basis.

- **Approval actions:** approve as recommended; edit amount; change resolution (refund, partial refund, replacement, return-then-refund); reject with a required reason.

- Store every edit and rejection reason in approvals for later learning.

- Draft the customer message from approved facts only; let the reviewer edit it.

- Reviewer notifications by email and in-app badge.

**Done when**

- The damaged-item case pauses at “human approval required”, the breakdown shows why confidence is lower, the reviewer approves, and the executor completes the action.

## Phase 10 — Dispute pipeline (Demo case 3)

**Suggested timing:** Days 5–6 \| **Priority:** Must (core of the second flow)

**Goal**

Handle a PayPal dispute from webhook to evidence submission, respecting stage rules.

**Tasks**

- **Webhook endpoint:** verify the signature, de-duplicate by event ID, store the raw event, then queue processing.

- **On dispute created:** fetch the dispute, link it to the order and create or update the case; record stage, status, reason, due date and the links the response offers.

- **Evidence mapper:** read the requested evidence, map each item to evidence you hold (for example carrier and tracking number, fulfilment proof, transaction ID, notes), and show a have / missing checklist.

- **Stage-aware actions:** make_offer only in the inquiry stage; provide_evidence only when PayPal is waiting for the seller and the link is present; accept_claim human-only; send_message allowed where PayPal permits.

- **Recommendation:** use the cost advisor to recommend defend, offer or accept, with the numbers shown.

- **Submission:** by default require approval; allow auto-submit only if the merchant policy says so.

- **Monitoring:** handle update and resolved events, refresh the case and notify the merchant; send deadline reminders.

- If API-created disputes are unavailable, create them from the buyer account and use real events from the sandbox plus the simulator.

**Done when**

- A sandbox dispute produces a case with a correct checklist; the reviewer approves; the evidence is submitted through the Disputes API; the case updates when PayPal sends the next event.

## Phase 11 — Policy builder, shadow mode, analytics and learning

**Suggested timing:** Days 6–7 \| **Priority:** Should

**Goal**

Make the product usable by non-technical merchants and let them build trust before automating.

**Policy builder ( /app/policies )**

- Starter templates and a plain-English text box.

- LLM compiles the text to the JSON rule schema; show the result as readable rule cards plus the JSON, and flag anything ambiguous.

- **Backtest:** run the draft policy against past or seeded cases and show how many would auto-execute, need approval or be blocked.

- Publish creates a new version; allow rollback.

**Shadow mode**

- The agent records what it would have done and compares it with what the merchant actually did. Show agreement rate and estimated time saved.

**Analytics ( /app/analytics )**

- Auto-resolution rate, escalation rate, refunds by reason, disputes handled, override rate, and estimated hours saved (state the assumption used).

**Override learning (stretch)**

- Summarise repeated rejections and suggest a policy change. It is a suggestion only; never change a policy automatically.

**Done when**

- A merchant can type a refund rule in plain English, see it compiled, backtest it and publish it; shadow mode shows an agreement metric.

## Phase 12 — Security, evaluation and hardening

**Suggested timing:** Days 6–7 \| **Priority:** Must (this builds judge trust)

**Goal**

Prove the system is safe and measure how well it works.

**Tasks**

- Build a labelled set of **40–60 synthetic cases** covering every case type, edge cases and abuse cases.

- Write an evaluation script that reports the metrics in section 14.

- Run the adversarial suite: injection in message text, in filenames and in image text; forged tracking numbers; order/email mismatch; serial refunder; amount manipulation; replayed webhook; double submit.

- Security pass: secrets handling, role checks on every endpoint, tenant-isolation tests, rate limits, upload validation, CORS, dependency audit and no personal data in logs.

- Reliability: timeouts and retries for LLM and PayPal calls, a dead-letter list for failed jobs, and a guaranteed fail-safe to approval.

**Done when**

- You can quote classification accuracy, escalation rate and the false auto-refund rate from a repeatable run.

- All adversarial cases are held by the policy engine or executor.

## Phase 13 — Demo mode, deployment and rehearsal

**Suggested timing:** Final 1–2 days \| **Priority:** Must

**Goal**

Make the demo repeatable and robust.

**Tasks**

- **Simulator ( /admin/simulator ):** seed scenarios, change carrier status, replay a webhook, reset to a clean state with one click. **/demo** logs into the seeded merchant.

- Deploy to a host with HTTPS so PayPal webhooks reach you; set environment secrets; confirm sandbox mode is visibly labelled in the UI.

- Record a **fallback video** of a full successful run in case Wi-Fi or the sandbox misbehaves.

- Write the demo script (section 15), prepare slides and a one-page architecture diagram, and rehearse at least three times with a timer.

- Prepare answers on trust and safety, what is real versus simulated, and the production path (PayPal partner onboarding, real carrier data).

**Done when**

- Three clean timed rehearsals; reset takes under a minute; fallback video exists.
