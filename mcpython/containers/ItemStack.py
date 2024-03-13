from __future__ import annotations

from mcpython.resources.Tags import TAG_ITEMS
from mcpython.world.items.AbstractItem import AbstractItem, ITEM_REGISTRY


class ItemStack:
    __slots__ = ("_item", "_count", "data")

    EMPTY: ItemStack = None

    def __init__(self, item: type[AbstractItem] | str | None, count=1):
        self._item = (
            (item if not isinstance(item, str) else ITEM_REGISTRY.lookup(item))
            if count != 0
            else None
        )
        self._count = count if item is not None else 0
        self.data = None

    @property
    def item(self) -> type[AbstractItem] | None:
        return self._item

    @property
    def count(self) -> int:
        return self._count if self._item else 0

    def __repr__(self):
        return f"ItemStack(item={self.item.NAME if self.item else 'EMPTY'},count={self.count})"

    def is_empty(self) -> bool:
        return self.count == 0 or self.item is None

    def copy(self) -> ItemStack:
        return ItemStack(self.item, self.count)

    def set_amount(self, amount: int) -> ItemStack:
        return ItemStack(self.item, amount)

    def add_amount(self, amount: int) -> ItemStack:
        return ItemStack(self.item, self.count + amount)

    def is_compatible(self, other: ItemStack) -> bool:
        if isinstance(other, TagStack):
            return other.is_compatible(self)
        return self.item == other.item


class TagStack(ItemStack):
    def __init__(self, tag_name: str | None, entries: list[ItemStack] = None):
        super().__init__(None)
        self.tag_name = tag_name
        self.entries = entries or (
            [ItemStack(e) for e in TAG_ITEMS.load_tag_by_name(tag_name)]
            if tag_name
            else []
        )
        self.entries = [entry for entry in self.entries if not entry.is_empty()]

    @property
    def count(self) -> int:
        return max(entry.count for entry in self.entries)

    def is_empty(self) -> bool:
        return all(entry.is_empty() for entry in self.entries)

    def is_compatible(self, other: ItemStack) -> bool:
        if isinstance(other, TagStack):
            for a in self.entries:
                for b in other.entries:
                    if a.matches(b):
                        return True
        else:
            for entry in self.entries:
                if entry.is_compatible(other):
                    return True

        return False

    def __repr__(self):
        return f"TagStack({self.tag_name},{self.entries})"


ItemStack.EMPTY = ItemStack(None)
