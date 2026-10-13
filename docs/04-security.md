> Source: Merged Plan, section 8. Section numbers mentioned in the text refer to `docs/source/ResolveAI_Merged_Plan.md`.

# 8. Security and guardrails

| **Threat**                                                  | **Control**                                                                                                                                                     |
|-------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Prompt injection in complaint text, filenames or image text | Customer content is passed as delimited data; model output must match a JSON schema; the model has no tool access to money; the policy engine ignores free text |
| Refund over-payment or double refund                        | Executor validates amount against remaining captured amount; idempotency key per action; request-ID header on PayPal calls                                      |
| Runaway automation                                          | Per-refund cap, daily cap, kill switch, dry-run mode, shadow mode                                                                                               |
| Wrong-stage dispute action                                  | Executor checks stage and presence of the API link before offer or evidence; accept-claim is human-only                                                         |
| Forged or replayed webhooks                                 | Signature verification, event-ID de-duplication, reject on failure                                                                                              |
| Spoofed complaints                                          | Order number + email match, rate limiting, magic-link case pages                                                                                                |
| Serial refund abuse                                         | Customer history signal and blocklist rule                                                                                                                      |
| Cross-tenant data leak                                      | Every query scoped by merchant ID; role checks server-side                                                                                                      |
| Malicious uploads                                           | File-type and size validation, strip image metadata, store outside web root                                                                                     |
| Credential theft                                            | PayPal secrets encrypted at rest and never sent to the browser or the LLM                                                                                       |
| LLM outage or bad output                                    | Fail safe to PENDING_APPROVAL                                                                                                                                   |
