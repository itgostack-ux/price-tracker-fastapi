from pydantic import BaseModel
from typing import Optional

class CompetitorSaveRequest(BaseModel):
    CompetitorID: Optional[int] = None
    CompetitorName: Optional[str] = None
    WebsiteURL: Optional[str] = None
    IsActive: Optional[int] = 1