# Tasks (solo run order)
One person plus Antigravity. This order replaces the team schedule in `docs/08-roadmap.md`: the demo-critical path comes first and the public website, onboarding and polish come last.

Tags: **[AGENT]** Antigravity does it. **[YOU]** only you can do it (accounts, keys, decisions, manual PayPal steps, recording). **[YOU+AGENT]** shared; the task text says who does what.
Status key: [ ] todo, [~] in progress, [x] done. Task IDs match the phase numbers in `docs/07-phases.md`.
Rule: do tasks strictly in this order, one at a time. At each GATE, stop and wait for me.

## Run order
| Step | Group | Gate after |
|---|---|---|
| 1 | Phase 0 — Foundations and verification | M0 PayPal verified |
| 2 | Phase 1a — Design system (public website comes later) | - |
| 3 | Phase 2 — Authentication and accounts | M1 Skeleton (auth working; landing page deferred) |
| 4 | Phase 4 — Core domain, data and connectors | - |
| 5 | Phase 5 — Customer portal and intake | M2 A case exists |
| 6 | Phase 6 — Reasoning layer, policy engine, risk score, cost advisor | M3 The agent decides |
| 7 | Phase 7a — Merchant portal: minimum screens | - |
| 8 | Phase 8 — Action executor and the refund path (Demo case 1) | M4 First real action (Case 1) |
| 9 | Phase 9 — Approval flow and the damaged-item case (Demo case 2) | M5 Human in the loop (Case 2) |
| 10 | Phase 10 — Dispute pipeline (Demo case 3), including the Disputes screen | M6 Disputes (Case 3) |
| 11 | Phase 7b — Merchant portal: Audit, Team, Settings | - |
| 12 | Phase 12 — Security, evaluation and hardening | - |
| 13 | Phase 11 — Policy builder, shadow mode, analytics and learning | M7 Trust layer |
| 14 | Phase 3 — Merchant onboarding and integrations | - |
| 15 | Phase 1b — Landing page and public pages | - |
| 16 | Phase 13 — Demo mode, deployment and rehearsal | M8 Demo-ready |

---
## Step 1: Phase 0 — Foundations and verification
**Goal:** Remove every PayPal unknown and set up the project so nothing later is blocked.

**Read first:** docs/07-phases.md (Phase 0), `docs/PayPal-Findings.md`, `docs/DECISIONS.md`

- [x] **P0.1** [YOU] Create a PayPal developer account, one sandbox **business** account, one sandbox **buyer** account and a REST app (pick a country with full REST support). Put the sandbox client ID and secret in `.env` (never paste them into chat or commit them).
- [ ] **P0.2** [YOU+AGENT] Stack decision: the agent proposes options with trade-offs for each row of `docs/DECISIONS.md`; you choose; the agent records the choices.
- [ ] **P0.3** [AGENT] Scaffold the repository to match `docs/02-architecture.md`: folders, lint/format, env loading from `.env`, run instructions in `README.md`. Commit.
- [ ] **P0.4** [AGENT] Read the current PayPal docs on developer.paypal.com. Write small runnable scripts in `scripts/paypal-sandbox/` for: access token; create order (print the buyer approval link); capture; full refund; partial refund; repeat a refund with the same request ID; add tracking. Record the doc URL used for each endpoint in `docs/PayPal-Findings.md`.
- [ ] **P0.5** [YOU] Approve the created order as the sandbox buyer, then let the agent run the capture, refund and tracking scripts. Check the results make sense.
- [ ] **P0.6** [YOU] Open an item-not-received dispute from the sandbox buyer account in Resolution Center.
- [ ] **P0.7** [AGENT] Script: GET the dispute and record status, stage, requested evidence and the links offered. Try provide-evidence and make-offer at the right and the wrong stage and record the exact errors.
- [ ] **P0.8** [AGENT] Try creating a dispute through the API. If blocked, record the error and the fallback (buyer UI).
- [ ] **P0.9** [YOU+AGENT] Webhook: you start a public tunnel; the agent builds a stub endpoint, subscribes to dispute events, implements signature verification and tests it with the PayPal simulator.
- [ ] **P0.10** [AGENT] Re-check the current PayPal Agent Toolkit tool list from its official docs and record it.
- [ ] **P0.11** [AGENT] Fill every row of `docs/PayPal-Findings.md` with confirmed behaviour and exact payloads. Mark each section 5 belief as confirmed or changed.

