"""Product service for database operations."""

from typing import Optional
from uuid import UUID
from app.db import get_db

# Default email for POC (single user)
DEFAULT_EMAIL = "alerts@kliuiev.com"


def search_products(name: str, limit: int = 5) -> list[dict]:
    """Search products by name (case-insensitive partial match)."""
    db = get_db()
    skip_words = {"inch", "inches", "the", "a", "an", "for", "with"}
    words = [w for w in name.split() if w.lower() not in skip_words]

    if len(words) > 1:
        pattern = "%" + "%".join(words) + "%"
    else:
        pattern = f"%{name}%"

    result = (
        db.table("products").select("*").ilike("name", pattern).limit(limit).execute()
    )

    if not result.data and len(words) > 1:
        for word in words:
            if len(word) > 2:
                result = (
                    db.table("products")
                    .select("*")
                    .ilike("name", f"%{word}%")
                    .limit(limit)
                    .execute()
                )
                if result.data:
                    break

    return result.data


def search_catalog(
    query: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 10,
) -> list[dict]:
    """Search the product catalog by name, category, and/or price range."""
    db = get_db()
    q = db.table("products").select("*")

    if query:
        skip_words = {"inch", "inches", "the", "a", "an", "for", "with"}
        words = [w for w in query.split() if w.lower() not in skip_words]
        if len(words) > 1:
            pattern = "%" + "%".join(words) + "%"
        else:
            pattern = f"%{query}%"
        q = q.ilike("name", pattern)

    if category:
        q = q.ilike("category", f"%{category}%")

    if min_price is not None:
        q = q.gte("current_price", min_price)

    if max_price is not None:
        q = q.lte("current_price", max_price)

    result = q.limit(limit).execute()

    # If name query returned nothing, try word-by-word fallback
    if not result.data and query:
        skip_words = {"inch", "inches", "the", "a", "an", "for", "with"}
        words = [w for w in query.split() if w.lower() not in skip_words]
        for word in words:
            if len(word) > 2:
                q2 = db.table("products").select("*").ilike("name", f"%{word}%")
                if category:
                    q2 = q2.ilike("category", f"%{category}%")
                if min_price is not None:
                    q2 = q2.gte("current_price", min_price)
                if max_price is not None:
                    q2 = q2.lte("current_price", max_price)
                result = q2.limit(limit).execute()
                if result.data:
                    break

    return result.data


def get_product_categories() -> list[str]:
    """Get all distinct product categories."""
    db = get_db()
    result = db.table("products").select("category").execute()
    return sorted({p["category"] for p in result.data})


def get_products_by_category(
    category: str, max_price: Optional[float] = None, limit: int = 10
) -> list[dict]:
    """Get products by category with optional max price filter."""
    db = get_db()
    query = db.table("products").select("*").ilike("category", f"%{category}%")
    if max_price:
        query = query.lte("current_price", max_price)
    result = query.limit(limit).execute()
    return result.data


def create_tracked_item(
    product_id: UUID, target_price: float, user_id: str | None = None
) -> dict:
    """Create a tracked item for a product."""
    db = get_db()
    data = {
        "product_id": str(product_id),
        "target_price": target_price,
    }
    if user_id:
        data["user_id"] = user_id
    result = (
        db.table("tracked_items")
        .insert(data)
        .execute()
    )
    return result.data[0] if result.data else {}


def get_tracked_item_by_product_id(
    product_id: UUID, user_id: str | None = None
) -> Optional[dict]:
    """Check if a product is already being tracked."""
    db = get_db()
    query = (
        db.table("tracked_items")
        .select("*")
        .eq("product_id", str(product_id))
    )
    if user_id:
        query = query.eq("user_id", user_id)
    result = query.limit(1).execute()
    return result.data[0] if result.data else None


def update_tracked_item_target_price(item_id: str, target_price: float) -> dict:
    """Update the target price for an existing tracked item."""
    db = get_db()
    result = (
        db.table("tracked_items")
        .update({"target_price": target_price})
        .eq("id", item_id)
        .execute()
    )
    return result.data[0] if result.data else {}


def get_tracked_items(user_id: str | None = None) -> list[dict]:
    """Get all tracked items with product details."""
    db = get_db()
    query = db.table("tracked_items").select("*, products(*)")
    if user_id:
        query = query.eq("user_id", user_id)
    result = query.execute()
    return result.data


def get_product_by_id(product_id: UUID) -> Optional[dict]:
    """Get a single product by ID."""
    db = get_db()
    result = (
        db.table("products").select("*").eq("id", str(product_id)).single().execute()
    )
    return result.data


def get_price_history(product_id: UUID, limit: int = 90) -> list[dict]:
    """Get price history for a product, ordered by date ascending."""
    db = get_db()
    result = (
        db.table("price_history")
        .select("price, created_at")
        .eq("product_id", str(product_id))
        .order("created_at", desc=False)
        .limit(limit)
        .execute()
    )
    return result.data
