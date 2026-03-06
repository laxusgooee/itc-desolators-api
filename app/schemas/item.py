from pydantic import BaseModel


class ItemBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    is_active: bool = True


class ItemCreate(ItemBase):
    """Schema for creating a new item."""
    pass


class ItemUpdate(BaseModel):
    """Schema for partially updating an item (all fields optional)."""
    name: str | None = None
    description: str | None = None
    price: float | None = None
    is_active: bool | None = None


class ItemRead(ItemBase):
    """Schema for reading / returning an item."""
    id: int

    model_config = {"from_attributes": True}
