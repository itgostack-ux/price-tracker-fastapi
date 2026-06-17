from fastapi import APIRouter
from sqlalchemy import text

from app.database import engine
from app.schemas.product_platform import ProductPlatformSaveRequest

router = APIRouter(
    prefix="/product-platform",
    tags=["Product Platform"]
)


# =====================================================
# GET ALL
# =====================================================
@router.get("/")
def get_product_platforms():

    with engine.connect() as conn:

        result = conn.execute(text("""
            SELECT
                PP.ProductPlatformID,

                PM.ProductID,
                PM.ItemCode,
                PM.ItemName,

                PL.PlatformID,
                PL.PlatformCode,
                PL.PlatformName,

                PP.ProductURL,
                PP.LastVerified,
                PP.IsActive,
                PP.URLStatus,
                PP.MatchScore,
                PP.MatchMethod,
                PP.VerificationStatus

            FROM ProductPlatform PP
            INNER JOIN ProductMaster PM
                ON PM.ProductID = PP.ProductID
            INNER JOIN PlatformMaster PL
                ON PL.PlatformID = PP.PlatformID

            ORDER BY PP.ProductPlatformID DESC
        """))

        return [dict(row._mapping) for row in result]


# =====================================================
# GET BY ID
# =====================================================
@router.get("/{product_platform_id}")
def get_product_platform(product_platform_id: int):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    PP.ProductPlatformID,

                    PM.ProductID,
                    PM.ItemCode,
                    PM.ItemName,

                    PL.PlatformID,
                    PL.PlatformCode,
                    PL.PlatformName,

                    PP.ProductURL,
                    PP.LastVerified,
                    PP.IsActive,
                    PP.URLStatus,
                    PP.MatchScore,
                    PP.MatchMethod,
                    PP.VerificationStatus

                FROM ProductPlatform PP
                INNER JOIN ProductMaster PM
                    ON PM.ProductID = PP.ProductID
                INNER JOIN PlatformMaster PL
                    ON PL.PlatformID = PP.PlatformID

                WHERE PP.ProductPlatformID = :ProductPlatformID
            """),
            {"ProductPlatformID": product_platform_id}
        )

        row = result.mappings().first()

        if not row:
            return {
                "success": False,
                "message": "Product Platform Not Found"
            }

        return dict(row)


# =====================================================
# ADD / UPDATE / DISABLE
# =====================================================
@router.post("/save")
def save_product_platform(payload: ProductPlatformSaveRequest):

    data = payload.model_dump()

    product_platform_id = data.get("ProductPlatformID")

    with engine.begin() as conn:

        # ---------------------------------------------
        # ADD
        # ---------------------------------------------
        if not product_platform_id:

            conn.execute(
                text("""
                    INSERT INTO ProductPlatform
                    (
                        ProductID,
                        PlatformID,
                        ProductURL,
                        LastVerified,
                        IsActive,
                        URLStatus,
                        MatchScore,
                        MatchMethod,
                        VerificationStatus
                    )
                    VALUES
                    (
                        :ProductID,
                        :PlatformID,
                        :ProductURL,
                        GETDATE(),
                        1,
                        :URLStatus,
                        :MatchScore,
                        :MatchMethod,
                        :VerificationStatus
                    )
                """),
                data
            )

            return {
                "success": True,
                "message": "Product Platform Added Successfully"
            }

        # ---------------------------------------------
        # DISABLE
        # ---------------------------------------------
        if data.get("IsActive") == 0:

            conn.execute(
                text("""
                    UPDATE ProductPlatform
                    SET
                        IsActive = 0
                    WHERE ProductPlatformID = :ProductPlatformID
                """),
                {"ProductPlatformID": product_platform_id}
            )

            return {
                "success": True,
                "message": "Product Platform Disabled Successfully"
            }

        # ---------------------------------------------
        # UPDATE
        # ---------------------------------------------
        conn.execute(
            text("""
                UPDATE ProductPlatform
                SET
                    ProductID = :ProductID,
                    PlatformID = :PlatformID,
                    ProductURL = :ProductURL,
                    LastVerified = GETDATE(),
                    URLStatus = :URLStatus,
                    MatchScore = :MatchScore,
                    MatchMethod = :MatchMethod,
                    VerificationStatus = :VerificationStatus,
                    IsActive = :IsActive
                WHERE ProductPlatformID = :ProductPlatformID
            """),
            data
        )

        return {
            "success": True,
            "message": "Product Platform Updated Successfully"
        }


# =====================================================
# ACTIVE RECORDS ONLY
# =====================================================
@router.get("/active/list")
def get_active_product_platforms():

    with engine.connect() as conn:

        result = conn.execute(text("""
            SELECT
                PP.ProductPlatformID,

                PM.ProductID,
                PM.ItemCode,
                PM.ItemName,

                PL.PlatformID,
                PL.PlatformCode,
                PL.PlatformName,

                PP.ProductURL,
                PP.LastVerified,
                PP.URLStatus,
                PP.MatchScore,
                PP.MatchMethod,
                PP.VerificationStatus

            FROM ProductPlatform PP
            INNER JOIN ProductMaster PM
                ON PM.ProductID = PP.ProductID
            INNER JOIN PlatformMaster PL
                ON PL.PlatformID = PP.PlatformID

            WHERE
                PP.IsActive = 1
                AND PL.IsEnabled = 1

            ORDER BY
                PM.ItemCode,
                PL.PlatformName
        """))

        return [dict(row._mapping) for row in result]
