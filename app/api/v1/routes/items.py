from fastapi import APIRouter, HTTPException

from app.schemas.item import ItemCreate, ItemRead, ItemUpdate
from app.services.item import ItemService

router = APIRouter()
service = ItemService()


@router.get("/", response_model=list[ItemRead])
def list_items():
    """Return all items."""
    return service.get_all()


@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: int):
    """Return a single item by ID."""
    item = service.get_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/", response_model=ItemRead, status_code=201)
def create_item(payload: ItemCreate):
    """Create a new item."""
    return service.create(payload)


@router.put("/{item_id}", response_model=ItemRead)
def update_item(item_id: int, payload: ItemUpdate):
    """Update an existing item."""
    item = service.update(item_id, payload)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int):
    """Delete an item."""
    deleted = service.delete(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
