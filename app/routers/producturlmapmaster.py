from fastapi import APIRouter
from sqlalchemy import text

from app.database import engine
from app.schemas.producturlmapmaster import ProductPlatformURLSaveRequest

router = APIRouter(
    prefix="/product-platform-url",
    tags=["Product Platform URL"]
)

@router.get("/{product_platform_id}")
def get_product_platform_url(product_platform_id: int):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    ProductPlatformID,
                    ProductID,
                    PlatformID,
                    ProductURL,
                    IsActive,
                    CreatedOn
                FROM ProductPlatformURLMaster
                WHERE ProductPlatformID = :ProductPlatformID
            """),
            {"ProductPlatformID": product_platform_id}
        )

        row = result.mappings().first()

        if not row:
            return {
                "success": False,
                "message": "Product Platform URL Not Found"
            }

        return dict(row)

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
