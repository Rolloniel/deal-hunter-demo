"""Demo router for reset functionality."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_current_user
from app.db import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/demo", tags=["demo"])


@router.post("/reset")
async def reset_demo(user=Depends(get_current_user)):
    """Reset demo by clearing this user's tracked items and alerts."""
    db = get_db()

    try:
        # Get this user's tracked item IDs
        user_items = (
            db.table("tracked_items")
            .select("id")
            .eq("user_id", user.id)
            .execute()
        )
        user_item_ids = [item["id"] for item in (user_items.data or [])]

        if user_item_ids:
            # Delete alerts for this user's tracked items
            for item_id in user_item_ids:
                db.table("alerts").delete().eq(
                    "tracked_item_id", item_id
                ).execute()

            # Delete this user's tracked items
            db.table("tracked_items").delete().eq(
                "user_id", user.id
            ).execute()

        # Reset ALL product prices to original values
        products_result = (
            db.table("products")
            .select("id, original_price")
            .not_.is_("original_price", "null")
            .execute()
        )
        for product in products_result.data:
            db.table("products").update(
                {"current_price": product["original_price"]}
            ).eq("id", product["id"]).execute()

        # Clear price history
        db.table("price_history").delete().neq(
            "product_id", "00000000-0000-0000-0000-000000000000"
        ).execute()

        return {"success": True, "message": "Demo reset complete"}

    except Exception as e:
        logger.error("Demo reset failed: %s", e)
        raise HTTPException(status_code=500, detail="Failed to reset demo")
