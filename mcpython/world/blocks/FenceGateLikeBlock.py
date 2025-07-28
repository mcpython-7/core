from __future__ import annotations

import itertools

from mcpython.containers.ItemStack import ItemStack
from mcpython.world.blocks.AbstractBlock import AbstractBlock
from mcpython.world.util import Facing

from pyglet.window import key, mouse


class FenceGateLikeBlock(AbstractBlock):
    FACE_ORDER: list[Facing] = list(Facing)[2:]
    BLOCk_STATE_LISTING = [
        {
            "facing": face.name.lower(),
            "in_wall": str(bool(in_wall)).lower(),
            "open": str(bool(opened)).lower(),
        }
        for face, in_wall, opened in itertools.product(FACE_ORDER, range(2), range(2))
    ]

    def __init__(self, position: tuple[int, int, int]):
        super().__init__(position)
        self.facing: Facing = Facing.NORTH
        self.in_wall = False
        self.open = False

    def get_block_state(self) -> dict[str, str]:
        return {
            "facing": self.facing.name.lower(),
            "in_wall": str(self.in_wall).lower(),
            "open": str(self.open).lower(),
        }

    def set_block_state(self, state: dict[str, str]):
        self.facing = Facing[state.get("facing", "north").upper()]
        self.in_wall = state.get("in_wall", "false") == "true"
        self.open = state.get("open", "false") == "true"

    def on_block_updated(self):
        x, y, z = self.position
        block = self.chunk.blocks.get((x, y + 1, z))

        prev = self.in_wall
        self.in_wall = isinstance(block, FenceGateLikeBlock)
        if self.in_wall != prev:
            self.update_render_state()

    def on_block_interaction(
        self, itemstack: ItemStack, button: int, modifiers: int
    ) -> bool:
        if button == mouse.RIGHT and not modifiers & key.LSHIFT:
            self.open = not self.open
            self.update_render_state()
            return True

        return False

    def is_solid(self, face: Facing) -> bool:
        return False
