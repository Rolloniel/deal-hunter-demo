from typing import Optional
from fastapi import APIRouter, HTTPException

from app.services.products import get_tracked_items, get_products_by_category
from app.db import get_db

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/tracked")
async def list_tracked():
    try:
        items = get_tracked_items()
        return {"tracked_items": items}
    except Exception as e:
        error_msg = str(e)
        if "Invalid API key" in error_msg or "401" in error_msg:
            raise HTTPException(
                status_code=503,
                detail="Database connection unavailable. Please check Supabase credentials.",
            )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_products(
    category: Optional[str] = None, max_price: Optional[float] = None
):
    try:
        if category:
            products = get_products_by_category(category, max_price)
        else:
            db = get_db()
            result = db.table("products").select("*").execute()
            products = result.data
        return {"products": products}
    except Exception as e:
        error_msg = str(e)
        if "Invalid API key" in error_msg or "401" in error_msg:
            raise HTTPException(
                status_code=503,
                detail="Database connection unavailable. Please check Supabase credentials.",
            )
        raise HTTPException(status_code=500, detail=str(e))
