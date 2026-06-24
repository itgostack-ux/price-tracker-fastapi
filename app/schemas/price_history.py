from pydantic import BaseModel
from typing import Optional

class PriceHistorySaveRequest(BaseModel):
    PriceID: Optional[int] = None
    ProductID: Optional[int] = None
    PlatformID: Optional[int] = None
    VerifiedID: Optional[int] = None
    Price: Optional[float] = None
    MRP: Optional[float] = None
    Discount: Optional[float] = None
    Source: Optional[str] = None
    IsDeleted: Optional[int] = 0