from __future__ import annotations

import abc
import typing

import pyglet.graphics.vertexdomain
from pyglet.math import Vec3

from mcpython.rendering.Models import BlockStateFile
from mcpython.resources.Registry import IRegisterAble, Registry
from mcpython.world.BoundingBox import AABB, IAABB
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
    TRANSPARENT = False
    NO_COLLISION = False
    BOUNDING_BOX: IAABB = AABB(Vec3(0, 0, 0), Vec3(1, 1, 1))
    BLOCk_STATE_LISTING: list[dict[str, str]] = [{}]

    HARDNESS = 8

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
        world.window.invalidate_focused_block()

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

    def on_block_merging(
        self,
        itemstack: ItemStack | None,
        hit_position: tuple[float, float, float] | None = None,
    ) -> bool:
        """
        Called when the player places a block into this block at the given position

        :param itemstack: the ItemStack used, or None
        :param hit_position: the exact position this block was hit at
        :returns: False if the block should be placed / merged, True if the block is merged with this block (-> consumes item)
        """
        return False

    def on_block_starting_to_break(
        self,
        itemstack: ItemStack | None,
        hit_position: tuple[float, float, float] | None,
    ) -> float | None:
        """
        Called when the player starts breaking a block

        :param itemstack: the ItemStack used, or None
        :param hit_position: the exact position this block was hit at, or None
        :returns: the break time in ticks, or None if the block cannot be broken with this itemstack
        """
        return self.HARDNESS if self.BREAKABLE else None

    def on_block_broken(
        self,
        itemstack: ItemStack | None,
        hit_position: tuple[float, float, float] | None,
    ) -> bool | None:
        """
        Called when the player broke a block with the given 'itemstack'

        :param itemstack: the ItemStack used, or None
        :param hit_position: the exact position this block was hit at or None
        :returns: None to let the block breaking happen, False to disallow it, and True to mark that it was handled
            (and accordingly, damage to the item should be delt)
        """
        return None if self.BREAKABLE else False

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
            if self not in self.chunk.block_tick_list:
                self.chunk.block_tick_list.append(self)
        elif self in self.chunk.block_tick_list:
            self.chunk.block_tick_list.remove(self)

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

