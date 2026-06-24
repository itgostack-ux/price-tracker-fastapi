from pydantic import BaseModel

class PlatformURLPriceHistorySaveRequest(BaseModel):
    PriceID: int = 0
    ProductPlatformID: int
    Price: float
    MRP: float = 0
    Discount: float = 0
    Source: str = ""
    IsActive: int = 1
