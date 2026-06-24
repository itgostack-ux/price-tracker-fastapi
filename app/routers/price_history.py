from fastapi import APIRouter
from sqlalchemy import text

from app.database import engine
from app.schemas.price_history import PriceHistorySaveRequest

router = APIRouter(
prefix="/price-history",
tags=["Price History"]
)

@router.post("/save")
def save_price_history(payload: PriceHistorySaveRequest):

    data = payload.model_dump()
    price_id = data.get("PriceID")

    with engine.begin() as conn:

        # ADD
        if not price_id:
    
            conn.execute(
                text("""
                    INSERT INTO PriceHistory
                    (
                        ProductID,
                        PlatformID,
                        VerifiedID,
                        Price,
                        MRP,
                        Discount,
                        CaptureTime,
                        Source
                    )
                    VALUES
                    (
                        :ProductID,
                        :PlatformID,
                        :VerifiedID,
                        :Price,
                        :MRP,
                        :Discount,
                        GETDATE(),
                        :Source
                    )
                """),
                data
            )
    
            return {
                "success": True,
                "message": "Price History Added Successfully"
            }
    
        # DELETE
        elif data.get("IsDeleted") == 1:
    
            conn.execute(
                text("""
                    DELETE FROM PriceHistory
                    WHERE PriceID = :PriceID
                """),
                {"PriceID": price_id}
            )
    
            return {
                "success": True,
                "message": "Price History Deleted Successfully"
            }
    
        # UPDATE
        else:
    
            conn.execute(
                text("""
                    UPDATE PriceHistory
                    SET
                        ProductID = :ProductID,
                        PlatformID = :PlatformID,
                        VerifiedID = :VerifiedID,
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
                "message": "Price History Updated Successfully"
            }
@router.get("/product/{product_id}")
def get_product_price_history(product_id: int):


   with engine.connect() as conn:

    result = conn.execute(
        text("""
            SELECT
                pm.ProductID,
                pm.ItemCode,
                pm.ItemName,
                pl.PlatformCode,
                pl.PlatformName,
                ph.PriceID,
                ph.Price,
                ph.MRP,
                ph.Discount,
                ph.CaptureTime,
                pp.ProductURL
            FROM PriceHistory ph
            INNER JOIN ProductMaster pm
                ON pm.ProductID = ph.ProductID
            INNER JOIN PlatformMaster pl
                ON pl.PlatformID = ph.PlatformID
            LEFT JOIN ProductPlatform pp
                ON pp.ProductID = ph.ProductID
                AND pp.PlatformID = ph.PlatformID
            WHERE ph.ProductID = :ProductID
            ORDER BY pl.PlatformCode, ph.CaptureTime DESC
        """),
        {"ProductID": product_id}
    )

    rows = [dict(row._mapping) for row in result]

    if not rows:
        return {
            "success": False,
            "message": "No Price History Found"
        }

    response = {
        "ProductID": rows[0]["ProductID"],
        "ItemCode": rows[0]["ItemCode"],
        "ItemName": rows[0]["ItemName"],
        "Platforms": {}
    }

    for row in rows:

        platform = row["PlatformCode"]

        if platform not in response["Platforms"]:
            response["Platforms"][platform] = {
                "PlatformName": row["PlatformName"],
                "ProductURL": row["ProductURL"],
                "PriceHistory": []
            }

        response["Platforms"][platform]["PriceHistory"].append({
            "PriceID": row["PriceID"],
            "Price": row["Price"],
            "MRP": row["MRP"],
            "Discount": row["Discount"],
            "CaptureTime": str(row["CaptureTime"])
        })

    return response
