from __future__ import annotations

import itertools
import math

from pyglet.math import Vec3

from mcpython.commands.Chat import Chat
from mcpython.containers.AbstractContainer import Slot, ItemInformationScreen
from mcpython.containers.PlayerInventoryContainer import (
    PlayerInventoryContainer,
    HotbarContainer,
)
from mcpython.world.blocks.AbstractBlock import AbstractBlock
from mcpython.world.entity.AbstractEntity import AbstractEntity
from mcpython.world.util import normalize


class PlayerEntity(AbstractEntity):
    NAME = "minecraft:player"

    def __init__(self, world, pos, rot):
        super().__init__(world, pos, rot)
        self.rotation = (0, 0)
        self.strafe = [0, 0]
        self.flying = False

        self.inventory = PlayerInventoryContainer()
        self.hotbar = HotbarContainer(self.inventory)
        self.hotbar.show_container()
        self.chat = Chat()

        self.slot_hover_info = ItemInformationScreen()

        self.moving_player_slot = Slot(
            self.inventory, (0, 0), on_update=self._update_moving_slot
        )

        self.breaking_block: AbstractBlock | None = None
        self.breaking_block_timer: float | None = None
        self.breaking_block_total_timer: float | None = None
        self.breaking_block_position: tuple[float, float, float] | None = None

        self.breaking_block_provider = None

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
            self.world.show_chunk(sector)

        for sector in hide:
            self.world.hide_chunk(sector)

    def _update_moving_slot(self, slot, old_stack):
        if not slot.itemstack.is_empty():
            self.slot_hover_info.bind_to_slot(slot)
        else:
            self.slot_hover_info.bind_to_slot(None)

    def get_sight_vector(self) -> Vec3:
        """Returns the current line of sight vector indicating the direction
        the player is looking.

        """
        x, y = self.rotation
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return Vec3(dx, dy, dz)

    def get_motion_vector(self) -> tuple[float, float, float]:
        """Returns the current motion vector indicating the velocity of the
        player.

        Returns
        -------
        vector : tuple of len 3
            Tuple containing the velocity in x, y, and z respectively.

        """
        if any(self.strafe):
            x, y = self.rotation
            strafe = math.degrees(math.atan2(*self.strafe))
            y_angle = math.radians(y)
            x_angle = math.radians(x + strafe)
            if self.flying:
                m = math.cos(y_angle)
                dy = math.sin(y_angle)
                if self.strafe[1]:
                    # Moving left or right.
                    dy = 0.0
                    m = 1
                if self.strafe[0] > 0:
                    # Moving backwards.
                    dy *= -1
                # When you are flying up or down, you have less left and right
                # motion.
                dx = math.cos(x_angle) * m
                dz = math.sin(x_angle) * m
            else:
                dy = 0.0
                dx = math.cos(x_angle)
                dz = math.sin(x_angle)
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return dx, dy, dz

    def hit_test(
        self,
        position: Vec3,
        vector: Vec3,
        max_distance=8,
    ) -> (
        tuple[
            tuple[int, int, int],
            tuple[int, int, int],
            tuple[float, float, float],
            tuple[int, int, int] | None,
        ]
        | tuple[None, None, None, None]
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
        block = None
        real_previous = None

        for _ in range(max_distance * m):
            key = normalize((x, y, z))

            if key != previous:
                block = self.world.get_or_create_chunk_by_position(key).blocks.get(key)

            if block and block.get_bounding_box().point_intersect(
                Vec3(x, y, z) - Vec3(*block.position)
            ):
                return key, previous, (x, y, z), real_previous

            if key != previous:
                real_previous = previous

            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m

        return None, None, None, None

    def update_breaking_block(self, force_reset=False):
        stack = self.inventory.get_selected_itemstack()

        vector = self.get_sight_vector()
        block, previous, block_raw, previous_real = self.hit_test(self.position, vector)
        if block is None:
            return
        block_chunk = self.world.get_or_create_chunk_by_position(block)

        instance = block_chunk.blocks[block]
        self.breaking_block_position = block_raw

        if instance is None:
            self.breaking_block = None
        elif instance != self.breaking_block or force_reset:
            self.breaking_block = instance
            self.breaking_block_timer = self.breaking_block_total_timer = (
                instance.on_block_starting_to_break(stack, block_raw)
            )

    def update_breaking_block_state(self, dt: float):
        if self.breaking_block is None or self.breaking_block_timer is None:
            return

        self.breaking_block_timer -= dt * 20

        if self.breaking_block_timer <= 0:
            state = self.breaking_block.on_block_broken(
                self.inventory.get_selected_itemstack(),
                self.breaking_block_position,
            )
            if state is None:
                self.world.remove_block(self.breaking_block)

            # todo: if state is not False, deal damage to tools

            if state is not False:
                self.update_breaking_block()
            else:
                self.breaking_block = None
