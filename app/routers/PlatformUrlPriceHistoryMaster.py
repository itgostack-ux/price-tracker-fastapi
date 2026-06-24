from fastapi import APIRouter
from sqlalchemy import text

from app.database import engine
from app.schemas.PlatformUrlPriceHistoryMaster import PlatformURLPriceHistorySaveRequest

router = APIRouter(
    prefix="/platform-price-history",
    tags=["Platform Price History"]
)


@router.get("/{price_id}")
def get_price(price_id: int):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT *
                FROM PlatformUrlPriceHistoryMaster
                WHERE PriceID = :PriceID
            """),
            {"PriceID": price_id}
        )

        row = result.mappings().first()

        if not row:
            return {
                "success": False,
                "message": "Price History Not Found"
            }

        return dict(row)


@router.post("/save")
def save_price(payload: PlatformURLPriceHistorySaveRequest):

    data = payload.model_dump()

    price_id = data.get("PriceID")

    with engine.begin() as conn:

        # ADD
        if not price_id:

            duplicate = conn.execute(
                text("""
                    SELECT TOP 1 PriceID
                    FROM PlatformUrlPriceHistoryMaster
                    WHERE ProductPlatformID = :ProductPlatformID
                      AND Price = :Price
                      AND ISNULL(MRP,0) = ISNULL(:MRP,0)
                      AND ISNULL(Discount,0) = ISNULL(:Discount,0)
                """),
                data
            ).fetchone()

            if duplicate:
                return {
                    "success": False,
                    "message": "Duplicate Price Record Already Exists"
                }

            result = conn.execute(
                text("""
                    INSERT INTO PlatformUrlPriceHistoryMaster
                    (
                        ProductPlatformID,
                        Price,
                        MRP,
                        Discount,
                        CaptureTime,
                        Source
                    )
                    OUTPUT INSERTED.PriceID
                    VALUES
                    (
                        :ProductPlatformID,
                        :Price,
                        :MRP,
                        :Discount,
                        GETDATE(),
                        :Source
                    )
                """),
                data
            )

            new_id = result.scalar()

            return {
                "success": True,
                "PriceID": new_id,
                "message": "Price Added Successfully"
            }

        # UPDATE DUPLICATE CHECK
        duplicate = conn.execute(
            text("""
                SELECT TOP 1 PriceID
                FROM PlatformUrlPriceHistoryMaster
                WHERE ProductPlatformID = :ProductPlatformID
                  AND Price = :Price
                  AND ISNULL(MRP,0) = ISNULL(:MRP,0)
                  AND ISNULL(Discount,0) = ISNULL(:Discount,0)
                  AND PriceID <> :PriceID
            """),
            data
        ).fetchone()

        if duplicate:
            return {
                "success": False,
                "message": "Duplicate Price Record Already Exists"
            }

        # UPDATE
        conn.execute(
            text("""
                UPDATE PlatformUrlPriceHistoryMaster
                SET
                    ProductPlatformID = :ProductPlatformID,
                    Price = :Price,
                    MRP = :MRP,
                    Discount = :Discount,
                    Source = :Source
                WHERE PriceID = :PriceID
            """),
            data
        )

        return {
            "success": True,
            "message": "Price Updated Successfully"
        }

@router.get("/product/{product_id}")
def get_price_by_product(product_id: int):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    PM.ProductID,
                    PH.ProductPlatformID,
                    PM.ItemName,
                    PL.PlatformID,
                    PL.PlatformName,
                    PPU.ProductURL,
                    PH.Price
                FROM PlatformUrlPriceHistoryMaster PH
                INNER JOIN ProductPlatformURLMaster PPU
                    ON PH.ProductPlatformID = PPU.ProductPlatformID
                INNER JOIN ProductMaster PM
                    ON PPU.ProductID = PM.ProductID
                INNER JOIN PlatformMaster PL
                    ON PPU.PlatformID = PL.PlatformID
                WHERE PM.ProductID = :ProductID
                ORDER BY PH.CaptureTime DESC
            """),
            {"ProductID": product_id}
        )

        return [dict(row._mapping) for row in result]
