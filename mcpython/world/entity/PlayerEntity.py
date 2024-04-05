from __future__ import annotations

import itertools

from mcpython.commands.Chat import Chat
from mcpython.containers.AbstractContainer import Slot, ItemInformationScreen
from mcpython.containers.PlayerInventoryContainer import (
    PlayerInventoryContainer,
    HotbarContainer,
)
from mcpython.world.blocks.AbstractBlock import AbstractBlock
from mcpython.world.entity.AbstractEntity import AbstractEntity


class PlayerEntity(AbstractEntity):
    NAME = "minecraft:player"

    def __init__(self, world, pos, rot):
        super().__init__(world, pos, rot)
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

    def update_breaking_block(self, force_reset=False):
        stack = self.inventory.get_selected_itemstack()

        vector = self.world.window.get_sight_vector()
        block, previous, block_raw, previous_real = self.world.hit_test(
            self.position, vector
        )
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
