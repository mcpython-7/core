from __future__ import annotations

import enum
import typing

from mcpython.containers.ItemStack import ItemStack
from mcpython.world.blocks.AbstractBlock import AbstractBlock, _EMPTY_STATE


class LogAxis(enum.Enum):
    X = 0
    Y = 1
    Z = 2


class LogLikeBlock(AbstractBlock):
    BLOCk_STATE_LISTING = [{"axis": "y"}, {"axis": "x"}, {"axis": "z"}]

    def __init__(self, position: tuple[int, int, int]):
        super().__init__(position)
        self.axis = LogAxis.Y

    def on_block_placed(
        self,
        itemstack: ItemStack,
        onto: tuple[int, int, int] | None = None,
        hit_position: tuple[float, float, float] | None = None,
    ):
        dx, dy, dz = (
            self.position[0] - onto[0],
            self.position[1] - onto[1],
            self.position[2] - onto[2],
        )

        if dy != 0:
            self.axis = LogAxis.Y
        elif dx != 0:
            self.axis = LogAxis.X
        elif dz != 0:
            self.axis = LogAxis.Z
        else:
            self.axis = LogAxis.Y

        self.update_render_state()

    def get_block_state(self) -> dict[str, str]:
        return {"axis": self.axis.name.lower()}

    def set_block_state(self, block_state: dict[str]):
        self.axis = LogAxis[block_state.get("axis", "y").upper()]

    def list_all_block_states(self) -> typing.Iterable[dict[str, str]]:
        yield _EMPTY_STATE
