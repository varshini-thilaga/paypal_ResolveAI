> Source: Merged Plan, section 7. Section numbers mentioned in the text refer to `docs/source/ResolveAI_Merged_Plan.md`.

# 7. Core logic

## 7.1 Policy engine

Merchants describe rules in plain English; an LLM compiles them to structured JSON that the merchant reviews and publishes. At run time **only the JSON is evaluated, by code**. Example:

> {
>
> "policy_id": "pol_001", "version": 3,
>
> "global": { "max_auto_refund_usd": 100, "max_auto_refunds_per_day": 20, "kill_switch": false },
>
> "rules": \[
>
> { "id": "inr_lost_small",
>
> "when": { "case_type": "ITEM_NOT_RECEIVED", "amount_lte": 100,
>
> "carrier_status": "LOST", "customer_refunds_90d_lt": 2 },
>
> "then": "AUTO_EXECUTE", "action": { "type": "REFUND_FULL" } },
>
> { "id": "damaged_any",
>
> "when": { "case_type": "ITEM_DAMAGED" },
>
> "then": "REQUIRE_APPROVAL" }
>
> \],
>
> "default": "REQUIRE_APPROVAL"
>
> }

- Outcomes: AUTO_EXECUTE, REQUIRE_APPROVAL, DENY, ESCALATE.

- Unknown or missing data resolves to REQUIRE_APPROVAL, never to auto-execute.

- **Define “carrier confirms loss” carefully.** Treat LOST as either a carrier-reported lost sub-status, or no tracking scan for N days past the estimated delivery date (N is merchant-configurable). Do not treat a generic exception as loss.

- Policies are versioned; every decision records the policy version it used.

## 7.2 Risk score (heuristic, not a probability)

| **Signal**                    | **Source**         | **Direction**                                                |
|-------------------------------|--------------------|--------------------------------------------------------------|
| Evidence completeness         | Evidence Pack      | More complete evidence raises the score                      |
| Tracking consistency          | Carrier connector  | Tracking agrees with the claim raises it                     |
| Amount                        | PayPal capture     | Higher amount lowers it                                      |
| Customer history              | Store DB / cases   | Prior refunds or disputes in 90 days lower it                |
| Address / identity match      | Order vs complaint | Mismatch lowers it                                           |
| Classification agreement      | Repeated LLM runs  | Disagreement lowers it                                       |
| Image quality and consistency | Vision model       | Blurry or inconsistent photo lowers it; never the sole basis |

Start with hand-set weights, then tune them against the labelled evaluation set. Show the breakdown in the UI. Do not present the total as “96% likely correct”.

## 7.3 Cost advisor

- **Refund now:** cost = refund amount; no dispute fee; no dispute-ratio impact.

- **Defend / offer:** expected cost = (1 − estimated win chance) × item value + chance of fee × fee amount, plus the projected effect on the dispute ratio. The win chance is a **heuristic from evidence completeness** until you have real outcomes; label it so.

- **Seller Protection:** show eligibility as met / not met / needs review based on the documented requirements (for example proof of delivery for item-not-received).

- The fee amount and dispute-ratio threshold are merchant-editable settings; do not hard-code figures.
