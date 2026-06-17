from pydantic import BaseModel, HttpUrl
from typing import Optional


class UrlMapSaveRequest(BaseModel):
    UrlMapID: Optional[int] = None

    ProductID: int
    CompetitorID: int

    CompetitorProductName: str
    CompetitorProductURL: str



    IsActive: int = 1