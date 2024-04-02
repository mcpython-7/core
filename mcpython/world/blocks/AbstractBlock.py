from __future__ import annotations

import abc
import enum
import random
import typing

import pyglet.graphics.vertexdomain
from pyglet.window import mouse, key

from mcpython.rendering.Models import BlockStateFile
from mcpython.resources.Registry import IRegisterAble, Registry
from mcpython.world.serialization.DataBuffer import (
    IBufferSerializableWithVersion,
    ReadBuffer,
    WriteBuffer,
)
from mcpython.world.util import Facing

if typing.TYPE_CHECKING:
    from mcpython.world.World import Chunk
    from mcpython.containers.ItemStack import ItemStack


_EMPTY_STATE = {}


class AbstractBlock(IRegisterAble, IBufferSerializableWithVersion, abc.ABC):
    NAME: str | None = None
    STATE_FILE: BlockStateFile | None = None
    BREAKABLE = True
    SHOULD_TICK = False

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.NAME is not None and cls.STATE_FILE is None:
            cls.STATE_FILE = BlockStateFile.by_name(cls.NAME)

    @classmethod
    def decode(cls, buffer: ReadBuffer):
        name = buffer.read_string()

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

    def update_render_state(self):
        if not self.shown:
            return

        world = self.chunk.world
        world.hide_block(self)
        world.show_block(self)

    def on_block_added(self, hit_position: tuple[float, float, float] = None):
        pass

    def on_block_loaded(self):
        self.on_block_added()

    def on_block_placed(self, itemstack: ItemStack, onto: tuple[int, int, int]):
        pass

    def on_block_removed(self):
        pass

    def on_block_updated(self):
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
                self.chunk.world.add_block(
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

    def on_block_placed(self, itemstack: ItemStack, onto: tuple[int, int, int]):
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
            block = self.chunk.world.get_or_create_chunk(p).blocks.get(p)

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
    class SlabHalf(enum.Enum):
        TOP = 0
        BOTTOM = 1
        DOUBLE = 2

    def __init__(self, position: tuple[int, int, int]):
        super().__init__(position)
        self.half: SlabLikeBlock.SlabHalf = self.SlabHalf.TOP

    def on_block_added(self, hit_position: tuple[float, float, float] = None):
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
            or (self.half == SlabLikeBlock.SlabHalf.BOTTOM and face == Facing.TOP)
            or (self.half == SlabLikeBlock.SlabHalf.TOP and face == Facing.BOTTOM)
        )


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