**Acceptance (all must be shown to pass):**
- [ ] You have personally seen refund, tracking and dispute-open work in the sandbox, and evidence submission either work or be documented as blocked with a fallback.
- [ ] PayPal-Findings.md exists and every row of section 5 is marked confirmed or changed.

**GATE M0 PayPal verified:** stop. Summarise what works, show evidence (test output, screenshots, IDs), list anything not done, and wait for me to say "gate passed".

---
## Step 2: Phase 1a — Design system (public website comes later)
**Goal:** Reusable UI kit and layouts for every later screen.

**Read first:** docs/07-phases.md (Phase 1), `docs/06-app-map.md`

- [ ] **P1.1** [AGENT] Colour palette, typography scale, spacing, buttons, inputs, cards, badges (status colours), tables, modals, toasts, empty states, skeleton loaders.
- [ ] **P1.2** [AGENT] Four layout shells: **public**, **auth**, **merchant app** (sidebar + top bar), **customer portal** (minimal, mobile-first).
- [ ] **P1.3** [AGENT] Responsive behaviour and basic accessibility (labels, focus states, contrast, keyboard navigation).

---
## Step 3: Phase 2 — Authentication and accounts
**Goal:** Let merchants sign up and sign in securely, with roles and tenant isolation in place from the start.

**Read first:** `docs/06-app-map.md`, `docs/04-security.md`, `docs/05-data-model.md`

- [ ] **P2.1** [AGENT] **/signup:** name, email, password, business name; creates a user, a merchant and an owner membership.
- [ ] **P2.2** [AGENT] **/login**, **/logout**, **/verify-email**, **/forgot-password**, **/reset-password**, **/accept-invite**.
- [ ] **P2.3** [AGENT] Use a vetted auth library or managed service. Hash passwords with a standard algorithm; never store plain text.
- [ ] **P2.4** [AGENT] Email verification and password reset with expiring single-use tokens.
- [ ] **P2.5** [AGENT] Secure session cookies (http-only, secure, same-site), CSRF protection on state-changing requests, and rate limiting on login and signup.
- [ ] **P2.6** [AGENT] Route guards: unauthenticated users are redirected from /app/\* to /login.
- [ ] **P2.7** [AGENT] Roles (owner, reviewer, viewer) enforced **server-side** on every endpoint, not only hidden in the UI.
- [ ] **P2.8** [AGENT] Tenant isolation: every query filtered by the signed-in user’s merchant ID; add a test that user A cannot read merchant B’s case.
- [ ] **P2.9** [AGENT] Seed accounts: a demo owner, a demo reviewer and a platform admin.

**Acceptance (all must be shown to pass):**
- [ ] A new user can sign up, verify, log in and reach onboarding.
- [ ] A reviewer cannot open /app/policies for editing; a user from merchant A cannot read merchant B’s data.

**GATE M1 Skeleton (auth working; landing page deferred):** stop. Summarise what works, show evidence (test output, screenshots, IDs), list anything not done, and wait for me to say "gate passed".

---
## Step 4: Phase 4 — Core domain, data and connectors
**Goal:** Build the data layer and the read-only connectors so a case can produce a correct Evidence Pack.

**Read first:** `docs/05-data-model.md`, `docs/02-architecture.md`, `docs/PayPal-Findings.md`

- [ ] **P4.1** [AGENT] Create migrations for the tables in section 9 and a seed script.
- [ ] **P4.2** [AGENT] **Store DB:** orders, items, fulfilments and invoices, with realistic seeded scenarios: delivered, in transit, lost, damaged, repeat refunder.
- [ ] **P4.3** [AGENT] **Mock carrier service:** an endpoint that returns scripted tracking status and sub-status, plus a control to change status and emit a webhook. Implement the “no scan for N days” stalled-shipment logic.
- [ ] **P4.4** [AGENT] **PayPal read connector:** order, capture and dispute lookups. Store capture IDs at checkout rather than depending on later searches.
- [ ] **P4.5** [AGENT] **Evidence Pack builder:** normalised JSON that combines the order, payment, tracking, history, messages and attachments with a source reference on every item.
- [ ] **P4.6** [AGENT] **Case state machine** with an audit-event writer on every transition.

**Acceptance (all must be shown to pass):**
- [ ] For each of five seeded scenarios, the Evidence Pack prints correctly and every item shows its source.
- [ ] State transitions are logged.

