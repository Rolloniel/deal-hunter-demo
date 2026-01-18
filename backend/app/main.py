from fastapi import FastAPI

app = FastAPI(title="DealHunter API")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "DealHunter API", "status": "ok"}
