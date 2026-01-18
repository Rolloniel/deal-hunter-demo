from fastapi import APIRouter

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.post("/simulate")
async def simulate_price_drop():
    return {"message": "Simulate endpoint placeholder"}
