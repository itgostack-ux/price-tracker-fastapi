from pydantic import BaseModel
from typing import Optional

class PriceHistorySaveRequest(BaseModel):
    PriceHistoryID: Optional[int] = None
    UrlMapID: int
    Competitor_Price: float
    MRP: Optional[float] = None