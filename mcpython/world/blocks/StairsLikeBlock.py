from __future__ import annotations

import enum
import itertools

from pyglet.math import Vec3

from mcpython.containers.ItemStack import ItemStack
from mcpython.world.BoundingBox import IAABB, AABBGroup, AABB
from mcpython.world.blocks.AbstractBlock import AbstractBlock
from mcpython.world.util import Facing


class StairsLikeBlock(AbstractBlock):
    class StairHalf(enum.Enum):
        TOP = 0
        BOTTOM = 1

    class StairShape(enum.Enum):
        STRAIGHT = 0
        INNER_LEFT = 1
        INNER_RIGHT = 2
        OUTER_LEFT = 3
        OUTER_RIGHT = 4

    # fmt: off
    BOX_VARIANTS: dict[tuple[StairHalf, Facing, StairShape], IAABB] = {
        (StairHalf.TOP, Facing.NORTH, StairShape.STRAIGHT): AABBGroup().add_box(AABB(Vec3(0, 0.5, 0), Vec3(1, 0.5, 1))).add_box(AABB(Vec3(0, 0, 0), Vec3(1, 0.5, 0.5))),
        (StairHalf.TOP, Facing.EAST, StairShape.STRAIGHT): AABBGroup().add_box(AABB(Vec3(0, 0.5, 0), Vec3(1, 0.5, 1))).add_box(AABB(Vec3(0.5, 0, 0), Vec3(0.5, 0.5, 1))),
        (StairHalf.TOP, Facing.SOUTH, StairShape.STRAIGHT): AABBGroup().add_box(AABB(Vec3(0, 0.5, 0), Vec3(1, 0.5, 1))).add_box(AABB(Vec3(0, 0, 0.5), Vec3(1, 0.5, 0.5))),
        (StairHalf.TOP, Facing.WEST, StairShape.STRAIGHT): AABBGroup().add_box(AABB(Vec3(0, 0.5, 0), Vec3(1, 0.5, 1))).add_box(AABB(Vec3(0, 0, 0), Vec3(0.5, 0.5, 1))),

        (StairHalf.BOTTOM, Facing.SOUTH, StairShape.STRAIGHT): AABBGroup().add_box(AABB(Vec3(0, 0, 0), Vec3(1, 0.5, 1))).add_box(AABB(Vec3(0, 0.5, 0), Vec3(1, 0.5, 0.5))),
        (StairHalf.BOTTOM, Facing.EAST, StairShape.STRAIGHT): AABBGroup().add_box(AABB(Vec3(0, 0, 0), Vec3(1, 0.5, 1))).add_box(AABB(Vec3(0.5, 0.5, 0), Vec3(0.5, 0.5, 1))),
        (StairHalf.BOTTOM, Facing.NORTH, StairShape.STRAIGHT): AABBGroup().add_box(AABB(Vec3(0, 0, 0), Vec3(1, 0.5, 1))).add_box(AABB(Vec3(0, 0.5, 0.5), Vec3(1, 0.5, 0.5))),
        (StairHalf.BOTTOM, Facing.WEST, StairShape.STRAIGHT): AABBGroup().add_box(AABB(Vec3(0, 0, 0), Vec3(1, 0.5, 1))).add_box(AABB(Vec3(0, 0.5, 0), Vec3(0.5, 0.5, 1))),
    }
    # fmt: on
    BLOCk_STATE_LISTING = [
        {
            "half": half.name.lower(),
            "facing": facing.name.lower(),
            "shape": shape.name.lower(),
        }
        for half, facing, shape in itertools.product(
            StairHalf, list(Facing)[3:], StairShape
        )
    ]

    def __init__(self, position: tuple[int, int, int]):
        super().__init__(position)
        self.half = StairsLikeBlock.StairHalf.TOP
        self.facing = Facing.NORTH
        self.shape = StairsLikeBlock.StairShape.STRAIGHT

    def get_bounding_box(self) -> IAABB:
        return self.BOX_VARIANTS.get(
            (self.half, self.facing, self.shape), self.BOUNDING_BOX
        )

    def get_block_state(self) -> dict[str, str]:
        return {
            "facing": self.facing.name.lower(),
            "half": self.half.name.lower(),
            "shape": self.shape.name.lower(),
        }

    def set_block_state(self, state: dict[str, str]):
        self.facing = Facing[state.get("facing", "north").upper()]
        self.half = StairsLikeBlock.StairHalf[state.get("half", "top").upper()]
        self.shape = StairsLikeBlock.StairShape[state.get("shape", "straight").upper()]

    def is_solid(self, face: Facing) -> bool:
        if face == Facing.UP:
            return self.half == StairsLikeBlock.StairHalf.BOTTOM

        elif face == Facing.DOWN:
            return self.half == StairsLikeBlock.StairHalf.TOP

        elif self.shape in [
            StairsLikeBlock.StairShape.INNER_LEFT,
            StairsLikeBlock.StairShape.INNER_RIGHT,
        ]:
            return False

        elif face == Facing.NORTH:
            return (
                self.facing == Facing.NORTH
                or (
                    self.facing == Facing.EAST
                    and self.shape == StairsLikeBlock.StairShape.OUTER_LEFT
                )
                or (
                    self.facing == Facing.WEST
                    and self.shape == StairsLikeBlock.StairShape.OUTER_RIGHT
                )
            )
        elif face == Facing.SOUTH:
            return (
                self.facing == Facing.SOUTH
                or (
                    self.facing == Facing.WEST
                    and self.shape == StairsLikeBlock.StairShape.OUTER_LEFT
                )
                or (
                    self.facing == Facing.EAST
                    and self.shape == StairsLikeBlock.StairShape.OUTER_RIGHT
                )
            )
        elif face == Facing.EAST:
            return (
                self.facing == Facing.SOUTH.EAST
                or (
                    self.facing == Facing.NORTH
                    and self.shape == StairsLikeBlock.StairShape.OUTER_LEFT
                )
                or (
                    self.facing == Facing.SOUTH
                    and self.shape == StairsLikeBlock.StairShape.OUTER_RIGHT
                )
            )
        elif face == Facing.WEST:
            return (
                self.facing == Facing.SOUTH.WEST
                or (
                    self.facing == Facing.SOUTH
                    and self.shape == StairsLikeBlock.StairShape.OUTER_LEFT
                )
                or (
                    self.facing == Facing.NORTH
                    and self.shape == StairsLikeBlock.StairShape.OUTER_RIGHT
                )
            )
        else:
            return False

    def on_block_placed(
        self,
        itemstack: ItemStack,
        onto: tuple[int, int, int] | None = None,
        hit_position: tuple[float, float, float] | None = None,
    ):
        if hit_position is None:
            return

        dx, dy, dz = (
            self.position[0] - hit_position[0],
            self.position[1] - hit_position[1],
            self.position[2] - hit_position[2],
        )

        self.half = (
            StairsLikeBlock.StairHalf.TOP
            if dy < 0
            else StairsLikeBlock.StairHalf.BOTTOM
        )

        if abs(dx) > abs(dz):
            self.facing = Facing.WEST if dx > 0 else Facing.EAST
        else:
            self.facing = Facing.NORTH if dz > 0 else Facing.SOUTH
            if self.half == StairsLikeBlock.StairHalf.BOTTOM:
                self.facing = self.facing.opposite

    def on_block_updated(self):
        pass
