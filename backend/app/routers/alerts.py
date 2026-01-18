"""Alerts router with simulate functionality."""

import random
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.db import get_db
from app.models.schemas import SimulateRequest
from app.services.email import send_price_alert
from app.services.products import get_tracked_items

router = APIRouter(prefix="/api/alerts", tags=["alerts"])
settings = get_settings()


@router.post("/simulate")
async def simulate_price_drop(request: Optional[SimulateRequest] = None):
    """
    Simulate a price drop for demo purposes.
    Updates the first tracked item's product price to below target.
    Sends email alert to configured demo email.
    """
    db = get_db()

    # Get tracked items
    items = get_tracked_items()

    if not items:
        raise HTTPException(
            status_code=404, detail="No tracked items found. Track a product first!"
        )

    # Use specified item or first one
    item = None
    if request and request.item_id:
        item = next((i for i in items if i["id"] == str(request.item_id)), None)
    if not item:
        item = items[0]

    product = item.get("products", {})
    product_id = item["product_id"]
    target_price = item["target_price"]
    old_price = product.get("current_price", target_price + 100)

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

    # Send email alert
    email_sent = False
    email_error = None
    try:
        email_sent = await send_price_alert(
            to_email=settings.demo_alert_email,
            product_name=product.get("name", "Unknown Product"),
            old_price=old_price,
            new_price=new_price,
            target_price=target_price,
            product_url="#",  # No real URL for POC
        )
    except Exception as e:
        email_error = str(e)
        print(f"Email send failed: {e}")

    # Create alert record
    db.table("alerts").insert(
        {
            "tracked_item_id": item["id"],
            "old_price": old_price,
            "new_price": new_price,
            "email_sent": email_sent,
        }
    ).execute()

    return {
        "success": True,
        "message": f"Price dropped to ${new_price:.2f}!",
        "product_name": product.get("name", "Unknown Product"),
        "product_id": product_id,
        "old_price": old_price,
        "new_price": new_price,
        "target_price": target_price,
        "email_sent": email_sent,
        "email_recipient": settings.demo_alert_email if email_sent else None,
        "email_error": email_error,
    }
