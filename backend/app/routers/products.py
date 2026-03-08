from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_session
from app.services.products import (
    get_tracked_items,
    get_products_by_category,
    get_price_history,
    search_catalog,
    get_product_categories,
)

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/search")
async def search_products_endpoint(
    q: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
):
    try:
        products = await search_catalog(
            session, query=q, category=category,
            min_price=min_price, max_price=max_price, limit=min(limit, 50),
        )
        return {"products": products, "count": len(products)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def list_categories(session: AsyncSession = Depends(get_session)):
    try:
        categories = await get_product_categories(session)
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tracked")
async def list_tracked(
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        items = await get_tracked_items(session, user_id=str(user.id))
        return {"tracked_items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_id}/price-history")
async def product_price_history(
    product_id: str,
    session: AsyncSession = Depends(get_session),
):
    try:
        history = await get_price_history(session, product_id)
        return {"price_history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_products(
    category: Optional[str] = None,
    max_price: Optional[float] = None,
    session: AsyncSession = Depends(get_session),
):
    try:
        if category:
            products = await get_products_by_category(session, category, max_price)
        else:
            from app.services.products import search_catalog
            products = await search_catalog(session)
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
