from __future__ import annotations

import typing

from mcpython.world.blocks.AbstractBlock import BLOCK_REGISTRY, AbstractBlock
from mcpython.world.util import Facing

if typing.TYPE_CHECKING:
    from mcpython.containers.ItemStack import ItemStack


@BLOCK_REGISTRY.register
class ShortGrass(AbstractBlock):
    NAME = "minecraft:short_grass"
    TRANSPARENT = True
    NO_COLLISION = True

    def get_tint_colors(self) -> list[tuple[float, float, float, float]] | None:
        return [(145 / 255, 189 / 255, 89 / 255, 1)]

    def is_solid(self, face: Facing) -> bool:
        return False

    def on_block_placed(
        self,
        itemstack: ItemStack | None,
        onto: tuple[int, int, int] | None = None,
        hit_position: tuple[float, float, float] | None = None,
    ) -> bool:
        x, y, z = self.position
        block = self.chunk.blocks.get((x, y - 1, z))
        if block is None or not block.is_solid(Facing.UP):
            return False

        return True

    def on_block_updated(self):
        x, y, z = self.position
        block = self.chunk.blocks.get((x, y - 1, z))
        if block is None or not block.is_solid(Facing.UP):
            self.chunk.remove_block(self)
