from __future__ import annotations

import itertools
import random
import sys
import time
import typing
from collections import deque

import pyglet
from pyglet.math import Vec3

from mcpython.config import TICKS_PER_SEC
from mcpython.rendering.util import (
    FACES,
)
from mcpython.world.serialization.DataBuffer import (
    IBufferSerializableWithVersion,
    ReadBuffer,
    WriteBuffer,
)
from mcpython.world.serialization.WorldStorage import WorldStorage
from mcpython.world.util import normalize, sectorize, Facing
from mcpython.world.blocks.AbstractBlock import (
    AbstractBlock,
    BLOCK_REGISTRY,
)
from mcpython.world.worldgen.WorldgenManager import generate_chunk


class Chunk(IBufferSerializableWithVersion):
    @classmethod
    def decode(cls, buffer: ReadBuffer):
        raise RuntimeError("use decode_instance() instead")

    def __init__(self, world: World, position: tuple[int, int]):
        self.world = world
        self.position = position
        self.blocks: dict[tuple[int, int, int], AbstractBlock] = {}
        self.shown = False
        self.tick_list: list[AbstractBlock] = []

    def tick(self):
        for block in self.tick_list:
            block.on_tick()

    def decode_instance(self, buffer: ReadBuffer):
        sector = buffer.read_int32(), buffer.read_int32()
        if sector != self.position:
            raise RuntimeError("wrong chunk")

        buffer = self.decode_datafixable(buffer, self)
        count = buffer.read_uint32()
        dx, dz = sector[0] * 16, sector[1] * 16
        for _ in range(count):
            px = buffer.read_uint8()
            py = buffer.read_uint16()
            pz = buffer.read_uint8()
            pos = px + dx, py, pz + dz
            block = AbstractBlock.decode(buffer)

            if block is not None:
                block.position = pos
                self.blocks[pos] = block

        for block in self.blocks.values():
            block.on_block_loaded()

    def encode(self, buffer: WriteBuffer):
        buffer.write_int32(self.position[0])
        buffer.write_int32(self.position[1])
        self.encode_datafixable(buffer)
        buffer.write_uint32(len(self.blocks))
        dx, dz = self.position[0] * 16, self.position[1] * 16
        for pos, instance in self.blocks.items():
            buffer.write_uint8(pos[0] - dx)
            buffer.write_int16(pos[1])
            buffer.write_uint8(pos[2] - dz)
            instance.encode(buffer)

    def __repr__(self):
        return f"Chunk({self.position[0]}, {self.position[1]}, {len(self.blocks)} blocks, visible={self.shown})"

    def show(self, immediate=True, force=False):
        if self.shown and not force:
            return

        self.shown = True

        for position, instance in self.blocks.items():
            if not instance.shown and self.world.exposed(position):
                self.world.show_block(instance, immediate)

    def hide(self, immediate=True, force=False):
        if not self.shown and not force:
            return

        self.shown = False

        for position, instance in self.blocks.items():
            if instance.shown:
                self.world.hide_block(instance, immediate)

    def add_block(
        self,
        position: tuple[int, int, int],
        block_type: type[AbstractBlock] | AbstractBlock | str,
        immediate=True,
        block_update=True,
        block_added_parms=(),
    ) -> AbstractBlock | None:
        """Add a block with the given `texture` and `position` to the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to add.
        block_type :
            The block type to use
        immediate : bool
            Whether or not to draw the block immediately.

        """
        if position in self.blocks:
            self.remove_block(position, immediate, block_update=block_update)

        if isinstance(block_type, AbstractBlock):
            instance = block_type
            instance.position = position

        elif isinstance(block_type, str):
            block_type = BLOCK_REGISTRY.lookup(block_type, raise_on_error=True)
            instance = block_type(position)

        else:
            instance = block_type(position)

        self.blocks[position] = instance
        instance.chunk = self

        instance.on_block_added(*block_added_parms)

        if immediate:
            if self.shown and self.world.exposed(position):
                self.world.show_block(instance)
            self.world.check_neighbors(position)

        if block_update:
            instance.on_block_updated()
            self.world.send_block_update(position)

        if instance.SHOULD_TICK:
            self.tick_list.append(instance)

        return instance

    def remove_block(
        self,
        position: tuple[int, int, int] | AbstractBlock,
        immediate=True,
        block_update=True,
    ) -> AbstractBlock | None:
        """Remove the block at the given `position`.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to remove.
        immediate : bool
            Whether or not to immediately remove block from canvas.

        """
        if isinstance(position, AbstractBlock):
            position = position.position

        if position not in self.blocks:
            return

        instance = self.blocks[position]
        del self.blocks[position]

        if immediate:
            if instance.shown:
                self.world.hide_block(instance)
            self.world.check_neighbors(position)

        instance.on_block_removed()
        if block_update:
            self.world.send_block_update(position)

        if instance.SHOULD_TICK:
            try:
                self.tick_list.remove(instance)
            except ValueError:
                print(
                    f"WARN: block {instance} is in the world and was scheduled to be ticked, but is not registered for ticking!",
                    file=sys.stderr,
                )

        return instance


