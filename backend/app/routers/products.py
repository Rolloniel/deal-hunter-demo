from typing import Optional
from fastapi import APIRouter

from app.services.products import get_tracked_items, get_products_by_category
from app.db import get_db

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/tracked")
async def list_tracked():
    """Get all tracked items with product details."""
    items = get_tracked_items()
    return {"tracked_items": items}


@router.get("")
async def list_products(
    category: Optional[str] = None, max_price: Optional[float] = None
):
    """Get products, optionally filtered by category and max price."""
    if category:
        products = get_products_by_category(category, max_price)
    else:
        db = get_db()
        result = db.table("products").select("*").execute()
        products = result.data
    return {"products": products}
