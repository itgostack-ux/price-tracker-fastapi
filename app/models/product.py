from pydantic import BaseModel
from typing import Optional

class ProductSaveRequest(BaseModel):
    ProductID: Optional[int] = None
    ItemCode: Optional[str] = None
    Brand: Optional[str] = None
    ModelName: Optional[str] = None
    RAM: Optional[str] = None
    StorageSize: Optional[str] = None
    ColorName: Optional[str] = None
    VariantName: Optional[str] = None
    ItemName: Optional[str] = None
    Category: Optional[str] = None
    SubCategory: Optional[str] = None
    IsActive: Optional[int] = 1