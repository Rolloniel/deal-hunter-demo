from fastapi import APIRouter

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("")
async def list_products():
    return {"products": []}


@router.get("/tracked")
async def list_tracked():
    return {"tracked_items": []}
