"""Demo router for reset functionality."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_session
from app.models.tables import Alert, TrackedItem, Product, PriceHistory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/demo", tags=["demo"])


@router.post("/reset")
async def reset_demo(
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Reset demo by clearing this user's tracked items and alerts."""
    try:
        # Get this user's tracked item IDs
        stmt = select(TrackedItem.id).where(TrackedItem.user_id == user.id)
        result = await session.execute(stmt)
        user_item_ids = [row[0] for row in result.all()]

        if user_item_ids:
            # Delete alerts for this user's tracked items
            await session.execute(
                delete(Alert).where(Alert.tracked_item_id.in_(user_item_ids))
            )
            # Delete this user's tracked items
            await session.execute(
                delete(TrackedItem).where(TrackedItem.user_id == user.id)
            )

        # Reset ALL product prices to original values
        stmt = select(Product).where(Product.original_price.is_not(None))
        result = await session.execute(stmt)
        products = result.scalars().all()
        for product in products:
            product.current_price = product.original_price

        # Clear price history
        await session.execute(delete(PriceHistory))

        await session.commit()
        return {"success": True, "message": "Demo reset complete"}

    except Exception as e:
        logger.error("Demo reset failed: %s", e)
        raise HTTPException(status_code=500, detail="Failed to reset demo")
