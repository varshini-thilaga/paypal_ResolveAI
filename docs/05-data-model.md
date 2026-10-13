> Source: Merged Plan, section 9. Section numbers mentioned in the text refer to `docs/source/ResolveAI_Merged_Plan.md`.

# 9. Data model

Every table carries a merchant_id so tenant isolation can be enforced in every query.

| **Table**                     | **Key fields**                                                                                                | **Notes**                                                        |
|-------------------------------|---------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| merchants                     | id, name, slug, support_email, currency, timezone, mode (shadow / approval / auto), kill_switch               | One per business                                                 |
| users, memberships            | user id, email, password hash (or auth-provider ID), merchant_id, role (owner / reviewer / viewer)            | Platform admin is a separate flag, demo only                     |
| paypal_connections            | merchant_id, environment, encrypted credentials, status, last_checked                                         | Never exposed to the browser                                     |
| customers                     | merchant_id, email, name, refund_count_90d, dispute_count_90d, blocked                                        | Derived counters                                                 |
| orders, order_items           | order number, paypal_order_id, capture_id, amount, currency, status, items                                    | Store the capture ID at checkout; do not rely on searching later |
| fulfillments, tracking_events | carrier, tracking number, status, sub-status, event time                                                      | Fed by the mock carrier or an aggregator                         |
| cases                         | merchant_id, source (complaint / dispute), type, state, order_id, amount, opened_at, due_at, magic_token_hash | Central entity                                                   |
| case_messages, attachments    | author (customer / merchant / agent), body, file path, mime type, size                                        | Customer text is always untrusted                                |
| evidence_items                | case_id, kind, source, payload, fetched_at                                                                    | Backs the Evidence Pack                                          |
| decisions                     | case_id, proposed_action, gate, rule_id, policy_version, score breakdown, cost comparison, model version      | One per evaluation                                               |
| approvals                     | decision_id, reviewer, outcome (approve / edit / reject), edited_values, reason                               | Override reasons feed learning                                   |
| actions                       | case_id, type, idempotency key, request payload, PayPal response ID, status                                   | Written only by the executor                                     |
| policies                      | merchant_id, version, source text, compiled JSON, status, published_by                                        | Versioned with rollback                                          |
| disputes                      | case_id, paypal_dispute_id, stage, status, reason, requested evidence, due date, available links              | Mirrors PayPal                                                   |
| webhook_events                | provider, event id, type, signature valid, processed_at                                                       | De-duplication                                                   |
| audit_log                     | actor, event, entity, before/after, timestamp                                                                 | Append-only                                                      |