---
## Step 5: Phase 5 — Customer portal and intake
**Goal:** Give customers a simple way to raise a problem and follow it, with no account needed.

**Read first:** `docs/06-app-map.md`, `docs/04-security.md`

- [ ] **P5.1** [AGENT] **/c/\[merchant\]/report:** order number + email check; problem type quick-select; free-text description; photo upload; desired outcome (refund, replacement, other).
- [ ] **P5.2** [AGENT] **/case/\[token\]:** magic-link status page with a timeline, messages from the merchant, and a place to upload more evidence or answer questions.
- [ ] **P5.3** [AGENT] Verify that the order number and email match before creating the case; otherwise show a neutral error.
- [ ] **P5.4** [AGENT] Generate a random magic token; store only its hash.
- [ ] **P5.5** [AGENT] Validate uploads (type, size), strip image metadata and store outside the web root.
- [ ] **P5.6** [AGENT] Send emails: received, needs more information, resolved, escalated.
- [ ] **P5.7** [AGENT] Rate-limit the form. Treat all customer text as untrusted data everywhere.
- [ ] **P5.8** [AGENT] Stretch: email forwarding ingest and an embeddable chat widget.

**Acceptance (all must be shown to pass):**
- [ ] A customer can submit a complaint with a photo, a case is created and linked to the order, and a confirmation email with a magic link is sent.

**GATE M2 A case exists:** stop. Summarise what works, show evidence (test output, screenshots, IDs), list anything not done, and wait for me to say "gate passed".

---
## Step 6: Phase 6 — Reasoning layer, policy engine, risk score, cost advisor
**Goal:** Turn an Evidence Pack into a safe, explainable decision.

**Read first:** `docs/03-decision-logic.md`, `docs/04-security.md`

- [ ] **P6.0** [YOU] Choose the LLM the app itself will use for classification, vision and drafting. Create the API key, put it in `.env` as `LLM_API_KEY`, and record the choice in `docs/DECISIONS.md` (row 8).
- [ ] **P6.1** [AGENT] **Classifier prompt and schema:** case type, claims, desired outcome, language and urgency. Customer text goes in a clearly delimited data field. Validate output against the schema and fall back to approval if invalid.
- [ ] **P6.2** [AGENT] **Policy engine:** implement the JSON rule schema from section 7.1 as a pure function with global caps and a default of REQUIRE_APPROVAL. Unit-test every rule path.
- [ ] **P6.3** [AGENT] **Risk scorer:** implement the signals in section 7.2 with a visible per-signal breakdown.
- [ ] **P6.4** [AGENT] **Cost advisor:** implement the three-path comparison in section 7.3 with merchant-editable fee settings.
- [ ] **P6.5** [AGENT] **Decision record:** persist proposed action, gate, rule fired, policy version, score breakdown, cost comparison and evidence references.
- [ ] **P6.6** [AGENT] Run the classifier several times on borderline cases and use disagreement as a score signal.

**Acceptance (all must be shown to pass):**
- [ ] Twenty seeded cases produce the expected gate and rule trace.
- [ ] Unit tests pass, including “unknown data → approval” and “over cap → blocked”.

**GATE M3 The agent decides:** stop. Summarise what works, show evidence (test output, screenshots, IDs), list anything not done, and wait for me to say "gate passed".

---
## Step 7: Phase 7a — Merchant portal: minimum screens
**Goal:** Give merchants one place to see, understand and act on every case.

**Read first:** `docs/06-app-map.md`

- [ ] **P7.1** [AGENT] Sidebar (Home, Cases, Approvals, Disputes, Policies, Analytics, Audit, Integrations, Team, Settings), top bar with merchant name, mode badge, kill-switch indicator and user menu. Hide or disable items by role.
- [ ] **P7.2** [AGENT] **Home ( /app ):** KPIs (open cases, awaiting approval, auto-resolved, refunds today, disputes due soon with countdown, estimated hours saved), approval queue preview and recent activity.
- [ ] **P7.3** [AGENT] **Cases ( /app/cases ):** table with filters (status, type, source, amount), search and sort by urgency or deadline.
- [ ] **P7.4** [AGENT] **Case detail ( /app/cases/\[id\] ):** header (status, order, amount); customer message and photos; evidence cards with sources; recommended action; rule trace; score breakdown; cost comparison; message-draft editor; Approve / Edit / Reject buttons; timeline and audit entries.
- [ ] **P7.5** [AGENT] **Approvals ( /app/approvals ):** queue sorted by deadline and risk.
- [ ] **P7.9** [AGENT] Build screens against the real API and seeded data, not hard-coded mock data, so they keep working as backend phases land.
- [ ] **P7.10** [AGENT] Add loading, empty and error states to every screen.

