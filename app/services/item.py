from app.schemas.item import ItemBase, ItemCreate, ItemUpdate

class ItemService:
    """
    Business logic for items.
    Uses an in-memory store — swap with a real DB session when ready.
    """

    def __init__(self) -> None:
        self._store: dict[int, ItemBase] = {}
        self._counter: int = 0

    def get_all(self) -> list[ItemBase]:
        return list(self._store.values())

    def get_by_id(self, item_id: int) -> ItemBase | None:
        return self._store.get(item_id)

    def create(self, payload: ItemCreate) -> ItemBase:
        self._counter += 1
        item = {
            "id": self._counter,
            **payload.model_dump()
        }
        self._store[item.id] = item
        return item

    def update(self, item_id: int, payload: ItemUpdate) -> ItemBase | None:
        item = self._store.get(item_id)
        if not item:
            return None
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        return item

    def delete(self, item_id: int) -> bool:
        if item_id not in self._store:
            return False
        del self._store[item_id]
        return True
