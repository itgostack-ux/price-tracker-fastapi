from fastapi import APIRouter
from sqlalchemy import text
from app.database import engine

router = APIRouter(
    prefix="/price-comparison",
    tags=["Price Comparison"]
)

@router.get("/")
def get_price_comparison():
    with engine.connect() as conn:
        result = conn.execute(
            text("EXEC dbo.usp_CompetitorPriceComparison")
        )

        columns = result.keys()
        data = [dict(zip(columns, row)) for row in result.fetchall()]

    return {
        "success": True,
        "count": len(data),
        "data": data
    }