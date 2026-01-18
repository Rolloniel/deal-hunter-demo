"""Alerts router with simulate functionality."""

import random
from fastapi import APIRouter, HTTPException
from app.db import get_db
from app.services.products import get_tracked_items
from app.models.schemas import SimulateRequest
from typing import Optional

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.post("/simulate")
async def simulate_price_drop(request: Optional[SimulateRequest] = None):
    """
    Simulate a price drop for demo purposes.
    Updates the first tracked item's product price to below target.
    """
    db = get_db()

    # Get tracked items
    items = get_tracked_items()

    if not items:
        raise HTTPException(status_code=404, detail="No tracked items found")

    # Use specified item or first one
    item = None
    if request and request.item_id:
        item = next((i for i in items if i["id"] == str(request.item_id)), None)
    if not item:
        item = items[0]

    product_id = item["product_id"]
    target_price = item["target_price"]

    # Calculate new price (10-50 below target)
    price_drop = random.uniform(10, 50)
    new_price = target_price - price_drop

    # Update product price
    db.table("products").update({"current_price": new_price}).eq(
        "id", product_id
    ).execute()

    # Add to price history
    db.table("price_history").insert(
        {"product_id": product_id, "price": new_price}
    ).execute()

    # Create alert record
    db.table("alerts").insert(
        {
            "tracked_item_id": item["id"],
            "email_sent": False,  # Will be true after email integration
        }
    ).execute()

    return {
        "success": True,
        "message": f"Price dropped to ${new_price:.2f}!",
        "product_id": product_id,
        "old_price": item["products"]["current_price"],
        "new_price": new_price,
        "target_price": target_price,
    }
