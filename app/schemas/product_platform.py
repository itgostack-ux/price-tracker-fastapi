from pydantic import BaseModel
from typing import Optional


class ProductPlatformSaveRequest(BaseModel):
    ProductPlatformID: Optional[int] = None
    ProductID: int
    PlatformID: int
    ProductURL: str

    URLStatus: str = "ACTIVE"
    MatchScore: float = 100
    MatchMethod: str = "SEARCH"
    VerificationStatus: str = "VERIFIED"

    IsActive: int = 1
