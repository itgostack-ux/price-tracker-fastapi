from fastapi import APIRouter
from sqlalchemy import text

from app.database import engine
from app.schemas.urlmap import UrlMapSaveRequest

router = APIRouter(
    prefix="/urlmap",
    tags=["URL Map"]
)

@router.post("/save")
def save_urlmap(payload: UrlMapSaveRequest):

    data = payload.model_dump()

    urlmap_id = data.get("UrlMapID")

    with engine.begin() as conn:

        # ADD
        if not urlmap_id:

            conn.execute(
                text("""
                    INSERT INTO CompetitorUrlMap
                    (
                        ProductID,
                        CompetitorID,
                        CompetitorProductName,
                        CompetitorProductURL,
                        CurrentPrice,
                        CurrentMRP,
                        IsActive
                    )
                    VALUES
                    (
                        :ProductID,
                        :CompetitorID,
                        :CompetitorProductName,
                        :CompetitorProductURL,
                        :CurrentPrice,
                        :CurrentMRP,
                        1
                    )
                """),
                data
            )

            return {
                "success": True,
                "message": "URL Map Added Successfully"
            }

        # DISABLE
        if data.get("IsActive") == 0:

            conn.execute(
                text("""
                    UPDATE CompetitorUrlMap
                    SET IsActive = 0
                    WHERE UrlMapID = :UrlMapID
                """),
                {"UrlMapID": urlmap_id}
            )

            return {
                "success": True,
                "message": "URL Map Disabled Successfully"
            }

        # UPDATE
        conn.execute(
            text("""
                UPDATE CompetitorUrlMap
                SET
                    ProductID = :ProductID,
                    CompetitorID = :CompetitorID,
                    CompetitorProductName = :CompetitorProductName,
                    CompetitorProductURL = :CompetitorProductURL,
                    CurrentPrice = :CurrentPrice,
                    CurrentMRP = :CurrentMRP
                WHERE UrlMapID = :UrlMapID
            """),
            data
        )

        return {
            "success": True,
            "message": "URL Map Updated Successfully"
        }

@router.get("/")
def get_urlmaps():

    with engine.connect() as conn:

        result = conn.execute(text("""
            SELECT
                U.UrlMapID,
                P.ItemName,
                C.CompetitorName,
                U.CompetitorProductURL,
                U.CurrentPrice,
                U.CurrentMRP,
                U.IsActive
            FROM CompetitorUrlMap U
            INNER JOIN ProductMaster P
                ON P.ProductID = U.ProductID
            INNER JOIN Competitors C
                ON C.CompetitorID = U.CompetitorID
            ORDER BY U.UrlMapID DESC
        """))

        return [dict(row._mapping) for row in result]