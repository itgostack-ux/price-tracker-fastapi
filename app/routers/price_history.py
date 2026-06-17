from fastapi import APIRouter
from sqlalchemy import text

from app.database import engine
from app.schemas.price_history import PriceHistorySaveRequest

router = APIRouter(
    prefix="/price-history",
    tags=["Price History"]
)


@router.post("/save")
def save_price(payload: PriceHistorySaveRequest):

    data = payload.model_dump()

    with engine.begin() as conn:

        conn.execute(
            text("""
                INSERT INTO CompetitorPriceHistory
                (
                    UrlMapID,
                    Competitor_Price,
                    MRP,
                    CheckedOn
                )
                VALUES
                (
                    :UrlMapID,
                    :Competitor_Price,
                    :MRP,
                    GETDATE()
                )
            """),
            data
        )

    return {
        "success": True,
        "message": "Price Saved Successfully"
    }


@router.get("/")
def get_price_history():

    with engine.connect() as conn:

        result = conn.execute(text("""
            SELECT
                PH.PriceHistoryID,
                PM.ItemCode,
                PM.ItemName,
                C.CompetitorName,
                PH.Competitor_Price,
                PH.MRP,
                PH.CheckedOn
            FROM CompetitorPriceHistory PH
            INNER JOIN CompetitorUrlMap UM
                ON UM.UrlMapID = PH.UrlMapID
            INNER JOIN ProductMaster PM
                ON PM.ProductID = UM.ProductID
            INNER JOIN Competitors C
                ON C.CompetitorID = UM.CompetitorID
            ORDER BY PH.PriceHistoryID DESC
        """))

        return [dict(row._mapping) for row in result]