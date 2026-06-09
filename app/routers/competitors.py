from fastapi import APIRouter
from sqlalchemy import text

from app.database import engine
from app.schemas.competitor import CompetitorSaveRequest

router = APIRouter(
    prefix="/competitors",
    tags=["Competitors"]
)

# GET ALL
@router.get("/")
def get_competitors():

    with engine.connect() as conn:

        result = conn.execute(text("""
            SELECT
                CompetitorID,
                CompetitorName,
                WebsiteURL,
                IsActive,
                CreatedOn
            FROM Competitors
            ORDER BY CompetitorName
        """))

        return [dict(row._mapping) for row in result]


# GET BY ID
@router.get("/{competitor_id}")
def get_competitor(competitor_id: int):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT *
                FROM Competitors
                WHERE CompetitorID = :CompetitorID
            """),
            {"CompetitorID": competitor_id}
        )

        row = result.mappings().first()

        if not row:
            return {
                "success": False,
                "message": "Competitor Not Found"
            }

        return dict(row)


# ADD / UPDATE / DISABLE
@router.post("/save")
def save_competitor(payload: CompetitorSaveRequest):

    data = payload.model_dump()

    competitor_id = data.get("CompetitorID")

    with engine.begin() as conn:

        # ADD
        if not competitor_id:

            conn.execute(
                text("""
                    INSERT INTO Competitors
                    (
                        CompetitorName,
                        WebsiteURL,
                        IsActive
                    )
                    VALUES
                    (
                        :CompetitorName,
                        :WebsiteURL,
                        1
                    )
                """),
                data
            )

            return {
                "success": True,
                "message": "Competitor Added Successfully"
            }

        # DISABLE
        if data.get("IsActive") == 0:

            conn.execute(
                text("""
                    UPDATE Competitors
                    SET IsActive = 0
                    WHERE CompetitorID = :CompetitorID
                """),
                {"CompetitorID": competitor_id}
            )

            return {
                "success": True,
                "message": "Competitor Disabled Successfully"
            }

        # UPDATE
        conn.execute(
            text("""
                UPDATE Competitors
                SET
                    CompetitorName = :CompetitorName,
                    WebsiteURL = :WebsiteURL
                WHERE CompetitorID = :CompetitorID
            """),
            data
        )

        return {
            "success": True,
            "message": "Competitor Updated Successfully"
        }