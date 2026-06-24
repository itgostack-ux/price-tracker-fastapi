from fastapi import APIRouter
from sqlalchemy import text

from app.database import engine
from app.schemas.product import ProductSaveRequest

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.get("/")
def get_products():

    with engine.connect() as conn:

        result = conn.execute(text("""
            SELECT
                ProductID,
                ItemCode,
                Brand,
                ModelName,
                RAM,
                StorageSize,
                ColorName,
                VariantName,
                ItemName,
                Category,
                SubCategory,
                IsActive,
                CreatedOn
            FROM ProductMaster
            ORDER BY ProductID DESC
        """))

        return [dict(row._mapping) for row in result]


@router.get("/{product_id}")
def get_product(product_id: int):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT *
                FROM ProductMaster
                WHERE ProductID = :ProductID
            """),
            {"ProductID": product_id}
        )

        row = result.mappings().first()

        if not row:
            return {
                "success": False,
                "message": "Product Not Found"
            }

        return dict(row)


@router.post("/save")
def save_product(payload: ProductSaveRequest):

    data = payload.model_dump()

    product_id = data.get("ProductID")

    with engine.begin() as conn:

        # ADD
        if not product_id:

            conn.execute(
                text("""
                    INSERT INTO ProductMaster
                    (
                        ItemCode,
                        Brand,
                        ModelName,
                        RAM,
                        StorageSize,
                        ColorName,
                        VariantName,
                        ItemName,
                        Category,
                        SubCategory,
                        IsActive
                    )
                    VALUES
                    (
                        :ItemCode,
                        :Brand,
                        :ModelName,
                        :RAM,
                        :StorageSize,
                        :ColorName,
                        :VariantName,
                        :ItemName,
                        :Category,
                        :SubCategory,
                        1
                    )
                """),
                data
            )

            return {
                "success": True,
                "message": "Product Added Successfully"
            }

        # DISABLE
        if data.get("IsActive") == 0:

            conn.execute(
                text("""
                    UPDATE ProductMaster
                    SET IsActive = 0
                    WHERE ProductID = :ProductID
                """),
                {"ProductID": product_id}
            )

            return {
                "success": True,
                "message": "Product Disabled Successfully"
            }

        # UPDATE
        conn.execute(
            text("""
                UPDATE ProductMaster
                SET
                    ItemCode = :ItemCode,
                    Brand = :Brand,
                    ModelName = :ModelName,
                    RAM = :RAM,
                    StorageSize = :StorageSize,
                    ColorName = :ColorName,
                    VariantName = :VariantName,
                    ItemName = :ItemName,
                    Category = :Category,
                    SubCategory = :SubCategory,
                   IsActive = :IsActive
                WHERE ProductID = :ProductID
            """),
            data
        )

        return {
            "success": True,
            "message": "Product Updated Successfully"
        }