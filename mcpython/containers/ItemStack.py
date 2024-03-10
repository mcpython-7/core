from __future__ import annotations
from mcpython.world.items.AbstractItem import AbstractItem


class ItemStack:
    def __init__(self, item: AbstractItem, count=1):
        self.count = count
        self.item = item
