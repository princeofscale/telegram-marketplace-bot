# Providers

This file is the source of truth for external inventory providers connected to the bot.

## lolz.market / lzt.market

Status: integration scaffolded through the `LOLZTEAM` Python client.

Purpose:
- Import marketplace items into `source_products`.
- Expose selected items in `catalog_products`.
- Keep one local `inventory_items` reservation row per external marketplace item.
- On user purchase, reserve and validate the item via the provider API before confirming the external purchase.

API notes:
- Python package: `lolzteam`.
- Primary market API base used by the package: `https://prod-api.lzt.market`.
- Authorization: market token from `https://lolz.live/account/api` / `https://lzt.market/account/api`.
- The package sends `Authorization: Bearer <token>`.
- General API rate limit from public docs: 20 requests per minute.
- Search/list rate limit from public docs: 10 requests per minute.
- Market list wrapper: `market.categories.get(category_name=...)`.
- Item details wrapper: `market.managing.get(item_id=...)`.
- Purchase flow in current package version:
  - `market.purchasing.cart.add(item_id=...)`
  - `market.purchasing.check(item_id=...)`
  - `market.purchasing.buy(item_id=..., price=...)`

Current env vars:
- `LOLZ_MARKET_ACCESS_TOKEN`
- `LOLZ_MARKET_BASE_URL`
- `LOLZ_MARKET_CATEGORIES`
- `LOLZ_MARKET_SYNC_LIMIT_PER_CATEGORY`
- `LOLZ_BALANCE_USERNAME`
- `LOLZ_BALANCE_CURRENCY`

## LOLZ Balance top-ups

Status: integration scaffolded through the `LOLZTEAM` Python client.

Purpose:
- Generate a transfer link to the merchant LOLZ account.
- Store a unique transfer comment as `deposits.provider_payment_id`.
- Verify incoming transfer history by the same comment before crediting the local user balance.

Current receiver:
- `princeofscale` (`https://lolz.live/princeofscale/`)

Flow:
- User chooses a top-up amount.
- Bot creates a pending deposit with `payment_method=lolz_balance`.
- Bot sends a payment URL like `https://lzt.market/balance/transfer?username=princeofscale&amount=100.00&comment=lolz:<user_id>:<deposit_id>&hold=0`.
- User pays through LOLZ.
- Bot checks `market.payments.history(operation_type="income", comment=<deposit_comment>)`.
- Existing deposit verification logic credits the user only when the incoming amount is at least the requested amount.

API notes:
- Payment link target: `https://lzt.market/balance/transfer`.
- History wrapper: `market.payments.history(...)`.
- History endpoint: `GET /user/payments`.
- Transfer endpoint for outgoing payments: `POST /balance/transfer`; not used for user top-ups because users pay manually through the generated link.

Open decisions:
- Which categories are allowed in production.
- Markup policy per category.
- Whether to auto-sync on a schedule or keep sync as an admin/manual job.
- Refund/failure policy if the provider confirms purchase but the local DB commit fails.

References:
- [Official LOLZTEAM Market.md](https://github.com/AS7RIDENIED/LOLZTEAM/blob/main/Documentation/Market.md)
- [LOLZTEAM PyPI](https://pypi.org/project/LOLZTEAM/)
- [Token page](https://lolz.live/account/api)
