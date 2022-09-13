import copy
import typing

from mcpython.world.item.Item import Item


class InvalidItemCount(Exception):
    pass


class ItemStack:
    """
    Class representing a stack of an item
    """

    __slots__ = ("item_type", "count", "nbt")

    @classmethod
    def create_empty(cls):
        return cls(None, 0)

    def __init__(self, item_type: Item | None, count: int):
        self.item_type = item_type
        self.count = count
        self.set_count(count, call_event=False)

        self.nbt: typing.Dict[str, typing.Any] = {}

    def set_count(
        self, count: int, validate=True, raise_exception=False, call_event=True
    ):
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
            return

        if count == 0:
            self.clear()
            return

        previous = self.count
        self.count = count

        if call_event:
            self.item_type.on_item_count_changed(self, previous, self.count)

    def add_count(self, count: int, validate=True, call_event=True) -> int:
        if self.item_type is None:
            return 0

        if count < 0:
            return -self.remove_count(-count, validate, call_event)

        new_count = self.count + count

        if not validate:
            previous_count = self.count
            self.count = new_count

            if call_event:
                self.item_type.on_item_count_changed(self, previous_count, new_count)

            return count

        if new_count > self.item_type.get_maximum_stack_size():
            self.count = self.item_type.get_maximum_stack_size()
            return new_count - self.count

        self.set_count(new_count, False, False, call_event)
        return count

    def remove_count(self, count: int, validate=True, call_event=True) -> int:
        if self.item_type is None:
            return 0

        if count < 0:
            return -self.add_count(-count, validate, call_event)

        new_count = self.count - count

        if not validate:
            previous_count = self.count
            self.count = new_count

            if call_event:
                self.item_type.on_item_count_changed(self, previous_count, new_count)

            return count

        if new_count < 0:
            self.clear(call_event=call_event)
            return count + new_count

        self.set_count(new_count, False, False, call_event)
        return count

    def clear(self, call_event=True):
        if self.item_type is None:
            self.count = 0
            return

        if not call_event:
            self.count = 0
            self.item_type = None
            return

        previous_count = self.count
        self.count = 0
        previous_item_type = self.item_type
        self.item_type = None
        previous_item_type.on_item_count_changed(self, previous_count, 0)
        self.nbt.clear()
        return self

    def copy(self) -> "ItemStack":
        itemstack = ItemStack(self.item_type, self.count)
        itemstack.nbt = copy.deepcopy(self.nbt)
        self.item_type.on_itemstack_copied(self, itemstack)
        return itemstack

    def copy_from(self, itemstack: "ItemStack"):
        self.item_type = itemstack.item_type
        self.count = itemstack.count
        self.nbt = copy.deepcopy(itemstack.nbt)
        self.item_type.on_itemstack_copied(itemstack, self)
        return self