**Acceptance (all must be shown to pass):**
- [ ] A reviewer can open any seeded case and understand, from one screen, what happened, why the agent recommends an action and what each button will do.

---
## Step 8: Phase 8 — Action executor and the refund path (Demo case 1)
**Goal:** Execute the first real PayPal action safely: the automatic refund for a lost package.

**Read first:** `docs/02-architecture.md`, `docs/04-security.md`, `docs/PayPal-Findings.md`

- [ ] **P8.1** [AGENT] Build the **executor** as the only module that holds write credentials.
- [ ] **P8.2** [AGENT] Actions: refund (full or partial), send message, add tracking. Idempotency key derived from case and action; send PayPal’s request-ID header.
- [ ] **P8.3** [AGENT] Pre-checks: amount does not exceed the remaining captured amount, currency matches, caps not exceeded, kill switch off, dry-run honoured, stage allowed.
- [ ] **P8.4** [AGENT] Retries reuse the same request ID; a timeout never causes a second refund.
- [ ] **P8.5** [AGENT] Wire AUTO_EXECUTE decisions to the executor; then send the customer email; then close the case.
- [ ] **P8.6** [AGENT] Show the refund ID and outcome on the case detail screen and in the audit log.
- [ ] **P8.7** [AGENT] Tests: double-click, retry after a lost response, over-refund attempt, kill switch on.

**Acceptance (all must be shown to pass):**
- [ ] End to end in the sandbox: complaint “package never arrived” → evidence → rule fires → refund executes → customer emailed → audit trail shows facts, rule, score and refund ID.

**GATE M4 First real action (Case 1):** stop. Summarise what works, show evidence (test output, screenshots, IDs), list anything not done, and wait for me to say "gate passed".

---
## Step 9: Phase 9 — Approval flow and the damaged-item case (Demo case 2)
**Goal:** Show the human-in-the-loop path with photo evidence and a lower-confidence decision.

**Read first:** `docs/03-decision-logic.md`, `docs/06-app-map.md`

- [ ] **P9.1** [AGENT] **Vision analysis:** send the uploaded photo to the vision model and extract: visible damage, consistency with the ordered item, image quality. Feed these into the score as signals, never as the sole basis.
- [ ] **P9.2** [AGENT] **Approval actions:** approve as recommended; edit amount; change resolution (refund, partial refund, replacement, return-then-refund); reject with a required reason.
- [ ] **P9.3** [AGENT] Store every edit and rejection reason in approvals for later learning.
- [ ] **P9.4** [AGENT] Draft the customer message from approved facts only; let the reviewer edit it.
- [ ] **P9.5** [AGENT] Reviewer notifications by email and in-app badge.

**Acceptance (all must be shown to pass):**
- [ ] The damaged-item case pauses at “human approval required”, the breakdown shows why confidence is lower, the reviewer approves, and the executor completes the action.

**GATE M5 Human in the loop (Case 2):** stop. Summarise what works, show evidence (test output, screenshots, IDs), list anything not done, and wait for me to say "gate passed".

---
## Step 10: Phase 10 — Dispute pipeline (Demo case 3), including the Disputes screen
**Goal:** Handle a PayPal dispute from webhook to evidence submission, respecting stage rules.

**Read first:** `docs/PayPal-Findings.md`, `docs/02-architecture.md`, `docs/03-decision-logic.md`

