"""Analytics router for dashboard summary metrics."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user
from app.db import get_session
from app.models.tables import Alert, TrackedItem, Product

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
async def get_summary(
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Get aggregated dashboard metrics."""
    total_items = 0
    total_alerts = 0
    total_savings = 0.0
    best_deal = None

    try:
        # Count tracked items
        count_stmt = select(func.count()).select_from(TrackedItem).where(TrackedItem.user_id == user.id)
        result = await session.execute(count_stmt)
        total_items = result.scalar() or 0

        # Get alerts for user
        alerts_stmt = (
            select(Alert)
            .join(TrackedItem)
            .where(TrackedItem.user_id == user.id)
            .options(selectinload(Alert.tracked_item).selectinload(TrackedItem.product))
        )
        result = await session.execute(alerts_stmt)
        alerts = result.scalars().all()
        total_alerts = len(alerts)

        for alert in alerts:
            old_price = alert.old_price or 0
            new_price = alert.new_price or 0
            savings = old_price - new_price
            if savings > 0:
                total_savings += savings

            if old_price > 0:
                pct_drop = ((old_price - new_price) / old_price) * 100
                if pct_drop > 0 and (best_deal is None or pct_drop > best_deal["pct_drop"]):
                    product_name = "Unknown Product"
                    if alert.tracked_item and alert.tracked_item.product:
                        product_name = alert.tracked_item.product.name
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
