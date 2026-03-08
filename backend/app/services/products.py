"""Product service for database operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.tables import Product, TrackedItem, PriceHistory


async def search_products(session: AsyncSession, name: str, limit: int = 5) -> list[dict]:
    """Search products by name (case-insensitive partial match)."""
    skip_words = {"inch", "inches", "the", "a", "an", "for", "with"}
    words = [w for w in name.split() if w.lower() not in skip_words]

    if len(words) > 1:
        pattern = "%" + "%".join(words) + "%"
    else:
        pattern = f"%{name}%"

    stmt = select(Product).where(Product.name.ilike(pattern)).limit(limit)
    result = await session.execute(stmt)
    rows = result.scalars().all()

    if not rows and len(words) > 1:
        for word in words:
            if len(word) > 2:
                stmt = select(Product).where(Product.name.ilike(f"%{word}%")).limit(limit)
                result = await session.execute(stmt)
                rows = result.scalars().all()
                if rows:
                    break

    return [_product_to_dict(p) for p in rows]


async def search_catalog(
    session: AsyncSession,
    query: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 10,
) -> list[dict]:
    """Search the product catalog by name, category, and/or price range."""
    stmt = select(Product)
    filters = []

    pattern = None
    if query:
        skip_words = {"inch", "inches", "the", "a", "an", "for", "with"}
        words = [w for w in query.split() if w.lower() not in skip_words]
        if len(words) > 1:
            pattern = "%" + "%".join(words) + "%"
        else:
            pattern = f"%{query}%"
        filters.append(Product.name.ilike(pattern))

    if category:
        filters.append(Product.category.ilike(f"%{category}%"))
    if min_price is not None:
        filters.append(Product.current_price >= min_price)
    if max_price is not None:
        filters.append(Product.current_price <= max_price)

    if filters:
        stmt = stmt.where(*filters)
    stmt = stmt.limit(limit)

    result = await session.execute(stmt)
    rows = result.scalars().all()

    # Word-by-word fallback if name query returned nothing
    if not rows and query:
        skip_words = {"inch", "inches", "the", "a", "an", "for", "with"}
        words = [w for w in query.split() if w.lower() not in skip_words]
        for word in words:
            if len(word) > 2:
                fallback_filters = [Product.name.ilike(f"%{word}%")]
                if category:
                    fallback_filters.append(Product.category.ilike(f"%{category}%"))
                if min_price is not None:
                    fallback_filters.append(Product.current_price >= min_price)
                if max_price is not None:
                    fallback_filters.append(Product.current_price <= max_price)
                stmt2 = select(Product).where(*fallback_filters).limit(limit)
                result = await session.execute(stmt2)
                rows = result.scalars().all()
                if rows:
                    break

    return [_product_to_dict(p) for p in rows]


async def get_product_categories(session: AsyncSession) -> list[str]:
    """Get all distinct product categories."""
    stmt = select(Product.category).distinct()
    result = await session.execute(stmt)
    return sorted(row[0] for row in result.all())


async def get_products_by_category(
    session: AsyncSession, category: str, max_price: Optional[float] = None, limit: int = 10
) -> list[dict]:
    """Get products by category with optional max price filter."""
    stmt = select(Product).where(Product.category.ilike(f"%{category}%"))
    if max_price:
        stmt = stmt.where(Product.current_price <= max_price)
    stmt = stmt.limit(limit)
    result = await session.execute(stmt)
    return [_product_to_dict(p) for p in result.scalars().all()]


async def create_tracked_item(
    session: AsyncSession, product_id: UUID, target_price: float, user_id: str
) -> dict:
    """Create a tracked item for a product."""
    item = TrackedItem(product_id=product_id, user_id=user_id, target_price=target_price)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return {"id": str(item.id), "product_id": str(item.product_id), "target_price": item.target_price}


async def get_tracked_item_by_product_id(
    session: AsyncSession, product_id: UUID, user_id: str | None = None
) -> Optional[dict]:
    """Check if a product is already being tracked."""
    stmt = select(TrackedItem).where(TrackedItem.product_id == product_id)
    if user_id:
        stmt = stmt.where(TrackedItem.user_id == user_id)
    stmt = stmt.limit(1)
    result = await session.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        return None
    return {"id": str(item.id), "product_id": str(item.product_id), "target_price": item.target_price}


async def update_tracked_item_target_price(session: AsyncSession, item_id: str, target_price: float) -> dict:
    """Update the target price for an existing tracked item."""
    stmt = update(TrackedItem).where(TrackedItem.id == item_id).values(target_price=target_price)
    await session.execute(stmt)
    await session.commit()
    return {"id": item_id, "target_price": target_price}


async def get_tracked_items(session: AsyncSession, user_id: str | None = None) -> list[dict]:
    """Get all tracked items with product details."""
    stmt = select(TrackedItem).options(selectinload(TrackedItem.product))
    if user_id:
        stmt = stmt.where(TrackedItem.user_id == user_id)
    result = await session.execute(stmt)
    items = result.scalars().all()
    return [
        {
            "id": str(item.id),
            "product_id": str(item.product_id),
            "user_id": str(item.user_id),
            "target_price": item.target_price,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "products": _product_to_dict(item.product) if item.product else None,
        }
        for item in items
    ]


async def get_product_by_id(session: AsyncSession, product_id: UUID) -> Optional[dict]:
    """Get a single product by ID."""
    stmt = select(Product).where(Product.id == product_id)
    result = await session.execute(stmt)
    product = result.scalar_one_or_none()
    return _product_to_dict(product) if product else None


async def get_price_history(session: AsyncSession, product_id: UUID, limit: int = 90) -> list[dict]:
    """Get price history for a product, ordered by date ascending."""
    stmt = (
        select(PriceHistory.price, PriceHistory.created_at)
        .where(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.created_at.asc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return [{"price": row.price, "created_at": row.created_at.isoformat()} for row in result.all()]


def _product_to_dict(p: Product) -> dict:
    """Convert a Product model to dict matching the old Supabase format."""
    return {
        "id": str(p.id),
        "name": p.name,
        "category": p.category,
        "current_price": p.current_price,
        "original_price": p.original_price,
        "image_url": p.image_url,
    }
