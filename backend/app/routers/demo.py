"""Demo router for reset functionality."""

from fastapi import APIRouter

from app.db import get_db

router = APIRouter(prefix="/api/demo", tags=["demo"])


@router.post("/reset")
async def reset_demo():
    """Reset demo by clearing tracked items and alerts."""
    db = get_db()

    # Delete alerts FIRST (FK child references tracked_items)
    db.table("alerts").delete().neq(
        "tracked_item_id", "00000000-0000-0000-0000-000000000000"
    ).execute()

    # Delete tracked_items SECOND (FK parent)
    db.table("tracked_items").delete().neq(
        "product_id", "00000000-0000-0000-0000-000000000000"
    ).execute()
    # Reset ALL product prices to original values
    # Get all products with original_price set
    products_result = (
        db.table("products")
        .select("id, original_price")
        .not_.is_("original_price", "null")
        .execute()
    )
    for product in products_result.data:
        db.table("products").update({"current_price": product["original_price"]}).eq(
            "id", product["id"]
        ).execute()

    # Clear price history (remove simulated entries)
    db.table("price_history").delete().neq(
        "product_id", "00000000-0000-0000-0000-000000000000"
    ).execute()

    return {"success": True, "message": "Demo reset complete"}
