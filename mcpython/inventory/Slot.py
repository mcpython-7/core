import typing

import pyglet

from mcpython.world.item.ItemStack import ItemStack


class AbstractSlot:
    def __init__(self):
        self.batch: pyglet.graphics.Batch = None
        self.renderer = None
        self.rendering_data = []

    def get_rendering_position(self):
        return 0, 0

    async def hide_slot(self):
        if self.batch is None: return

        if self.renderer:
            await self.renderer.delete_rendering_data(self, self.batch, self.rendering_data)
            self.rendering_data.clear()
            self.renderer = None

    async def update_rendering_state(self, new_renderer=False):
        stack = await self.get_underlying_itemstack()

        if stack.count == 0:
            await self.hide_slot()
            return

        if new_renderer or self.renderer is None:
            self.renderer = stack.item_type.get_itemstack_renderer(stack)

            self.rendering_data[:] = await self.renderer.initial_render_slot(self, self.batch)
        else:
            await self.renderer.update_rendering_data(self, self.batch, self.rendering_data)

    async def set_itemstack(self, itemstack: ItemStack) -> bool:
        raise NotImplementedError

    async def try_insert_most_itemstack(self, itemstack: ItemStack) -> ItemStack:
        if await self.set_itemstack(await itemstack.copy()):
            return await itemstack.clear()
        return itemstack

    async def get_underlying_itemstack(self) -> ItemStack | None:
        raise ValueError(f"Cannot get underlying itemstack for {self}")

    async def contains_resource(self, resource: ItemStack) -> bool:
        return False

    async def try_extract(self, itemstack: ItemStack) -> bool:
        raise NotImplementedError

    async def try_extract_most(self, itemstack: ItemStack) -> ItemStack:
        if self.try_extract(itemstack):
            return ItemStack.create_empty()
        return itemstack


class DefaultSlot(AbstractSlot):
    def __init__(self, render_position: typing.Tuple[int, int], validator: typing.Callable[["DefaultSlot", ItemStack], bool] = lambda _, __: True):
        super().__init__()

        self.render_position = render_position
        self.validator = validator

        self.itemstack = ItemStack.create_empty()

    def get_rendering_position(self):
        return self.render_position

    async def set_itemstack(self, itemstack: ItemStack) -> bool:
        if not self.validator(self, itemstack):
            return False

        self.itemstack = itemstack
        await self.update_rendering_state(new_renderer=True)
        return True

    async def try_insert_most_itemstack(self, itemstack: ItemStack) -> ItemStack:
        if itemstack.count == 0:
            return itemstack

        if self.itemstack.count == 0:
            self.itemstack = await itemstack.copy()

            if self.itemstack.count > self.itemstack.item_type.get_maximum_stack_size():
                delta = self.itemstack.item_type.get_maximum_stack_size() - self.itemstack.count
                await self.itemstack.add_count(-delta)

                await self.update_rendering_state(new_renderer=True)

                return await (await itemstack.copy()).set_count(delta)

            await self.update_rendering_state(new_renderer=True)

            return ItemStack.create_empty()

        if not self.itemstack.compare_data(itemstack):
            return await itemstack.copy()

        delta = self.itemstack.count - self.itemstack.item_type.get_maximum_stack_size()

        if delta == 0:
            return await itemstack.copy()

        if delta < 0:
            self.itemstack.add_count(itemstack.count)

            await self.update_rendering_state(new_renderer=False)

            return ItemStack.create_empty()

        self.itemstack.set_count(self.itemstack.item_type.get_maximum_stack_size())
        await self.update_rendering_state(new_renderer=False)
        return await (await itemstack.copy()).set_count(delta)

    async def get_underlying_itemstack(self) -> ItemStack:
        return self.itemstack

    async def contains_resource(self, resource: ItemStack) -> bool:
        return await self.itemstack.compare_data(resource)

    async def try_extract(self, itemstack: ItemStack) -> bool:
        if not await self.itemstack.compare_data(itemstack):
            return False

        if self.itemstack.count < itemstack.count:
            return False

        await self.itemstack.add_count(-itemstack.count)
        await self.update_rendering_state(new_renderer=False)
        return True

    async def try_extract_most(self, itemstack: ItemStack) -> ItemStack:
        if itemstack.count == 0 or not await self.itemstack.compare_data(itemstack) or self.itemstack.count == 0:
            return itemstack

        delta = self.itemstack.count - itemstack.count

        if delta == 0:
            await self.itemstack.clear()
            await self.update_rendering_state(new_renderer=True)
            return ItemStack.create_empty()

        if delta < 0:
            await self.itemstack.clear()
            await self.update_rendering_state(new_renderer=True)
            return await (await itemstack.copy()).set_count(-delta)

        await self.itemstack.add_count(-delta)
        await self.update_rendering_state(new_renderer=False)
        return ItemStack.create_empty()

