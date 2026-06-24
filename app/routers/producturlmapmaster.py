from fastapi import APIRouter
from sqlalchemy import text

from app.database import engine
from app.schemas.producturlmapmaster import ProductPlatformURLSaveRequest

router = APIRouter(
    prefix="/product-platform-url",
    tags=["Product Platform URL"]
)

@router.get("/product/{product_id}")
def get_product_urls(product_id: int):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    PM.ProductID,
                    PM.ItemName,
                    PM.Brand,
                    PM.ModelName,
                    PPU.ProductPlatformID,
                    PL.PlatformID,
                    PL.PlatformName,
                    PPU.ProductURL
                FROM ProductPlatformURLMaster PPU
                INNER JOIN ProductMaster PM
                    ON PPU.ProductID = PM.ProductID
                INNER JOIN PlatformMaster PL
                    ON PPU.PlatformID = PL.PlatformID
                WHERE PM.ProductID = :ProductID
                ORDER BY PL.PlatformName
            """),
            {"ProductID": product_id}
        )

        rows = [dict(row._mapping) for row in result]

        if not rows:
            return {
                "success": False,
                "message": "No Platform URLs Found"
            }

        return {
            "success": True,
            "ProductID": rows[0]["ProductID"],
            "ItemName": rows[0]["ItemName"],
            "Brand": rows[0]["Brand"],
            "ModelName": rows[0]["ModelName"],
            "Platforms": [
                {
                    "ProductPlatformID": row["ProductPlatformID"],
                    "PlatformID": row["PlatformID"],
                    "PlatformName": row["PlatformName"],
                    "ProductURL": row["ProductURL"]
                }
                for row in rows
            ]
        }
@router.post("/save")
def save_product_platform_url(payload: ProductPlatformURLSaveRequest):

    data = payload.model_dump()

    product_platform_id = data.get("ProductPlatformID")

    with engine.begin() as conn:

        # ADD
        if not product_platform_id:

            duplicate = conn.execute(
                text("""
                    SELECT ProductPlatformID
                    FROM ProductPlatformURLMaster
                    WHERE ProductID = :ProductID
                      AND PlatformID = :PlatformID
                      AND IsActive = 1
                """),
                data
            ).fetchone()

            if duplicate:
                return {
                    "success": False,
                    "message": "Product URL already exists for this Platform"
                }

            result = conn.execute(
                text("""
                    INSERT INTO ProductPlatformURLMaster
                    (
                        ProductID,
                        PlatformID,
                        ProductURL,
                        IsActive
                    )
                    OUTPUT INSERTED.ProductPlatformID
                    VALUES
                    (
                        :ProductID,
                        :PlatformID,
                        :ProductURL,
                        1
                    )
                """),
                data
            )

            new_id = result.scalar()

            return {
                "success": True,
                "ProductPlatformID": new_id,
                "message": "Product Platform URL Added Successfully"
            }

        # DISABLE
        if data.get("IsActive") == 0:

            conn.execute(
                text("""
                    UPDATE ProductPlatformURLMaster
                    SET IsActive = 0
                    WHERE ProductPlatformID = :ProductPlatformID
                """),
                {"ProductPlatformID": product_platform_id}
            )

            return {
                "success": True,
                "message": "Product Platform URL Disabled Successfully"
            }

        # UPDATE DUPLICATE CHECK
        duplicate = conn.execute(
            text("""
                SELECT ProductPlatformID
                FROM ProductPlatformURLMaster
                WHERE ProductID = :ProductID
                  AND PlatformID = :PlatformID
                  AND ProductPlatformID <> :ProductPlatformID
                  AND IsActive = 1
            """),
            data
        ).fetchone()

        if duplicate:
            return {
                "success": False,
                "message": "Product URL already exists for this Platform"
            }

        # UPDATE
        conn.execute(
            text("""
                UPDATE ProductPlatformURLMaster
                SET
                    ProductID = :ProductID,
                    PlatformID = :PlatformID,
                    ProductURL = :ProductURL,
                    IsActive = :IsActive
                WHERE ProductPlatformID = :ProductPlatformID
            """),
            data
        )

        return {
            "success": True,
            "message": "Product Platform URL Updated Successfully"
        }
