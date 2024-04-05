from __future__ import annotations

import itertools
import math

from pyglet.math import Vec3

from mcpython.commands.Chat import Chat
from mcpython.config import (
    FLYING_SPEED,
    WALKING_SPEED,
    GRAVITY,
    TERMINAL_VELOCITY,
    PLAYER_HEIGHT,
)
from mcpython.containers.AbstractContainer import Slot, ItemInformationScreen
from mcpython.containers.PlayerInventoryContainer import (
    PlayerInventoryContainer,
    HotbarContainer,
)
from mcpython.rendering.util import FACES
from mcpython.world.blocks.AbstractBlock import AbstractBlock
from mcpython.world.entity.AbstractEntity import AbstractEntity
from mcpython.world.util import normalize


class PlayerEntity(AbstractEntity):
    NAME = "minecraft:player"

    def __init__(self, world, pos, rot):
        super().__init__(world, pos, rot)

        self.gamemode = 0

        self.rotation = (0, 0)
        self.strafe = [0, 0]
        self.flying = False
        self.no_collision = False
        self.dy = 0
        self.key_dy = 0

        self.inventory = PlayerInventoryContainer()
        self.hotbar = HotbarContainer(self.inventory)
        self.hotbar.show_container()
        self.chat = Chat(self)

        self.slot_hover_info = ItemInformationScreen()

        self.moving_player_slot = Slot(
            self.inventory, (0, 0), on_update=self._update_moving_slot
        )

        self.breaking_block: AbstractBlock | None = None
        self.breaking_block_timer: float | None = None
        self.breaking_block_total_timer: float | None = None
        self.breaking_block_position: tuple[float, float, float] | None = None

        self.breaking_block_provider = None

    def set_gamemode(self, gamemode: int):
        if gamemode == self.gamemode:
            return
        self.gamemode = gamemode

        if gamemode in {0, 2}:
            self.flying = False

        if gamemode == 3:
            self.flying = True
            self.no_collision = True
        else:
            self.no_collision = False

    def update_position(self, dt: float):
        """Private implementation of the `update()` method. This is where most
        of the motion logic lives, along with gravity and collision detection.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        # walking
        speed = FLYING_SPEED if self.flying else WALKING_SPEED
        d = dt * speed  # distance covered this tick.
        dx, dy, dz = self.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d
        # gravity
        if not self.flying:
            # Update your vertical speed: if you are falling, speed up until you
            # hit terminal velocity; if you are jumping, slow down until you
            # start falling.
            self.dy -= dt * GRAVITY
            self.dy = max(self.dy, -TERMINAL_VELOCITY)
            dy += self.dy * dt

        # collisions
        x, y, z = self.position

        if not self.no_collision:
            x, y, z = self.collide((x + dx, y + dy, z + dz), PLAYER_HEIGHT)
        else:
            x, y, z = x + dx, y + dy, z + dz

        self.position = Vec3(x, y, z)

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
        dy = 0.0
        dx = 0.0
        dz = 0.0

        if any(self.strafe):
            x, y = self.rotation
            strafe = math.degrees(math.atan2(*self.strafe))
            x_angle = math.radians(x + strafe)

            dx = math.cos(x_angle)
            dz = math.sin(x_angle)

        if self.key_dy:
            dy = self.key_dy * 0.7

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

    def collide(self, position: tuple[float, float, float], height: int):
        """Checks to see if the player at the given `position` and `height`
        is colliding with any blocks in the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check for collisions at.
        height : int or float
            The height of the player.

        Returns
        -------
        position : tuple of len 3
            The new position of the player taking into account collisions.

        """
        # How much overlap with a dimension of a surrounding block you need to
        # have to count as a collision. If 0, touching terrain at all counts as
        # a collision. If .49, you sink into the ground, as if walking through
        # tall grass. If >= .5, you'll fall through the ground.
        pad = 0
        p = list(position)
        np = normalize(position)
        for face in FACES:  # check all surrounding blocks
            for i in range(3):  # check each dimension independently
                if not face[i]:
                    continue

                # How much overlap you have with this dimension.
                # todo: here we could do a hitbox-based check instead
                d = (p[i] - np[i]) * face[i]
                if d < pad:
                    continue

                for dy in range(height):  # check each height
                    op = list(np)
                    op[1] -= dy
                    op[i] += face[i]

                    block = self.world.get_or_create_chunk_by_position(op).blocks.get(
                        tuple(op)
                    )

                    if block is None or block.NO_COLLISION:
                        continue

                    # d = block.get_bounding_box().check_axis_intersection(
                    #     i,
                    #     Vec3(*block.position) - Vec3(*self.player.position),
                    # )
                    # if d == 0:
                    #     continue

                    p[i] -= (d - pad) * face[i]
                    if face in [(0, -1, 0), (0, 1, 0)]:
                        # You are colliding with the ground or ceiling, so stop
                        # falling / rising.
                        self.dy = 0

                    break

        return tuple(p)
