from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import chat, products, alerts
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="DealHunter API",
    description="AI-powered deal tracking assistant",
    version="0.1.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dealhunter.kliuiev.com",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(products.router)
app.include_router(alerts.router)


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "DealHunter API", "version": "0.1.0"}
