from pydantic import BaseModel

class ProductPlatformURLSaveRequest(BaseModel):
    ProductPlatformID: int = 0
    ProductID: int
    PlatformID: int
    ProductURL: str
    IsActive: int = 1
