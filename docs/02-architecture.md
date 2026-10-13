> Source: Merged Plan, section 6. Section numbers mentioned in the text refer to `docs/source/ResolveAI_Merged_Plan.md`.

# 6. System architecture

> Customer portal / email ─┐ ┌─ Merchant portal
>
> PayPal webhooks ─────────┤ │ (approve / edit / reject)
>
> Carrier webhooks ────────┴─► Case Orchestrator (state machine) ─► Audit log
>
> │
>
> ┌───────────────────────┼──────────────────────┐
>
> ▼ ▼ ▼
>
> Evidence connectors Reasoning layer (LLM) Policy engine (code)
>
> • PayPal txn/dispute • Classify complaint • Merchant rules (JSON)
>
> • Carrier tracking • Extract claims • Caps, blocklists
>
> • Store DB / invoices • Vision on photos • AUTO / APPROVE / DENY
>
> • Customer history • Draft messages / ESCALATE
>
> └──────► Evidence Pack ──► Risk scorer + Cost advisor
>
> │
>
> ▼
>
> Action executor (the ONLY writer)
>
> refund · make_offer · provide_evidence · send_message
>
> add_tracking · accept_claim = human-only

## 6.1 Case state machine

> RECEIVED → CLASSIFIED → EVIDENCE_GATHERED → DECIDED
>
> → AUTO_EXECUTED or PENDING_APPROVAL → EXECUTED → CLOSED
>
> Side states: NEEDS_INFO, ESCALATED, REJECTED, FAILED

Every transition writes an audit event. If any step fails (LLM timeout, PayPal error, missing evidence), the case falls back to **PENDING_APPROVAL or ESCALATED**, never to automatic action.

## 6.2 Modules

| **Module**                      | **Responsibility**                                                                       | **Notes**                                                                                                                                |
|---------------------------------|------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| Intake                          | Customer form, email ingest (stretch), PayPal and carrier webhooks                       | Webhook endpoints verify signatures and are idempotent on event ID                                                                       |
| Classifier (LLM)                | Map complaint to a case type; extract claims and desired outcome; structured JSON output | Taxonomy mirrors PayPal dispute reasons (for example item not received, not as described, unauthorised, credit not processed, duplicate) |
| Evidence connectors (read-only) | PayPal order/capture/dispute, carrier tracking, store DB, customer history, photos       | Produce a normalised Evidence Pack                                                                                                       |
| Policy engine                   | Evaluate merchant rules and global caps; output a gate                                   | Pure function, fully unit-tested, no LLM inside                                                                                          |
| Risk scorer                     | Transparent score from named signals                                                     | Heuristic, calibrated on the test set                                                                                                    |
| Cost advisor                    | Compare refund, offer and defend                                                         | Shows the numbers behind each path                                                                                                       |
| Action executor                 | Only module with PayPal write credentials                                                | Idempotency, caps, dry-run, kill switch, stage checks                                                                                    |
| Dispute pipeline                | Read requested evidence, map to held evidence, submit                                    | Stage-aware; deadline reminders                                                                                                          |
| Communications                  | Draft customer messages from approved facts only                                         | Never promises anything the decision does not cover                                                                                      |
| Merchant portal                 | Review, approve, configure, analyse                                                      | Section 10                                                                                                                               |
| Audit log                       | Append-only record of facts, rule, score and action                                      | Exportable                                                                                                                               |
