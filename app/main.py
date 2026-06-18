from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.routers.products import router as products_router
from app.routers.competitors import router as competitors_router
from app.routers.urlmap import router as urlmap_router
from app.routers import price_comparison
from app.routers import price_history

from app.database import engine

app = FastAPI(
    title="Price Tracker API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://155.117.46.151:3000",
        "https://price-intel-dashboard.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Price Tracker API Running"}

@app.get("/health")
def health_check():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT DB_NAME()"))
        db_name = result.scalar()

    return {
        "database": db_name,
        "status": "connected"
    }

app.include_router(products_router)
app.include_router(competitors_router)
app.include_router(urlmap_router)
app.include_router(price_comparison.router)
app.include_router(price_history.router)