- [ ] **P7.6** [AGENT] **Disputes ( /app/disputes ):** PayPal cases with stage, due date and an evidence checklist (have / missing).
- [ ] **P10.1** [AGENT] **Webhook endpoint:** verify the signature, de-duplicate by event ID, store the raw event, then queue processing.
- [ ] **P10.2** [AGENT] **On dispute created:** fetch the dispute, link it to the order and create or update the case; record stage, status, reason, due date and the links the response offers.
- [ ] **P10.3** [AGENT] **Evidence mapper:** read the requested evidence, map each item to evidence you hold (for example carrier and tracking number, fulfilment proof, transaction ID, notes), and show a have / missing checklist.
- [ ] **P10.4** [AGENT] **Stage-aware actions:** make_offer only in the inquiry stage; provide_evidence only when PayPal is waiting for the seller and the link is present; accept_claim human-only; send_message allowed where PayPal permits.
- [ ] **P10.5** [AGENT] **Recommendation:** use the cost advisor to recommend defend, offer or accept, with the numbers shown.
- [ ] **P10.6** [AGENT] **Submission:** by default require approval; allow auto-submit only if the merchant policy says so.
- [ ] **P10.7** [AGENT] **Monitoring:** handle update and resolved events, refresh the case and notify the merchant; send deadline reminders.
- [ ] **P10.8** [YOU+AGENT] If API-created disputes are unavailable, create them from the buyer account and use real events from the sandbox plus the simulator.

**Acceptance (all must be shown to pass):**
- [ ] A sandbox dispute produces a case with a correct checklist; the reviewer approves; the evidence is submitted through the Disputes API; the case updates when PayPal sends the next event.

**GATE M6 Disputes (Case 3):** stop. Summarise what works, show evidence (test output, screenshots, IDs), list anything not done, and wait for me to say "gate passed".

---
## Step 11: Phase 7b — Merchant portal: Audit, Team, Settings
**Goal:** Remaining merchant screens.

**Read first:** `docs/06-app-map.md`

- [ ] **P7.7** [AGENT] **Audit ( /app/audit ):** searchable log with export.
- [ ] **P7.8** [AGENT] **Team ( /app/team )** and **Settings ( /app/settings ):** invites, roles, caps, mode and kill switch.

---
## Step 12: Phase 12 — Security, evaluation and hardening
**Goal:** Prove the system is safe and measure how well it works.

**Read first:** `docs/04-security.md`, `docs/09-eval-and-demo.md`

- [ ] **P12.1** [AGENT] Build a labelled set of **40–60 synthetic cases** covering every case type, edge cases and abuse cases.
- [ ] **P12.2** [AGENT] Write an evaluation script that reports the metrics in section 14.
- [ ] **P12.3** [AGENT] Run the adversarial suite: injection in message text, in filenames and in image text; forged tracking numbers; order/email mismatch; serial refunder; amount manipulation; replayed webhook; double submit.
- [ ] **P12.4** [AGENT] Security pass: secrets handling, role checks on every endpoint, tenant-isolation tests, rate limits, upload validation, CORS, dependency audit and no personal data in logs.
- [ ] **P12.5** [AGENT] Reliability: timeouts and retries for LLM and PayPal calls, a dead-letter list for failed jobs, and a guaranteed fail-safe to approval.

**Acceptance (all must be shown to pass):**
- [ ] You can quote classification accuracy, escalation rate and the false auto-refund rate from a repeatable run.
- [ ] All adversarial cases are held by the policy engine or executor.

---
## Step 13: Phase 11 — Policy builder, shadow mode, analytics and learning
**Goal:** Make the product usable by non-technical merchants and let them build trust before automating.

**Read first:** `docs/03-decision-logic.md`, `docs/06-app-map.md`

- [ ] **P11.1** [AGENT] Starter templates and a plain-English text box.
- [ ] **P11.2** [AGENT] LLM compiles the text to the JSON rule schema; show the result as readable rule cards plus the JSON, and flag anything ambiguous.
- [ ] **P11.3** [AGENT] **Backtest:** run the draft policy against past or seeded cases and show how many would auto-execute, need approval or be blocked.
- [ ] **P11.4** [AGENT] Publish creates a new version; allow rollback.
- [ ] **P11.5** [AGENT] The agent records what it would have done and compares it with what the merchant actually did. Show agreement rate and estimated time saved.
- [ ] **P11.6** [AGENT] Auto-resolution rate, escalation rate, refunds by reason, disputes handled, override rate, and estimated hours saved (state the assumption used).
- [ ] **P11.7** [AGENT] Summarise repeated rejections and suggest a policy change. It is a suggestion only; never change a policy automatically.

**Acceptance (all must be shown to pass):**
- [ ] A merchant can type a refund rule in plain English, see it compiled, backtest it and publish it; shadow mode shows an agreement metric.

**GATE M7 Trust layer:** stop. Summarise what works, show evidence (test output, screenshots, IDs), list anything not done, and wait for me to say "gate passed".

---
## Step 14: Phase 3 — Merchant onboarding and integrations
**Goal:** Guide a new merchant from an empty account to a connected, safe starting configuration.

