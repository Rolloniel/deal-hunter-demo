"""Alerts router with simulate functionality."""

import logging
import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user
from app.config import get_settings
from app.db import get_session
from app.models.schemas import SimulateRequest
from app.models.tables import Alert, TrackedItem, Product, PriceHistory
from app.services.email import send_price_alert
from app.services.products import get_tracked_items

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/alerts", tags=["alerts"])
settings = get_settings()


@router.post("/simulate")
async def simulate_price_drop(
    request: SimulateRequest | None = None,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Simulate a price drop for demo purposes."""
    items = await get_tracked_items(session, user_id=user.id)

    if not items:
        raise HTTPException(status_code=404, detail="No tracked items found. Track a product first!")

    item = None
    if request and request.item_id:
        item = next((i for i in items if i["id"] == str(request.item_id)), None)
    if not item:
        item = items[0]

    product = item.get("products", {})
    product_id = item.get("product_id")
    target_price = item.get("target_price")

    if not product_id or target_price is None:
        raise HTTPException(status_code=400, detail="Invalid tracked item data")

    old_price = product.get("current_price", target_price + 100)
    recipient_email = request.email if request and request.email else settings.demo_alert_email

    price_drop = random.uniform(10, 50)
    new_price = target_price - price_drop

    # Update product price
    await session.execute(
        update(Product).where(Product.id == product_id).values(current_price=new_price)
    )

    # Add to price history
    session.add(PriceHistory(product_id=product_id, price=new_price))

    # Send email alert
    email_sent = False
    email_error = None
    try:
        email_sent = await send_price_alert(
            to_email=recipient_email,
            product_name=product.get("name", "Unknown Product"),
            old_price=old_price, new_price=new_price, target_price=target_price,
        )
    except Exception as e:
        email_error = str(e)
        logger.error("Email send failed: %s", e)

    # Create alert record
    session.add(Alert(
        tracked_item_id=item["id"], old_price=old_price,
        new_price=new_price, email_sent=email_sent,
    ))
    await session.commit()

    return {
        "success": True,
        "message": f"Price dropped to ${new_price:.2f}!",
        "product_name": product.get("name", "Unknown Product"),
        "product_id": product_id,
        "old_price": old_price, "new_price": new_price,
        "target_price": target_price,
        "email_sent": email_sent,
        "email_recipient": recipient_email,
        "email_error": email_error,
    }


@router.get("")
async def get_alerts(
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Get all triggered alerts with product names for current user."""
    try:
        stmt = (
            select(Alert)
            .join(TrackedItem)
            .join(Product, TrackedItem.product_id == Product.id)
            .where(TrackedItem.user_id == user.id)
            .options(selectinload(Alert.tracked_item).selectinload(TrackedItem.product))
            .order_by(Alert.created_at.desc())
        )
        result = await session.execute(stmt)
        alerts_list = result.scalars().all()

        alerts = []
        for alert in alerts_list:
            product_name = "Unknown Product"
            if alert.tracked_item and alert.tracked_item.product:
                product_name = alert.tracked_item.product.name

            alerts.append({
                "id": str(alert.id),
                "product_name": product_name,
                "old_price": alert.old_price,
                "new_price": alert.new_price,
                "email_sent": alert.email_sent,
                "created_at": alert.created_at.isoformat() if alert.created_at else None,
            })

        return {"alerts": alerts}
    except Exception as e:
        logger.error("Error fetching alerts: %s", e)
        return {"alerts": []}
