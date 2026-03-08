from typing import Optional
from fastapi import APIRouter, HTTPException

from app.services.products import (
    get_tracked_items,
    get_products_by_category,
    get_price_history,
    search_catalog,
    get_product_categories,
)
from app.db import get_db

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/search")
async def search_products_endpoint(
    q: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 10,
):
    """Search products by name, category, and/or price range."""
    try:
        products = search_catalog(
            query=q,
            category=category,
            min_price=min_price,
            max_price=max_price,
            limit=min(limit, 50),
        )
        return {"products": products, "count": len(products)}
    except Exception as e:
        error_msg = str(e)
        if "Invalid API key" in error_msg or "401" in error_msg:
            raise HTTPException(
                status_code=503,
                detail="Database connection unavailable. Please check Supabase credentials.",
            )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def list_categories():
    """Get all available product categories."""
    try:
        categories = get_product_categories()
        return {"categories": categories}
    except Exception as e:
        error_msg = str(e)
        if "Invalid API key" in error_msg or "401" in error_msg:
            raise HTTPException(
                status_code=503,
                detail="Database connection unavailable. Please check Supabase credentials.",
            )
        raise HTTPException(status_code=500, detail=str(e))


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


@router.get("/{product_id}/price-history")
async def product_price_history(product_id: str):
    try:
        history = get_price_history(product_id)
        return {"price_history": history}
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
