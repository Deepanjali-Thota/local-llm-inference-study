# Label Policy

Each ticket gets exactly one category, based on the customer's main need.

## Categories
- **billing**: payments, charges, refunds, invoices, receipts, pricing, discounts, plans, seat/plan upgrades or downgrades
- **technical**: bugs, errors, crashes, slowness, something not working as expected
- **account**: login, password, profile, permissions, security, deleting or changing an account
- **other**: feature requests, feedback, company questions, legal, partnerships, anything else

## Tie-break rules
1. Choose by the customer's main need, not by words that appear in the ticket.
2. Permissions or access problems → account, even if they look like a bug.
3. Changing plan, seats or users (upgrade, downgrade, limits tied to a plan) → billing.
4. A payment or checkout page that errors or freezes → technical (the bug is the problem, not the charge).
5. Paid but the purchased feature isn't active → billing.
6. Requests for new features or integrations → other.
7. If rules conflict, the more specific problem wins: a broken payment/checkout page (rule 4) beats a plan change (rule 3).