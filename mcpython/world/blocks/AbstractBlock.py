from __future__ import annotations

import abc
import enum
import random
import typing

import pyglet.graphics.vertexdomain

from mcpython.rendering.Models import BlockStateFile
from mcpython.resources.Registry import IRegisterAble, Registry
from mcpython.world.serialization.DataBuffer import (
    IBufferSerializableWithVersion,
    ReadBuffer,
    WriteBuffer,
)

if typing.TYPE_CHECKING:
    from mcpython.world.items.AbstractItem import AbstractItem
    from mcpython.containers.ItemStack import ItemStack


_EMPTY_STATE = {}


class AbstractBlock(IRegisterAble, IBufferSerializableWithVersion, abc.ABC):
    NAME: str | None = None
    STATE_FILE: BlockStateFile | None = None
    BREAKABLE = True

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

        from mcpython.rendering.Window import Window

        world = Window.INSTANCE.world
        world.hide_block(self)
        world.show_block(self)

    def on_block_added(self):
        pass

    def on_block_loaded(self):
        self.on_block_added()

    def on_block_placed(self, itemstack: ItemStack, onto: tuple[int, int, int]):
        pass

    def on_block_removed(self):
        pass

    def on_block_updated(self, world):
        pass

    def on_block_interaction(
        self, itemstack: ItemStack, button: int, modifiers: int
    ) -> bool:
        """
        Called when the block is interacted with.
        'button' and 'modifiers' are the mouse buttons pressed.
        Should return 'True' if the normal logic should NOT continue.
        """
        return False

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

    def on_block_updated(self, world):
        from mcpython.world.World import World

        chunk = World.INSTANCE.get_or_create_chunk(self.position)

        if (
            self.position[0],
            self.position[1] - 1,
            self.position[2],
        ) not in chunk.blocks:
            pyglet.clock.schedule_once(self.fall, 0.5)
            self.falling = True

    def fall(self, _):
        from mcpython.world.World import World

        self.falling = False

        chunk = World.INSTANCE.get_or_create_chunk(self.position)

        if (
            chunk.blocks.get(self.position, None) is self
            and (
                self.position[0],
                self.position[1] - 1,
                self.position[2],
            )
            not in chunk.blocks
        ):
            World.INSTANCE.remove_block(self.position, block_update=False)
            old_pos = self.position
            World.INSTANCE.add_block(
                (self.position[0], self.position[1] - 1, self.position[2]), self
            )
            World.INSTANCE.send_block_update(old_pos)


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
        print(dx, dy, dz)

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
    FACE_ORDER = ["north", "east", "south", "west"]

    def __init__(self, position: tuple[int, int, int]):
        super().__init__(position)
        self.connected = [False, False, False, False]

    def get_block_state(self) -> dict[str, str]:
        return {
            face: str(state).lower()
            for face, state in zip(self.FACE_ORDER, self.connected)
        }

    def set_block_state(self, state: dict[str, str]):
        for face, state in state.items():
            self.connected[self.FACE_ORDER.index(face)] = state == "true"

    def on_block_updated(self, world):
        self.connected = random.choices([False, True], k=6)
        self.update_render_state()


@BLOCK_REGISTRY.register
class Bedrock(AbstractBlock):
    NAME = "minecraft:bedrock"
    BREAKABLE = False
