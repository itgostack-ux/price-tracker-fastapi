from fastapi import APIRouter
from sqlalchemy import text

from app.database import engine
from app.schemas.platform import PlatformSaveRequest

router = APIRouter(
    prefix="/platforms",
    tags=["Platform Master"]
)

# GET ALL
@router.get("/")
def get_platforms():

    with engine.connect() as conn:

        result = conn.execute(text("""
            SELECT
                PlatformID,
                PlatformCode,
                PlatformName,
                IsEnabled,
                BaseURL,
                CollectorType
            FROM PlatformMaster
            ORDER BY PlatformName
        """))

        return [dict(row._mapping) for row in result]


# GET BY ID
@router.get("/{platform_id}")
def get_platform(platform_id: int):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT *
                FROM PlatformMaster
                WHERE PlatformID = :PlatformID
            """),
            {"PlatformID": platform_id}
        )

        row = result.mappings().first()

        if not row:
            return {
                "success": False,
                "message": "Platform Not Found"
            }

        return dict(row)


# ADD / UPDATE / DISABLE
@router.post("/save")
def save_platform(payload: PlatformSaveRequest):

    data = payload.model_dump()

    platform_id = data.get("PlatformID")

    with engine.begin() as conn:

        # ADD
        if not platform_id:

            conn.execute(
                text("""
                    INSERT INTO PlatformMaster
                    (
                        PlatformCode,
                        PlatformName,
                        IsEnabled,
                        BaseURL,
                        CollectorType
                    )
                    VALUES
                    (
                        :PlatformCode,
                        :PlatformName,
                        1,
                        :BaseURL,
                        :CollectorType
                    )
                """),
                data
            )

            return {
                "success": True,
                "message": "Platform Added Successfully"
            }

        # DISABLE
        if data.get("IsEnabled") == 0:

            conn.execute(
                text("""
                    UPDATE PlatformMaster
                    SET IsEnabled = 0
                    WHERE PlatformID = :PlatformID
                """),
                {"PlatformID": platform_id}
            )

            return {
                "success": True,
                "message": "Platform Disabled Successfully"
            }

        # UPDATE
        conn.execute(
            text("""
                UPDATE PlatformMaster
                SET
                    PlatformCode = :PlatformCode,
                    PlatformName = :PlatformName,
                    BaseURL = :BaseURL,
                    CollectorType = :CollectorType,
                    IsEnabled = :IsEnabled
                WHERE PlatformID = :PlatformID
            """),
            data
        )

        return {
            "success": True,
            "message": "Platform Updated Successfully"
        }