from __future__ import annotations

import abc
import enum
import typing

import pyglet.graphics.vertexdomain
from pyglet.math import Vec3
from pyglet.window import mouse, key

from mcpython.rendering.Models import BlockStateFile
from mcpython.resources.Registry import IRegisterAble, Registry
from mcpython.world.BoundingBox import AABB, IAABB, AABBGroup
from mcpython.world.serialization.DataBuffer import (
    IBufferSerializableWithVersion,
    ReadBuffer,
    WriteBuffer,
)
from mcpython.world.util import Facing
from mcpython.world.worldgen.WorldgenManager import Structure

if typing.TYPE_CHECKING:
    from mcpython.world.World import Chunk
    from mcpython.containers.ItemStack import ItemStack


_EMPTY_STATE = {}


class AbstractBlock(IRegisterAble, IBufferSerializableWithVersion, abc.ABC):
    NAME: str | None = None
    STATE_FILE: BlockStateFile | None = None
    BREAKABLE = True
    SHOULD_TICK = False
    TRANSPARENT = False
    NO_COLLISION = False
    BOUNDING_BOX: IAABB = AABB(Vec3(0, 0, 0), Vec3(1, 1, 1))

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.NAME is not None and cls.STATE_FILE is None:
            cls.STATE_FILE = BlockStateFile.by_name(cls.NAME)

    @classmethod
    def decode(cls, buffer: ReadBuffer):
        name = buffer.read_string()

        if not name:
            return

        block_type = typing.cast(
            AbstractBlock, BLOCK_REGISTRY.lookup(name, raise_on_error=True)
        )
        obj = cls((0, 0, 0))
        buffer = block_type.decode_datafixable(buffer, obj)
        block_type.inner_decode(obj, buffer)
        return obj

    @classmethod
    def inner_decode(cls, obj: AbstractBlock, buffer: ReadBuffer):
        state = {
            buffer.read_string(): buffer.read_string()
            for _ in range(buffer.read_uint16())
        }
        obj.set_block_state(state)

    def __init__(self, position: tuple[int, int, int]):
        self.position = position
        self.shown = False
        self.vertex_data: list[pyglet.graphics.vertexdomain.VertexList] = []
        self.chunk: Chunk = None

    def get_bounding_box(self) -> IAABB:
        return self.BOUNDING_BOX

    def encode(self, buffer: WriteBuffer):
        buffer.write_string(self.NAME)
        self.encode_datafixable(buffer)
        self.inner_encode(buffer)

    def inner_encode(self, buffer: WriteBuffer):
        state = self.get_block_state()
        buffer.write_uint32(len(state))
        for key, value in state.items():
            buffer.write_string(key)
            buffer.write_string(value)

    def set_block_state(self, state: dict[str, str]):
        pass

    def get_block_state(self) -> dict[str, str]:
        return _EMPTY_STATE

    def get_tint_colors(self) -> list[tuple[float, float, float, float]] | None:
        pass

    def update_render_state(self):
        if not self.shown:
            return

        world = self.chunk.world
        world.hide_block(self)
        world.show_block(self)

    def on_block_added(self):
        pass

    def on_block_loaded(self):
        self.on_block_added()

    def on_block_placed(
        self,
        itemstack: ItemStack | None,
        onto: tuple[int, int, int] | None = None,
        hit_position: tuple[float, float, float] | None = None,
    ) -> bool:
        """
        Called when the block is physically placed in the world by a player-like

        :param itemstack: the ItemStack used, or None
        :param onto: which block this block was placed against, or None
        :param hit_position: the exact position the other block was hit with during ray collision
        :return: False if the placement is prohibited
        """

    def on_block_removed(self):
        pass

    def on_block_updated(self):
        pass

    def on_random_update(self):
        pass

    def on_tick(self):
        """
        Called every tick when loaded and SHOULD_TICK is True

        WARNING: modifying SHOULD_TICK at in-game time is fatal!

        You may call set_ticking(bool) at runtime (ensure that you remove the block when on_block_removed!)
        """

    def set_ticking(self, ticking: bool):
        if ticking:
            if self not in self.chunk.tick_list:
                self.chunk.tick_list.append(self)
        elif self in self.chunk.tick_list:
            self.chunk.tick_list.remove(self)

    def on_block_interaction(
        self, itemstack: ItemStack, button: int, modifiers: int
    ) -> bool:
        """
        Called when the block is interacted with.
        'button' and 'modifiers' are the mouse buttons pressed.
        Should return 'True' if the normal logic should NOT continue.
        """
        return False

    def is_solid(self, face: Facing) -> bool:
        return True

    def __repr__(self):
        return f"{self.__class__.__name__}{self.position}"


