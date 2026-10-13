# PayPal findings (source of truth, fill during Phase 0)
Rule: if it is not confirmed here, do not assume it.

| Item | Expected | Confirmed? | Actual behaviour / payload | Date |
|---|---|---|---|---|
| Refund: full (empty body) | | | | |
| Refund: partial | | | | |
| Refund: retry with same request ID | | | | |
| Add tracking | | | | |
| Dispute stages and statuses | | | | |
| Links offered per stage | | | | |
| provide-evidence at correct stage | | | | |
| provide-evidence at wrong stage (error) | | | | |
| make-offer (inquiry only?) | | | | |
| Evidence types and file limits | | | | |
| Create dispute via API possible? | | | | |
| Webhook events and signature verification | | | | |
| Sandbox country and currency used | | | | |
| MCP/toolkit dispute tools available | | | | |

---
## Beliefs from the plan (unverified, to confirm in Phase 0)
The table below is Merged Plan section 5. Nothing in it is confirmed until recorded above.

These come from earlier research and from the two plans compared. PayPal documentation changes, so **treat every row as “believed, confirm in the sandbox”**. Phase 0 exists to settle them.

| **Item**                             | **What is believed**                                                                                                     | **How to verify**                                     | **Fallback**                                                                                                     |
|--------------------------------------|--------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|
| Refund call                          | Refund a capture; empty body = full; request-ID header makes retries idempotent                                          | Call it twice with the same request ID in sandbox     | Store our own idempotency key and check refund status before retry                                               |
| Dispute stages and links             | Offers only in inquiry; evidence only when waiting for seller; available actions appear as links in the dispute response | Open a sandbox dispute and GET it at each stage       | Gate every action by stage and by presence of the link                                                           |
| Creating disputes in sandbox via API | Needs a special scope that may require contacting PayPal                                                                 | Try the API call                                      | Open disputes from the sandbox buyer account in Resolution Center; use the webhook simulator for events          |
| Evidence types and file limits       | Item-not-received accepts carrier + tracking number, notes, documents; file type/size limits exist                       | Read the Provide Evidence docs and test an upload     | Constrain uploads in our UI to the allowed types                                                                 |
| MCP / toolkit dispute tools          | Sources disagree on list; no provide-evidence tool                                                                       | Read the current tool reference                       | Use the REST Disputes API directly                                                                               |
| Webhook signature verification       | PayPal provides a way to verify webhook signatures                                                                       | Implement against the docs and send a simulator event | Reject unverified events                                                                                         |
| Dispute and Seller Protection rules  | Item-not-received protection needs proof of delivery; card-chargeback claims may be ineligible                           | Read the Seller Protection page                       | Show eligibility as “needs review”, not as a fact                                                                |
| Fees                                 | Third-party sources disagree                                                                                             | PayPal’s official fee page                            | Make fee a merchant-editable setting, never hard-coded                                                           |
| Sandbox country / currency           | Features and currencies depend on account country                                                                        | Create accounts in a country with full REST support   | Use USD for the demo, matching the \$89 example                                                                  |
| Multi-merchant PayPal connection     | A real product needs PayPal’s third-party permission / partner onboarding                                                | Read the partner docs                                 | Hackathon: server-held sandbox credentials per demo merchant; describe partner onboarding as the production path |
