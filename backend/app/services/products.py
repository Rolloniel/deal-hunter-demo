"""Product service for database operations."""

from typing import Optional
from uuid import UUID
from app.db import get_db

# Default email for POC (single user)
DEFAULT_EMAIL = "alerts@kliuiev.com"


def search_products(name: str, limit: int = 5) -> list[dict]:
    """Search products by name (case-insensitive partial match)."""
    db = get_db()
    result = (
        db.table("products")
        .select("*")
        .ilike("name", f"%{name}%")
        .limit(limit)
        .execute()
    )
    return result.data


def get_products_by_category(
    category: str, max_price: Optional[float] = None, limit: int = 5
) -> list[dict]:
    """Get products by category with optional max price filter."""
    db = get_db()
    query = db.table("products").select("*").ilike("category", f"%{category}%")
    if max_price:
        query = query.lte("current_price", max_price)
    result = query.limit(limit).execute()
    return result.data


def create_tracked_item(
    product_id: UUID, target_price: float, email: str = DEFAULT_EMAIL
) -> dict:
    """Create a tracked item for a product."""
    db = get_db()
    result = (
        db.table("tracked_items")
        .insert(
            {
                "product_id": str(product_id),
                "target_price": target_price,
                "email": email,
            }
        )
        .execute()
    )
    return result.data[0] if result.data else {}


def get_tracked_items(email: str = DEFAULT_EMAIL) -> list[dict]:
    """Get all tracked items for an email with product details."""
    db = get_db()
    # Join tracked_items with products
    result = (
        db.table("tracked_items").select("*, products(*)").eq("email", email).execute()
    )
    return result.data


def get_product_by_id(product_id: UUID) -> Optional[dict]:
    """Get a single product by ID."""
    db = get_db()
    result = (
        db.table("products").select("*").eq("id", str(product_id)).single().execute()
    )
    return result.data
