from __future__ import annotations

import random
import time
import typing
from collections import deque

import pyglet
from pyglet.math import Vec3

from mcpython.config import TICKS_PER_SEC
from mcpython.rendering.util import (
    FACES,
)
from mcpython.world.util import normalize, sectorize
from mcpython.world.blocks.AbstractBlock import (
    AbstractBlock,
    BLOCK_REGISTRY,
)


class World:
    INSTANCE: World = None

    def __init__(self):
        World.INSTANCE = self

        # A Batch is a collection of vertex lists for batched rendering.
        self.batch = pyglet.graphics.Batch()

        # A mapping from position to the texture of the block at that position.
        # This defines all the blocks that are currently in the world.
        self.world: dict[tuple[int, int, int], AbstractBlock] = {}

        # Mapping from sector to a list of positions inside that sector.
        self.sectors: dict[tuple[int, int], list[tuple[int, int, int]]] = {}

        # Simple function queue implementation. The queue is populated with
        # _show_block() and _hide_block() calls
        self.queue = deque()

        self._initialize()

    def _initialize(self):
        """Initialize the world by placing all the blocks."""
        n = 100  # 1/2 width and height of world
        s = 1  # step size
        y = 0  # initial y height
        for x in range(-n, n + 1, s):
            for z in range(-n, n + 1, s):
                # create a layer stone a grass everywhere.
                self.add_block(
                    (x, y - 2, z), "minecraft:dirt", immediate=False, block_update=False
                )
                self.add_block(
                    (x, y - 3, z),
                    "minecraft:bedrock",
                    immediate=False,
                    block_update=False,
                )
                if x in (-n, n) or z in (-n, n):
                    # create outer walls.
                    for dy in range(-2, 3):
                        self.add_block(
                            (x, y + dy, z),
                            "minecraft:bedrock",
                            immediate=False,
                            block_update=False,
                        )

        blocks = list(
            filter(lambda e: e.BREAKABLE, list(BLOCK_REGISTRY._registry.values()))
        )

        # generate the hills randomly
        o = n - 10
        for _ in range(120):
            a = random.randint(-o, o)  # x position of the hill
            b = random.randint(-o, o)  # z position of the hill
            c = -1  # base of the hill
            h = random.randint(1, 6)  # height of the hill
            s = random.randint(4, 8)  # 2 * s is the side length of the hill
            d = 1  # how quickly to taper off the hills
            t = random.choice(blocks)
            for y in range(c, c + h):
                for x in range(a - s, a + s + 1):
                    for z in range(b - s, b + s + 1):
                        if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
                            continue
                        if (x - 0) ** 2 + (z - 0) ** 2 < 5**2:
                            continue
                        self.add_block(
                            (x, y, z), t, immediate=False, block_update=False
                        )
                s -= d  # decrement side length so hills taper off

    def hit_test(
        self,
        position: Vec3,
        vector: Vec3,
        max_distance=8,
    ) -> tuple[tuple[int, int, int], tuple[int, int, int]] | tuple[None, None]:
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
            if key != previous and key in self.world:
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None

    def exposed(self, position: tuple[int, int, int]) -> bool:
        """Returns False is given `position` is surrounded on all 6 sides by
        blocks, True otherwise.

        """
        x, y, z = position
        for dx, dy, dz in FACES:
            if (x + dx, y + dy, z + dz) not in self.world:
                return True
        return False

    def add_block(
        self,
        position: tuple[int, int, int],
        block_type: type[AbstractBlock] | AbstractBlock | str,
        immediate=True,
        block_update=True,
    ):
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
        if position in self.world:
            self.remove_block(position, immediate)

        if isinstance(block_type, AbstractBlock):
            instance = block_type
            instance.position = position
        elif isinstance(block_type, str):
            block_type = BLOCK_REGISTRY.lookup(block_type, raise_on_error=True)
            instance = block_type(position)
        else:
            instance = block_type(position)

        self.world[position] = instance
        self.sectors.setdefault(sectorize(position), []).append(position)
        if immediate:
            if self.exposed(position):
                self.show_block(instance)
            self.check_neighbors(position)
        instance.on_block_added()

        if block_update:
            instance.on_block_updated(self)
            self.send_block_update(position)

    def remove_block(
        self,
        position: tuple[int, int, int],
        immediate=True,
        block_update=True,
    ):
        """Remove the block at the given `position`.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to remove.
        immediate : bool
            Whether or not to immediately remove block from canvas.

        """
        instance = self.world[position]
        del self.world[position]
        self.sectors[sectorize(position)].remove(position)
        if immediate:
            if instance.shown:
                self.hide_block(instance)
            self.check_neighbors(position)
        instance.on_block_removed()
        if block_update:
            self.send_block_update(position)

    def check_neighbors(self, position: tuple[int, int, int]):
        """Check all blocks surrounding `position` and ensure their visual
        state is current. This means hiding blocks that are not exposed and
        ensuring that all exposed blocks are shown. Usually used after a block
        is added or removed.

        """
        x, y, z = position
        for dx, dy, dz in FACES:
            key = (x + dx, y + dy, z + dz)
            if key not in self.world:
                continue
            instance = self.world[key]
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
            if key not in self.world:
                continue
            instance = self.world[key]
            instance.on_block_updated(self)

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

    def show_sector(self, sector: tuple[int, int]):
        """Ensure all blocks in the given sector that should be shown are
        drawn to the canvas.

        """
        for position in self.sectors.get(sector, []):
            instance = self.world[position]
            if not instance.shown and self.exposed(position):
                self.show_block(instance, False)

    def hide_sector(self, sector: tuple[int, int]):
        """Ensure all blocks in the given sector that should be hidden are
        removed from the canvas.

        """
        for position in self.sectors.get(sector, []):
            instance = self.world[position]
            if instance.shown:
                self.hide_block(instance, False)

    def change_sectors(self, before: tuple[int, int], after: tuple[int, int]):
        """Move from sector `before` to sector `after`. A sector is a
        contiguous x, y sub-region of world. Sectors are used to speed up
        world rendering.

        """
        before_set: set[tuple[int, int]] = set()
        after_set: set[tuple[int, int]] = set()
        pad = 4
        for dx in range(-pad, pad + 1):
            for dy in [0]:  # range(-pad, pad + 1):
                for dz in range(-pad, pad + 1):
                    if dx**2 + dy**2 + dz**2 > (pad + 1) ** 2:
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
            self.show_sector(sector)
        for sector in hide:
            self.hide_sector(sector)

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
