from __future__ import annotations

import enum

from pyglet.math import Vec3

from mcpython.containers.ItemStack import ItemStack
from mcpython.world.BoundingBox import AABB
from mcpython.world.blocks.AbstractBlock import AbstractBlock
from mcpython.world.util import Facing


class SlabLikeBlock(AbstractBlock):
    TOP_BOUNDING_BOX = AABB(Vec3(0, 0.5, 0), Vec3(1, 0.5, 1))
    BOTTOM_BOUNDING_BOX = AABB(Vec3(0, 0, 0), Vec3(1, 0.5, 1))
    BLOCK_STATE_LISTING = [
        {"half": "top"},
        {"half": "bottom"},
        {"half": "double"},
    ]

    class SlabHalf(enum.Enum):
        TOP = 0
        BOTTOM = 1
        DOUBLE = 2

    def __init__(self, position: tuple[int, int, int]):
        super().__init__(position)
        self.half: SlabLikeBlock.SlabHalf = self.SlabHalf.TOP

    def on_block_placed(
        self,
        itemstack: ItemStack,
        onto: tuple[int, int, int] | None = None,
        hit_position: tuple[float, float, float] | None = None,
    ):
        if hit_position:
            if hit_position[1] < self.position[1]:
                self.half = SlabLikeBlock.SlabHalf.BOTTOM
            else:
                self.half = SlabLikeBlock.SlabHalf.TOP

    def on_block_merging(
        self,
        itemstack: ItemStack | None,
        hit_position: tuple[float, float, float] | None = None,
    ) -> bool:
        if itemstack.item.NAME != self.NAME:
            return False
        if (
            self.half == SlabLikeBlock.SlabHalf.TOP
            and hit_position[1] < self.position[1] + 0.25
        ):
            self.half = SlabLikeBlock.SlabHalf.DOUBLE
            self.update_render_state()
            return True
        elif (
            self.half == SlabLikeBlock.SlabHalf.BOTTOM
            and hit_position[1] > self.position[1] - 0.25
        ):
            self.half = SlabLikeBlock.SlabHalf.DOUBLE
            self.update_render_state()
            return True
        return False

    def get_block_state(self) -> dict[str, str]:
        return {"type": self.half.name.lower()}

    def set_block_state(self, state: dict[str, str]):
        self.half = SlabLikeBlock.SlabHalf[state.get("half", "top").upper()]

    def is_solid(self, face: Facing) -> bool:
        return (
            self.half == SlabLikeBlock.SlabHalf.DOUBLE
            or (self.half == SlabLikeBlock.SlabHalf.BOTTOM and face == Facing.UP)
            or (self.half == SlabLikeBlock.SlabHalf.TOP and face == Facing.DOWN)
        )

    def get_bounding_box(self) -> AABB:
        if self.half == SlabLikeBlock.SlabHalf.DOUBLE:
            return self.BOUNDING_BOX
        if self.half == SlabLikeBlock.SlabHalf.TOP:
            return self.TOP_BOUNDING_BOX
        return self.BOTTOM_BOUNDING_BOX
