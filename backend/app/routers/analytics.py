"""Analytics router for dashboard summary metrics."""

import logging

from fastapi import APIRouter

from app.db import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
async def get_summary():
    """Get aggregated dashboard metrics: total items, alerts, savings, best deal."""
    db = get_db()

    total_items = 0
    total_alerts = 0
    total_savings = 0.0
    best_deal = None

    try:
        # Count tracked items
        items_result = db.table("tracked_items").select("id", count="exact").execute()
        total_items = items_result.count or 0

        # Get alerts with price data
        alerts_result = (
            db.table("alerts")
            .select("*, tracked_items(product_id, products(name))")
            .execute()
        )
        alerts = alerts_result.data or []
        total_alerts = len(alerts)

        for alert in alerts:
            old_price = alert.get("old_price", 0) or 0
            new_price = alert.get("new_price", 0) or 0
            savings = old_price - new_price
            if savings > 0:
                total_savings += savings

            # Calculate percentage drop for best deal
            if old_price > 0:
                pct_drop = ((old_price - new_price) / old_price) * 100
                if pct_drop > 0 and (best_deal is None or pct_drop > best_deal["pct_drop"]):
                    product_name = "Unknown Product"
                    tracked_items = alert.get("tracked_items")
                    if tracked_items:
                        products = tracked_items.get("products")
                        if products:
                            product_name = products.get("name", "Unknown Product")

                    best_deal = {
                        "product_name": product_name,
                        "old_price": old_price,
                        "new_price": new_price,
                        "pct_drop": round(pct_drop, 1),
                    }

    except Exception as e:
        logger.error("Error fetching analytics summary: %s", e)

    return {
        "total_items": total_items,
        "total_alerts": total_alerts,
        "total_savings": round(total_savings, 2),
        "best_deal": best_deal,
    }
