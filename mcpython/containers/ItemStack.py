from __future__ import annotations
from mcpython.world.items.AbstractItem import AbstractItem


class ItemStack:
    @classmethod
    def empty(cls):
        return ItemStack(None)

    def __init__(self, item: AbstractItem | None, count=1):
        self.item = item
        self.count = count if item is not None else 0

    def __repr__(self):
        return f"ItemStack(item={self.item.NAME},count={self.count})"

    def is_empty(self) -> bool:
        return self.count == 0 or self.item is None

    def copy(self) -> ItemStack:
        return ItemStack(self.item, self.count)

    def set_amount(self, amount: int) -> ItemStack:
        self.count = amount
        if amount == 0:
            self.item = None
        return self

    def add_amount(self, amount: int) -> ItemStack:
        self.count += amount
        if amount == 0:
            self.item = None
        return self

    def is_compatible(self, other: ItemStack) -> bool:
        return self.item == other.item
