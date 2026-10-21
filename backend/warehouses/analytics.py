import math
from typing import Any

from common.config import LOW_STOCK_THRESHOLD

# Days of projected demand the suggested order must cover
_TARGET_DAYS = 30
# Safety stock knobs: buffer against demand variability over the supplier lead time at a target
# service level. There is no lead-time data, so a one-week default is assumed (tune here);
# z = 1.28 targets a ~90% service level (raise towards 1.65 for ~95%). Safety stock is only
# added in warehouse mode, where real per-product demand variability is available.
_LEAD_TIME_DAYS = 7
_SERVICE_Z = 1.28
# Reference period for the formula-based fallback (no real sales data available)
_BASE_PERIOD_DAYS = 90
# Reference values used for the formula-based fallback multipliers
_REF_RATING = 3.5
_REF_PRICE = 50.0


def build_stock_report(
    products: list[dict[str, Any]],
    sales_velocity: dict[int, float] | None = None,
    demand_std: dict[int, float] | None = None,
) -> dict[str, Any]:
    """Reorder report for a product list.

    `sales_velocity` — {product_id: avg_daily_sales} — is the blended velocity computed by
    the warehouse service (local 70 % + other-warehouses average 30 %). When provided:
      - products not in the dict have velocity 0 (no demand signal → urgency ok, order 0)
      - urgency is driven by days-until-stockout only; zero velocity never causes critical

    `demand_std` — {product_id: std_of_daily_demand} — adds a safety stock on top of the
    mean 30-day coverage: `z × σ × sqrt(lead_time)`, so volatile (lumpy) demand gets a bigger
    buffer than steady demand with the same average. Absent/zero σ → no safety stock, matching
    the previous mean-only behaviour.

    When `sales_velocity` is None (global endpoint, no warehouse context), the formula below
    is used as a fallback (and no safety stock is added):
        review_base = num_reviews × 10 / _BASE_PERIOD_DAYS
        popularity  = (rating / 3.5) ^ 1.5
        price_sens  = (50 / price) ^ 0.35
        avg_daily   = review_base × popularity × price_sens
    """
    items = []
    for product in products:
        reviews = product.get("reviews") or []
        stock = product.get("stock") or 0
        product_id = product.get("id")

        if sales_velocity is not None:
            # Warehouse context: use blended velocity; absent product → zero demand
            avg_daily = sales_velocity.get(product_id, 0.0)
        else:
            # Global context: estimate from product attributes
            rating = product.get("rating") or _REF_RATING
            price = max(product.get("price") or _REF_PRICE, 0.01)
            review_base = len(reviews) * 10 / _BASE_PERIOD_DAYS
            popularity = (rating / _REF_RATING) ** 1.5
            price_sens = (_REF_PRICE / price) ** 0.35
            avg_daily = review_base * popularity * price_sens

        sales_90d = round(avg_daily * 90)
        projected_30d = math.ceil(avg_daily * 30)

        if avg_daily > 0:
            days_until_stockout: int | None = int(stock / avg_daily)
        else:
            days_until_stockout = None

        sigma = demand_std.get(product_id, 0.0) if demand_std is not None else 0.0
        safety_stock = math.ceil(_SERVICE_Z * sigma * math.sqrt(_LEAD_TIME_DAYS)) if sigma > 0 else 0

        raw_order = max(0, math.ceil(avg_daily * _TARGET_DAYS) + safety_stock - stock)
        min_qty = product.get("minimumOrderQuantity") or 1
        if raw_order > 0:
            suggested_order = max(raw_order, min_qty)
        elif stock == 0:
            suggested_order = min_qty  # no recent sales but nothing in stock — order the minimum
        else:
            suggested_order = 0

        if sales_velocity is not None:
            # Warehouse mode: out of stock is always critical; demand signal drives the rest
            if stock == 0 or (avg_daily > 0 and days_until_stockout < 7):
                urgency = "critical"
            elif avg_daily > 0 and days_until_stockout < 30:
                urgency = "warning"
            else:
                urgency = "ok"
        else:
            # Global mode: zero stock is always critical regardless of velocity estimate
            if stock == 0 or (days_until_stockout is not None and days_until_stockout < 7):
                urgency = "critical"
            elif days_until_stockout is not None and days_until_stockout < 30:
                urgency = "warning"
            else:
                urgency = "ok"

        items.append({
            "id": product.get("id"),
            "title": product.get("title"),
            "sku": product.get("sku"),
            "thumbnail": product.get("thumbnail"),
            "category": product.get("category"),
            "currentStock": stock,
            "avgDailySales": round(avg_daily, 3),
            "salesLast90Days": sales_90d,
            "projectedDemand30d": projected_30d,
            "daysUntilStockout": days_until_stockout,
            "safetyStock": safety_stock,
            "suggestedOrder": suggested_order,
            "urgency": urgency,
        })

    _urgency_rank = {"critical": 0, "warning": 1, "ok": 2}
    items.sort(key=lambda x: (
        _urgency_rank[x["urgency"]],
        x["daysUntilStockout"] if x["daysUntilStockout"] is not None else 99999,
    ))

    return {
        "items": items,
        "criticalCount": sum(1 for i in items if i["urgency"] == "critical"),
        "warningCount": sum(1 for i in items if i["urgency"] == "warning"),
        "totalSuggestedOrder": sum(i["suggestedOrder"] for i in items),
    }
