> Source: Merged Plan, section 10. Section numbers mentioned in the text refer to `docs/source/ResolveAI_Merged_Plan.md`.

# 10. Application map: users, portals and pages

## 10.1 Who uses what

| **User**                   | **Account?**    | **Entry point** | **Can do**                                                                                       |
|----------------------------|-----------------|-----------------|--------------------------------------------------------------------------------------------------|
| Visitor                    | No              | Landing site    | Learn, try the demo, sign up                                                                     |
| Merchant owner             | Yes             | Merchant portal | Everything, including policy, caps, kill switch, team, integrations                              |
| Merchant reviewer          | Yes             | Merchant portal | Review cases, approve/edit/reject, submit dispute evidence; cannot change policy or integrations |
| Merchant viewer            | Yes             | Merchant portal | Read-only access to cases and analytics                                                          |
| Customer                   | No (magic link) | Customer portal | Report a problem, upload photos, track status, reply                                             |
| Platform admin (demo only) | Yes             | Simulator       | Seed data, change carrier status, replay webhooks, reset                                         |

## 10.2 Sitemap

| **Area**        | **Route (suggested)**             | **Purpose**                                           | **Access**                 |
|-----------------|-----------------------------------|-------------------------------------------------------|----------------------------|
| Public site     | /                                 | Landing page                                          | Public                     |
|                 | /how-it-works                     | Pipeline explained with the three scenarios           | Public                     |
|                 | /security                         | Guardrails and human-approval explained               | Public                     |
|                 | /demo                             | Enter a pre-seeded demo merchant                      | Public                     |
|                 | /privacy, /terms                  | Legal placeholders                                    | Public                     |
| Auth            | /signup, /login, /verify-email    | Create account, sign in, confirm email                | Public                     |
|                 | /forgot-password, /reset-password | Password recovery                                     | Public                     |
|                 | /accept-invite                    | Join a merchant team                                  | Invite token               |
| Onboarding      | /app/onboarding                   | Setup wizard                                          | Owner                      |
| Merchant portal | /app                              | Home dashboard                                        | All roles                  |
|                 | /app/cases                        | Case inbox with filters                               | All roles                  |
|                 | /app/cases/\[id\]                 | Case detail and decision                              | All roles; actions by role |
|                 | /app/approvals                    | Approval queue                                        | Reviewer, owner            |
|                 | /app/disputes                     | PayPal disputes with deadlines and evidence checklist | Reviewer, owner            |
|                 | /app/policies                     | Policy list, builder, versions                        | Owner (view for others)    |
|                 | /app/analytics                    | Metrics and shadow-mode savings                       | All roles                  |
|                 | /app/audit                        | Audit log and export                                  | Owner, reviewer            |
|                 | /app/integrations                 | PayPal, carrier, store, webhook health                | Owner                      |
|                 | /app/team                         | Invites and roles                                     | Owner                      |
|                 | /app/settings                     | Profile, caps, mode, kill switch, notifications       | Owner                      |
| Customer portal | /c/\[merchant\]/report            | Complaint form                                        | Public                     |
|                 | /case/\[token\]                   | Case status, messages, extra uploads                  | Magic link                 |
| Demo tools      | /admin/simulator                  | Seed, carrier status control, webhook replay, reset   | Platform admin             |

## 10.3 Main user journeys

**Merchant**

1.  Sign up → verify email → onboarding wizard (profile, PayPal, store, carrier, policy, mode).

2.  Home dashboard shows open cases, approvals waiting and dispute deadlines.

3.  Open a case → read evidence and recommendation → approve, edit or reject → see the result and audit entry.

**Customer**

1.  Open the merchant’s report page → enter order number and email → describe the problem, choose desired outcome, upload photos.

2.  Receive a confirmation email with a magic link to the case page.

3.  Follow the timeline, answer questions, receive the outcome email.

**Dispute**

1.  Buyer opens a PayPal dispute → webhook arrives → case created and linked to the order.

2.  Agent reads what PayPal requests, builds an evidence checklist and recommendation.

3.  Reviewer approves (or policy allows auto) → evidence submitted → status tracked to resolution.
