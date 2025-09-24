from __future__ import annotations

import functools

from mcpython.resources.Tags import TAG_ITEMS
from mcpython.world.items.AbstractItem import AbstractItem, ITEM_REGISTRY
from mcpython.world.serialization.DataBuffer import (
    ReadBuffer,
    WriteBuffer,
)
from mcpython.world.serialization.IBufferSerializable import (
    IBufferSerializableWithVersion,
)


class ItemStack(IBufferSerializableWithVersion):
    __slots__ = ("_item", "_count", "data")

    EMPTY: ItemStack = None

    # Max version is 254; 255 means "extended version attribute" (not used yet)
    ITEMSTACK_VERSION = 0

    @classmethod
    def decode(cls, buffer: ReadBuffer) -> ItemStack:
        name = buffer.read_string()
        if name == 0:
            return cls.EMPTY

        size = buffer.read_uint16()
        itemstack = ItemStack(name, size)
        buffer = cls.decode_datafixable(buffer)
        itemstack.item.decode_metadata(itemstack, buffer)
        return itemstack

    @functools.cached_property
    def VERSION(self):
        return 0 if self.is_empty() else self.item.VERSION << 8 + self.ITEMSTACK_VERSION

    @functools.cached_property
    def DATA_FIXERS(self):
        # Ensure that the correct fixer is used
        return (
            {}
            if self.is_empty()
            else {
                version << 8 + self.ITEMSTACK_VERSION: fixer
                for version, fixer in self.item.DATA_FIXERS.items()
            }
        )

    def __init__(self, item: type[AbstractItem] | str | None, count=1):
        self._item = (
            (ITEM_REGISTRY.lookup(item) if isinstance(item, str) else item)
            if count != 0
            else None
        )
        self._count = count if item is not None else 0
        self.data = None
        self._metadata: dict | None = None

    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = {}
        return self._metadata

    def encode(self, buffer: WriteBuffer):
        if self.is_empty():
            buffer.write_string("")
            return

        buffer.write_string(self.item.NAME)
        buffer.write_uint16(self.count)
        self.encode_datafixable(buffer)
        self.item.encode_metadata(self, buffer)

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
        if self.is_empty():
            return ItemStack(None)
        stack = ItemStack(self.item, self.count)
        self.item.copy_metadata(self, stack)
        return stack

    def set_amount(self, amount: int = 1) -> ItemStack:
        """
        Creates a new ItemStack with the same item, but the given amount

        WARNING: when this itemstack is empty, returns an empty stack

        :param amount: the amount to use
        :return: the new itemstack, is empty when amount is 0
        :raises ValueError if amount is negative
        """
        if self.is_empty():
            return ItemStack(None)

        if amount < 0:
            raise ValueError(
                f"Cannot create an itemstack with negative amount {amount}"
            )
        if amount == 0:
            return ItemStack(None)

        stack = ItemStack(self.item, amount)
        self.item.copy_metadata(self, stack)
        return stack

    def add_amount(self, amount: int) -> ItemStack:
        """
        Creates a new ItemStack, with the added amount

        WARNING: when this itemstack is empty, returns an empty stack

        :param amount: the amount to add, might be negative to reduce
        :return: the ItemStack; might be empty if count is 0
        :raises ValueError: if the count would be negative afterwards
        """
        if self.is_empty():
            return ItemStack(None)

        if self.count + amount < 0:
            raise ValueError(
                f"Cannot subtract {-amount} from this stack, as it only holds {self.count} items"
            )

        if self.count + amount == 0:
            return ItemStack(None)

        stack = ItemStack(self.item, self.count + amount)
        self.item.copy_metadata(self, stack)
        return stack

    def is_compatible(self, other: ItemStack) -> bool:
        if isinstance(other, TagStack):
            return other.is_compatible(self)
        return self.item == other.item and self.item.check_metadata_compatible(
            self, other
        )


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
            return self.tag_name == other.tag_name
        else:
            for entry in self.entries:
                if entry.is_compatible(other):
                    return True

        return False

    def __repr__(self):
        return f"TagStack({self.tag_name},{self.entries})"


ItemStack.EMPTY = ItemStack(None)