class World:
    INSTANCE: World = None

    def __init__(self):
        World.INSTANCE = self

        self.storage = WorldStorage()

        # A Batch is a collection of vertex lists for batched rendering.
        self.batch = pyglet.graphics.Batch()

        self.chunks: dict[tuple[int, int], Chunk] = {}

        # Simple function queue implementation. The queue is populated with
        # _show_block() and _hide_block() calls
        self.queue = deque()

        self._initialize()

    def tick(self):
        for chunk in self.chunks.values():
            chunk.tick()

    def get_or_create_chunk_by_position(
        self, position: tuple[int, int, int] | tuple[int, int]
    ) -> Chunk:
        c = position[0] // 16, position[-1] // 16
        chunk = self.chunks.get(c)
        if chunk is None:
            chunk = self.chunks[c] = Chunk(self, c)
        return chunk

    def get_or_create_chunk_by_coord(self, coord: tuple[int, int]):
        chunk = self.chunks.get(coord)
        if chunk is None:
            chunk = self.chunks[coord] = Chunk(self, coord)
        return chunk

    def _initialize(self):
        """Initialize the world by placing all the blocks."""

        for cx, cz in itertools.product(range(-3, 4), range(-3, 4)):
            generate_chunk(self.get_or_create_chunk_by_coord((cx, cz)))

        self.ensure_chunks_shown()

    def hit_test(
        self,
        position: Vec3,
        vector: Vec3,
        max_distance=8,
    ) -> (
        tuple[tuple[int, int, int], tuple[int, int, int], tuple[float, float, float]]
        | tuple[None, None, None]
    ):
        """Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return None, None.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check visibility from.
        vector : tuple of len 3
            The line of sight vector.
        max_distance : int
            How many blocks away to search for a hit.

        """
        m = 8
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in range(max_distance * m):
            key = normalize((x, y, z))

            if (
                key != previous
                and key in self.get_or_create_chunk_by_position(key).blocks
            ):
                return key, previous, (x, y, z)

            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None, None

    def exposed(self, position: tuple[int, int, int]) -> bool:
        """Returns False is given `position` is surrounded on all 6 sides by
        blocks, True otherwise.

        """
        for face in Facing:
            pos = face.position_offset(position)
            block = self.get_or_create_chunk_by_position(pos).blocks.get(pos)
            if not block or not block.is_solid(face):
                return True

        return False

    def add_block(
        self,
        position: tuple[int, int, int],
        block_type: type[AbstractBlock] | AbstractBlock | str,
        immediate=True,
        block_update=True,
        block_added_parms=(),
    ) -> AbstractBlock:
        """Add a block with the given `texture` and `position` to the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to add.
        block_type :
            The block type to use
        immediate : bool
            Whether or not to draw the block immediately.

        """
        chunk = self.get_or_create_chunk_by_position(position)
        return chunk.add_block(
            position,
            block_type,
            immediate,
            block_update=block_update,
            block_added_parms=block_added_parms,
        )

    def remove_block(
        self,
        position: tuple[int, int, int] | AbstractBlock,
        immediate=True,
        block_update=True,
    ) -> AbstractBlock | None:
        """Remove the block at the given `position`.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to remove.
        immediate : bool
            Whether or not to immediately remove block from canvas.

        """
        chunk = self.get_or_create_chunk_by_position(position)
        return chunk.remove_block(
            position, immediate=immediate, block_update=block_update
        )

    def check_neighbors(self, position: tuple[int, int, int]):
        """Check all blocks surrounding `position` and ensure their visual
        state is current. This means hiding blocks that are not exposed and
        ensuring that all exposed blocks are shown. Usually used after a block
        is added or removed.

        """
        x, y, z = position
        for dx, dy, dz in FACES:
            key = (x + dx, y + dy, z + dz)
            chunk = self.get_or_create_chunk_by_position(key)
            if key not in chunk.blocks:
                continue
            instance = chunk.blocks[key]
            if self.exposed(key):
                if not instance.shown:
                    self.show_block(instance)
            else:
                if instance.shown:
                    self.hide_block(instance)

    def send_block_update(self, position: tuple[int, int, int]):
        x, y, z = position
        for dx, dy, dz in FACES:
            key = (x + dx, y + dy, z + dz)
            chunk = self.get_or_create_chunk_by_position(key)
            if key not in chunk.blocks:
                continue
            instance = chunk.blocks[key]
            instance.on_block_updated()

    def show_block(self, instance: AbstractBlock, immediate=True):
        """Show the block at the given `position`. This method assumes the
        block has already been added with add_block()

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        immediate : bool
            Whether or not to show the block immediately.

        """
        instance.shown = True
        if immediate:
            self._show_block(instance)
        else:
            self._enqueue(self._show_block, instance)

    def _show_block(self, instance: AbstractBlock):
        """Private implementation of the `show_block()` method.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        instance:
            The block instance

        """
        instance.vertex_data = instance.STATE_FILE.create_vertex_list(
            self.batch, instance.position, instance.get_block_state()
        )

    def hide_block(self, instance: AbstractBlock, immediate=True):
        """Hide the block at the given `position`. Hiding does not remove the
        block from the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to hide.
        immediate : bool
            Whether or not to immediately remove the block from the canvas.

        """
        instance.shown = False
        if immediate:
            self._hide_block(instance)
        else:
            self._enqueue(self._hide_block, instance)

    def _hide_block(self, instance: AbstractBlock):
        """Private implementation of the 'hide_block()` method."""
        for element in instance.vertex_data:
            element.delete()
        instance.vertex_data = None

    def show_chunk(self, sector: tuple[int, int] | Chunk):
        """Ensure all blocks in the given sector that should be shown are
        drawn to the canvas.

        """
        chunk = self.chunks.get(sector) if isinstance(sector, tuple) else sector

        if chunk is None and isinstance(sector, tuple):
            chunk = self.chunks[sector] = Chunk(self, sector)

        chunk.show(immediate=False)

    def hide_chunk(self, sector: tuple[int, int] | Chunk):
        """Ensure all blocks in the given sector that should be hidden are
        removed from the canvas.

        """
        chunk = self.chunks.get(sector) if isinstance(sector, tuple) else sector

        if chunk is None and isinstance(sector, tuple):
            chunk = self.chunks[sector] = Chunk(self, sector)

        chunk.hide(immediate=False)

    def ensure_chunks_shown(self):
        pad = 4  # chunk range

        for dx, dz in itertools.product(range(-pad, pad + 1), range(-pad, pad + 1)):
            if dx**2 + dz**2 > (pad + 1) ** 2:
                continue

            self.show_chunk((dx, dz))

    def change_chunks(self, before: tuple[int, int], after: tuple[int, int]):
        """Move from sector `before` to sector `after`. A sector is a
        contiguous x, y sub-region of world. Sectors are used to speed up
        world rendering.

        """
        before_set: set[tuple[int, int]] = set()
        after_set: set[tuple[int, int]] = set()
        pad = 4  # chunk range

        for dx, dz in itertools.product(range(-pad, pad + 1), range(-pad, pad + 1)):
            if dx**2 + dz**2 > (pad + 1) ** 2:
                continue

            if before:
                x, z = before
                before_set.add((x + dx, z + dz))

            if after:
                x, z = after
                after_set.add((x + dx, z + dz))

        show = after_set - before_set
        hide = before_set - after_set
        for sector in show:
            self.show_chunk(sector)

        for sector in hide:
            self.hide_chunk(sector)

    def _enqueue(self, func: typing.Callable, *args):
        """Add `func` to the internal queue."""
        self.queue.append((func, args))

    def _dequeue(self):
        """Pop the top function from the internal queue and call it."""
        func, args = self.queue.popleft()
        func(*args)

    def process_queue(self):
        """Process the entire queue while taking periodic breaks. This allows
        the game loop to run smoothly. The queue contains calls to
        _show_block() and _hide_block() so this method should be called if
        add_block() or remove_block() was called with immediate=False

        """
        start = time.perf_counter()
        while self.queue and time.perf_counter() - start < 1.0 / TICKS_PER_SEC:
            self._dequeue()

    def process_entire_queue(self):
        """Process the entire queue with no breaks."""
        while self.queue:
            self._dequeue()
