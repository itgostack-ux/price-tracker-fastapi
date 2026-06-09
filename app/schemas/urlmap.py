from pydantic import BaseModel
from typing import Optional

class UrlMapSaveRequest(BaseModel):
    UrlMapID: Optional[int] = None

    ProductID: Optional[int] = None
    CompetitorID: Optional[int] = None

    CompetitorProductName: Optional[str] = None
    CompetitorProductURL: Optional[str] = None

    CurrentPrice: Optional[float] = None
    CurrentMRP: Optional[float] = None

    IsActive: Optional[int] = 1