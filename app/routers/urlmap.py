from fastapi import APIRouter
from sqlalchemy import text

from app.database import engine
from app.schemas.product_platform import ProductURLUpdateRequest

router = APIRouter(
    prefix="/urlmap",
    tags=["URL Map"]
)


@router.post("/update-url")
def update_url(payload: ProductURLUpdateRequest):

    data = payload.model_dump()

    with engine.begin() as conn:

        result = conn.execute(
            text("""
                UPDATE ProductPlatform
                SET
                    ProductURL = :ProductURL,
                    LastVerified = GETDATE()
                WHERE ProductPlatformID = :ProductPlatformID
                  AND ProductID = :ProductID
                  AND PlatformID = :PlatformID
            """),
            data
        )

        if result.rowcount == 0:
            return {
                "success": False,
                "message": "Record Not Found"
            }

        return {
            "success": True,
            "message": "URL Updated Successfully"
        }

@router.get("/{product_id}/{platform_id}")
def get_url(product_id: int, platform_id: int):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    ProductPlatformID,
                    ProductID,
                    PlatformID,
                    ProductURL,
                    LastVerified,
                    IsActive,
                    URLStatus,
                    MatchScore,
                    MatchMethod,
                    VerificationStatus
                FROM ProductPlatform
                WHERE ProductID = :ProductID
                  AND PlatformID = :PlatformID
            """),
            {
                "ProductID": product_id,
                "PlatformID": platform_id
            }
        )

        row = result.mappings().first()

        if not row:
            return {
                "success": False,
                "message": "URL Mapping Not Found"
            }

        return dict(row)