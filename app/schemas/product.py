from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    sku: str
    quantity: int
    price: float


class ProductResponse(ProductCreate):
    id: int

    class Config:
        from_attributes = True

class ProductUpdate(BaseModel):
    name: str
    sku: str
    quantity: int
    price: float