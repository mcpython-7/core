from __future__ import annotations
from mcpython.world.items.AbstractItem import AbstractItem


class ItemStack:
    __slots__ = ("_item", "_count", "data")

    EMPTY: ItemStack = None

    def __init__(self, item: type[AbstractItem] | None, count=1):
        self._item = item if count != 0 else None
        self._count = count if item is not None else 0
        self.data = None

    @property
    def item(self) -> type[AbstractItem] | None:
        return self._item

    @property
    def count(self) -> int:
        return self._count if self._item else 0

    def __repr__(self):
        return f"ItemStack(item={self.item.NAME},count={self.count})"

    def is_empty(self) -> bool:
        return self.count == 0 or self.item is None

    def copy(self) -> ItemStack:
        return ItemStack(self.item, self.count)

    def set_amount(self, amount: int) -> ItemStack:
        return ItemStack(self.item, amount)

    def add_amount(self, amount: int) -> ItemStack:
        return ItemStack(self.item, self.count + amount)

    def is_compatible(self, other: ItemStack) -> bool:
        return self.item == other.item


ItemStack.EMPTY = ItemStack(None)
