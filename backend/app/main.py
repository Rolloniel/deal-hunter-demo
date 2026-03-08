from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import sqlalchemy as sa

from app.routers import chat, products, alerts, analytics, demo, auth
from app.config import get_settings
from app.db import engine

settings = get_settings()

app = FastAPI(
    title="DealHunter API",
    description="AI-powered deal tracking assistant",
    version="0.1.0",
)

# Session middleware (required by Authlib OAuth)
app.add_middleware(SessionMiddleware, secret_key=settings.jwt_secret)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://deals.kliuiev.com",
        "https://dealhunter.kliuiev.com",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(products.router)
app.include_router(alerts.router)
app.include_router(analytics.router)
app.include_router(demo.router)


@app.on_event("startup")
async def startup():
    async with engine.connect() as conn:
        await conn.execute(sa.text("SELECT 1"))


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "DealHunter API", "version": "0.1.0"}