**Read first:** `docs/06-app-map.md`, `docs/PayPal-Findings.md`

- [ ] **P3.1** [AGENT] **Step 1 Business profile:** name, support email, currency, timezone, store URL.
- [ ] **P3.2** [AGENT] **Step 2 Connect PayPal:** for the hackathon, use server-held sandbox credentials for each demo merchant (or a form to paste sandbox credentials, stored encrypted). Show a connection-status check. Describe PayPal’s partner / third-party permission onboarding as the production path, after confirming its requirements.
- [ ] **P3.3** [AGENT] **Step 3 Store data:** use the seeded mock store; optionally add CSV order import.
- [ ] **P3.4** [AGENT] **Step 4 Carrier tracking:** mock carrier by default; an aggregator is optional.
- [ ] **P3.5** [AGENT] **Step 5 Policy:** choose a starter template (details come in Phase 11).
- [ ] **P3.6** [AGENT] **Step 6 Mode:** Shadow (recommend only), Approval for everything, or Auto within rules. Default to Shadow or Approval.
- [ ] **P3.7** [AGENT] **Step 7 Webhook health:** show whether PayPal events are arriving.
- [ ] **P3.8** [AGENT] Status, last-checked time and a “test connection” button for PayPal, carrier, store and webhooks.

**Acceptance (all must be shown to pass):**
- [ ] A new merchant can finish the wizard and see all integrations green in the sandbox.
- [ ] Credentials are encrypted at rest and never returned to the browser.

---
## Step 15: Phase 1b — Landing page and public pages
**Goal:** Public website.

**Read first:** `docs/06-app-map.md`, docs/07-phases.md (Phase 1)

- [ ] **P1.4** [AGENT] **Hero:** one-line promise (resolve complaints before they become PayPal disputes) with two buttons: “Try the demo” and “Get started”.
- [ ] **P1.5** [AGENT] **Problem strip:** evidence scattered across PayPal, carrier, inbox and policy.
- [ ] **P1.6** [AGENT] **How it works:** understand → decide within your rules → act with approval.
- [ ] **P1.7** [AGENT] **Three scenario cards:** lost package auto-refund, damaged item needing approval, dispute evidence submission, each with a short animated or static case timeline.
- [ ] **P1.8** [AGENT] **Trust section:** rules decide, humans approve high-risk cases, full audit trail, sandbox-first.
- [ ] **P1.9** [AGENT] **Who it is for:** small PayPal merchants. **FAQ.** **Footer** with legal links.
- [ ] **P1.10** [AGENT] /how-it-works, /security (explain the guardrails in section 8 in plain language), /demo (entry to the pre-seeded merchant), /privacy and /terms placeholders, 404 and error pages.
- [ ] **P1.11** [AGENT] Do not invent pricing or customer logos. If you need a pricing area, label it “Free during beta” or leave it out.

**Acceptance (all must be shown to pass):**
- [ ] The landing page and supporting pages render well on phone and desktop.
- [ ] The UI kit is used by at least one page in each of the four shells.

---
## Step 16: Phase 13 — Demo mode, deployment and rehearsal
**Goal:** Make the demo repeatable and robust.

**Read first:** `docs/09-eval-and-demo.md`

- [ ] **P13.1** [AGENT] **Simulator ( /admin/simulator ):** seed scenarios, change carrier status, replay a webhook, reset to a clean state with one click. **/demo** logs into the seeded merchant.
- [ ] **P13.2** [YOU+AGENT] Deploy to a host with HTTPS so PayPal webhooks reach you; set environment secrets; confirm sandbox mode is visibly labelled in the UI.
- [ ] **P13.3** [YOU] Record a **fallback video** of a full successful run in case Wi-Fi or the sandbox misbehaves.
- [ ] **P13.4** [YOU+AGENT] Write the demo script (section 15), prepare slides and a one-page architecture diagram, and rehearse at least three times with a timer.
- [ ] **P13.5** [YOU] Prepare answers on trust and safety, what is real versus simulated, and the production path (PayPal partner onboarding, real carrier data).

**Acceptance (all must be shown to pass):**
- [ ] Three clean timed rehearsals; reset takes under a minute; fallback video exists.

**GATE M8 Demo-ready:** stop. Summarise what works, show evidence (test output, screenshots, IDs), list anything not done, and wait for me to say "gate passed".

