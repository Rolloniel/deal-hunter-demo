"""Demo router for reset functionality."""

import logging

from fastapi import APIRouter, HTTPException

from app.db import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/demo", tags=["demo"])


@router.post("/reset")
async def reset_demo():
    """Reset demo by clearing tracked items and alerts."""
    db = get_db()

    try:
        # Delete alerts FIRST (FK child references tracked_items)
        db.table("alerts").delete().neq(
            "tracked_item_id", "00000000-0000-0000-0000-000000000000"
        ).execute()

        # Delete tracked_items SECOND (FK parent)
        db.table("tracked_items").delete().neq(
            "product_id", "00000000-0000-0000-0000-000000000000"
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
