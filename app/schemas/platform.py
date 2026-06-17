from pydantic import BaseModel
from typing import Optional


class PlatformSaveRequest(BaseModel):
    PlatformID: Optional[int] = None
    PlatformCode: str
    PlatformName: str
    BaseURL: str
    CollectorType: str
    IsEnabled: int = 1