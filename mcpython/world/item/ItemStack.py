import copy
import typing

from mcpython.world.item.Item import Item
from mcpython.world.item.ItemManager import ITEM_REGISTRY


class InvalidItemCount(Exception):
    pass


class ItemStack:
    """
    Class representing a stack of an item
    """

    __slots__ = ("item_type", "count", "nbt", "hidden_nbt")

    @classmethod
    def create_empty(cls):
        return cls(None, 0)

    def __init__(self, item_type: Item | str | None, count: int = None):
        if isinstance(item_type, str):
            item_type = ITEM_REGISTRY.lookup(item_type)

        self.item_type = item_type
        self.count = count if count is not None else (0 if item_type is None else 1)

        self.nbt: typing.Dict[str, typing.Any] = {}

        # nbt data not used for comparing ItemStack's
        self.hidden_nbt: typing.Dict[str, typing.Any] = {}

    async def compare_data(self, other: "ItemStack") -> bool:
        if self.item_type is None and other.item_type is None:
            return True

        return await self.item_type.compare_itemstack_data(self, other)

    async def set_count(
        self, count: int, validate=True, raise_exception=False, call_event=True
    ) -> "ItemStack":
        if count < 0:
            if raise_exception:
                raise InvalidItemCount(
                    f"Stack size {count} is less than 0, which is invalid"
                )
            count = 0

        elif (
            validate
            and self.item_type is not None
            and self.item_type.get_maximum_stack_size() < count
        ):
            if raise_exception:
                raise InvalidItemCount(
                    f"Stack size {count} is bigger than the maximum stack size of {self.item_type.NAME}, which is {self.item_type.get_maximum_stack_size()}"
                )

            count = self.item_type.get_maximum_stack_size()

        if self.item_type is None:
            self.count = 0
            return self

        if count == 0:
            await self.clear()
            return self

        previous = self.count
        self.count = count

        if call_event:
            await self.item_type.on_item_count_changed(self, previous, self.count)

        return self

    async def add_count(self, count: int, validate=True, call_event=True) -> int:
        if self.item_type is None:
            return 0

        if count < 0:
            return -self.remove_count(-count, validate, call_event)

        new_count = self.count + count

        if not validate:
            previous_count = self.count
            self.count = new_count

            if call_event:
                await self.item_type.on_item_count_changed(self, previous_count, new_count)

            return count

        if new_count > self.item_type.get_maximum_stack_size():
            self.count = self.item_type.get_maximum_stack_size()
            return new_count - self.count

        await self.set_count(new_count, False, False, call_event)
        return count

    async def remove_count(self, count: int, validate=True, call_event=True) -> int:
        if self.item_type is None:
            return 0

        if count < 0:
            return -self.add_count(-count, validate, call_event)

        new_count = self.count - count

        if not validate:
            previous_count = self.count
            self.count = new_count

            if call_event:
                await self.item_type.on_item_count_changed(self, previous_count, new_count)

            return count

        if new_count < 0:
            await self.clear(call_event=call_event)
            return count + new_count

        await self.set_count(new_count, False, False, call_event)
        return count

    async def clear(self, call_event=True):
        if self.item_type is None:
            self.count = 0
            return self

        if not call_event:
            self.count = 0
            self.item_type = None
            return self

        previous_count = self.count
        self.count = 0
        previous_item_type = self.item_type
        self.item_type = None
        self.nbt.clear()
        self.hidden_nbt.clear()

        await previous_item_type.on_item_count_changed(self, previous_count, 0)
        return self

    async def copy(self) -> "ItemStack":
        itemstack = ItemStack(self.item_type, self.count)
        itemstack.nbt = copy.deepcopy(self.nbt)
        itemstack.hidden_nbt = copy.deepcopy(self.hidden_nbt)
        await self.item_type.on_itemstack_copied(self, itemstack)
        return itemstack

    async def copy_from(self, itemstack: "ItemStack"):
        self.item_type = itemstack.item_type
        self.count = itemstack.count
        self.nbt = copy.deepcopy(itemstack.nbt)
        self.hidden_nbt = copy.deepcopy(itemstack.hidden_nbt)
        await self.item_type.on_itemstack_copied(itemstack, self)
        return self