BLOCK_REGISTRY = Registry("minecraft:block", AbstractBlock)


@BLOCK_REGISTRY.register
class Sand(AbstractBlock):
    NAME = "minecraft:sand"
    STATE_FILE = BlockStateFile.by_name(NAME)

    def __init__(self, position):
        super().__init__(position)
        self.falling = False
        self.ticks_to_fall = 3

    def on_block_updated(self):
        if self.falling:
            return

        from mcpython.world.World import World

        block = self.chunk.blocks.get(
            (
                self.position[0],
                self.position[1] - 1,
                self.position[2],
            )
        )

        if not block or (isinstance(block, Sand) and block.falling):
            self.set_ticking(True)
            self.ticks_to_fall = 3
            self.falling = True
            if block:
                block.on_block_updated()

    def on_tick(self):
        if not self.falling:
            self.set_ticking(False)
            return

        self.ticks_to_fall -= 1
        if self.ticks_to_fall <= 0:
            self.fall()

    def fall(self):
        self.falling = False

        if (
            self.chunk.blocks.get(self.position, None) is self
            and (
                self.position[0],
                self.position[1] - 1,
                self.position[2],
            )
            not in self.chunk.blocks
        ):
            self.chunk.world.INSTANCE.remove_block(self.position, block_update=False)
            old_pos = self.position
            if self.position[1] > -20:
                self.chunk.add_block(
                    (self.position[0], self.position[1] - 1, self.position[2]), self
                )
            else:
                self.set_ticking(False)
            self.chunk.world.send_block_update(old_pos)
        else:
            self.set_ticking(False)


class LogAxis(enum.Enum):
    X = 0
    Y = 1
    Z = 2


class LogLikeBlock(AbstractBlock):
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


class FenceLikeBlock(AbstractBlock):
    FACE_ORDER: list[Facing] = list(Facing)[2:]

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


class SlabLikeBlock(AbstractBlock):
    TOP_BOUNDING_BOX = AABB(Vec3(0, 0.5, 0), Vec3(1, 0.5, 1))
    BOTTOM_BOUNDING_BOX = AABB(Vec3(0, 0, 0), Vec3(1, 0.5, 1))

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
            print(hit_position, self.position, hit_position[1] < self.position[1])

            if hit_position[1] < self.position[1]:
                self.half = SlabLikeBlock.SlabHalf.BOTTOM
            else:
                self.half = SlabLikeBlock.SlabHalf.TOP

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


class GrowToStructureBlock(AbstractBlock):
    STRUCTURE: Structure = None
    GROWTH_STAGES = 3

    def __init__(self, position: tuple[int, int, int]):
        super().__init__(position)
        self.pending_growth = self.GROWTH_STAGES

    def on_random_update(self):
        if self.pending_growth == 0:
            return

        self.pending_growth -= 1
        if self.pending_growth == 0:
            self.grow()

    def inner_encode(self, buffer: WriteBuffer):
        super().inner_encode(buffer)
        buffer.write_uint8(self.pending_growth)

    @classmethod
    def inner_decode(cls, obj: GrowToStructureBlock, buffer: ReadBuffer):
        super().inner_decode(obj, buffer)
        obj.pending_growth = buffer.read_uint8()

    def grow(self):
        if self.STRUCTURE:
            self.STRUCTURE.place(self.chunk.world, self.position)


@BLOCK_REGISTRY.register
class Bedrock(AbstractBlock):
    NAME = "minecraft:bedrock"
    BREAKABLE = False


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


@BLOCK_REGISTRY.register
class GrassBlock(AbstractBlock):
    NAME = "minecraft:grass_block"

    def get_block_state(self) -> dict[str, str]:
        return {"snowy": "false"}

    def get_tint_colors(self) -> list[tuple[float, float, float, float]] | None:
        return [(145 / 255, 189 / 255, 89 / 255, 1)]


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

    def on_block_updated(self):
        x, y, z = self.position
        block = self.chunk.blocks.get((x, y - 1, z))
        if block is None or not block.is_solid(Facing.UP):
            self.chunk.remove_block(self)
