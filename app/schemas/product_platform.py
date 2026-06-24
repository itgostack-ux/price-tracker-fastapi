from pydantic import BaseModel

class ProductURLUpdateRequest(BaseModel):
    ProductPlatformID: int
    ProductID: int
    PlatformID: int
    ProductURL: str