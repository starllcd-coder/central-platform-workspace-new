from decimal import Decimal

from .models import MarketplaceListing


def compute_marketplace_rankings(*, module_id=None, tenant_ids=None, limit=100):
    qs = MarketplaceListing.objects.filter(is_active=True).select_related("tenant", "module")
    if module_id:
        qs = qs.filter(module_id=module_id)
    if tenant_ids is not None:
        qs = qs.filter(tenant_id__in=tenant_ids)

    rows = list(qs[:1000])
    if not rows:
        return []

    prices = [row.base_price for row in rows]
    min_price = min(prices)
    max_price = max(prices)
    price_span = max_price - min_price

    score_rows = []
    for row in rows:
        rating_score = min(max(Decimal(row.average_rating), Decimal("0")), Decimal("5")) / Decimal("5")
        if price_span <= 0:
            price_score = Decimal("1")
        else:
            price_score = (max_price - row.base_price) / price_span
        plan_score = min(max(Decimal(row.plan_level_boost), Decimal("0")), Decimal("100")) / Decimal("100")
        manual_score = Decimal(row.manual_boost) / Decimal("100")

        final_score = (
            rating_score * Decimal("0.50")
            + price_score * Decimal("0.35")
            + plan_score * Decimal("0.15")
            + manual_score
        )
        score_rows.append(
            {
                "tenant_id": row.tenant_id,
                "tenant_name": row.tenant.name,
                "tenant_code": row.tenant.tenant_code,
                "module_id": row.module_id,
                "module_code": row.module.code,
                "module_name": row.module.name,
                "base_price": row.base_price,
                "average_rating": row.average_rating,
                "rating_count": row.rating_count,
                "plan_level_boost": row.plan_level_boost,
                "manual_boost": row.manual_boost,
                "score": final_score.quantize(Decimal("0.0001")),
            }
        )

    score_rows.sort(
        key=lambda item: (
            item["score"],
            item["average_rating"],
            -item["base_price"],
            item["rating_count"],
        ),
        reverse=True,
    )
    return score_rows[: max(1, int(limit))]
