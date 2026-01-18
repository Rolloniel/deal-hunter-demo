from fastapi import APIRouter

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("")
async def chat():
    return {"message": "Chat endpoint placeholder"}
