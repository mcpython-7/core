import typing

import pyglet

from mcpython.inventory.Slot import AbstractSlot
from mcpython.world.item.ItemStack import ItemStack


class AbstractItemstackRenderer:
    @classmethod
    async def initial_render_slot(cls, slot: AbstractSlot, batch: pyglet.graphics.Batch) -> typing.List:
        raise NotImplementedError

    @classmethod
    async def update_rendering_data(cls, slot: AbstractSlot, batch: pyglet.graphics.Batch, data: typing.List):
        raise NotImplementedError

    @classmethod
    async def delete_rendering_data(cls, slot: AbstractSlot, batch: pyglet.graphics.Batch, data: typing.List):
        for item in data:
            item.delete()


class DefaultItemstackRenderer(AbstractItemstackRenderer):
    @classmethod
    async def initial_render_slot(cls, slot: AbstractSlot, batch: pyglet.graphics.Batch) -> typing.List:
        stack: ItemStack = await slot.get_underlying_itemstack()
        x, y = slot.get_rendering_position()
        return [
            pyglet.text.Label("WIP", font_size=15, x=x, y=y, color=(0, 0, 0, 255), batch=batch),
            pyglet.text.Label(str(stack.count), font_size=8, x=x+30, y=y-2, color=(0, 0, 0, 255), batch=batch)
        ]

    @classmethod
    async def update_rendering_data(cls, slot: AbstractSlot, batch: pyglet.graphics.Batch, data: typing.List):
        pass  # todo: update sprite and count!

