from __future__ import annotations

import typing

from pyglet.window import mouse, key

from mcpython.world.blocks.AbstractBlock import BLOCK_REGISTRY, AbstractBlock

if typing.TYPE_CHECKING:
    from mcpython.containers.ItemStack import ItemStack


@BLOCK_REGISTRY.register
class CraftingTable(AbstractBlock):
    NAME = "minecraft:crafting_table"
    CONTAINER = None

    def on_block_interaction(
        self, itemstack: ItemStack, button: int, modifiers: int
    ) -> bool:
        if button == mouse.RIGHT and not modifiers & key.MOD_SHIFT:
            from mcpython.rendering.Window import Window

            if self.CONTAINER is None:
                # todo: create it earlier, requires worldgen to happen later
                from mcpython.containers.CraftingTableInventory import (
                    CraftingTableContainer,
                )

                CraftingTable.CONTAINER = CraftingTableContainer()

            Window.INSTANCE.set_exclusive_mouse(False)
            self.CONTAINER.show_container()
            return True

        return False
