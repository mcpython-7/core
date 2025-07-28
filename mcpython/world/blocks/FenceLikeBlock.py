from __future__ import annotations

import itertools

from mcpython.world.blocks.AbstractBlock import AbstractBlock
from mcpython.world.util import Facing


class FenceLikeBlock(AbstractBlock):
    FACE_ORDER: list[Facing] = list(Facing)[2:]
    BLOCk_STATE_LISTING = [
        {
            "north": str(bool(a)).lower(),
            "east": str(bool(b)).lower(),
            "south": str(bool(c)).lower(),
            "west": str(bool(d)).lower(),
        }
        for a, b, c, d in itertools.product(range(2), range(2), range(2), range(2))
    ]

    def __init__(self, position: tuple[int, int, int]):
        super().__init__(position)
        self.connected = [False] * 4

    def may_connect_to(self, fence: FenceLikeBlock) -> bool:
        return True

    def get_block_state(self) -> dict[str, str]:
        return {
            face.name.lower(): str(state).lower()
            for face, state in zip(self.FACE_ORDER, self.connected)
        }

    def set_block_state(self, state: dict[str, str]):
        for face, state in state.items():
            self.connected[self.FACE_ORDER.index(Facing[face.upper()])] = (
                state == "true"
            )

    def on_block_updated(self):
        pos = self.position

        for i, face in enumerate(self.FACE_ORDER):
            p = face.position_offset(pos)
            block = self.chunk.world.get_or_create_chunk_by_position(p).blocks.get(p)

            if block and (
                block.is_solid(face.opposite)
                or (isinstance(block, FenceLikeBlock) and block.may_connect_to(self))
            ):
                self.connected[i] = True
            else:
                self.connected[i] = False

        self.update_render_state()

    def is_solid(self, face: Facing) -> bool:
        return False
