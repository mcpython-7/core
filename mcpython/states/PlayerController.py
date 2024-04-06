from __future__ import annotations

import time

import pyglet
from pyglet.window import mouse, key

from mcpython.config import JUMP_SPEED
from mcpython.containers.ItemStack import ItemStack
from mcpython.states.AbstractState import AbstractStatePart
from mcpython.world.entity.PlayerEntity import PlayerEntity
from mcpython.world.util import sectorize


class PlayerController(AbstractStatePart):
    def __init__(self, player: PlayerEntity):
        super().__init__()
        self.player = player
        self.last_space_press = 0

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        stack = self.player.inventory.get_selected_itemstack()
        world = self.player.world

        vector = self.player.get_sight_vector()
        block, previous, block_raw, previous_real = self.player.hit_test(
            self.player.position, vector
        )
        block_chunk = world.get_or_create_chunk_by_position(block) if block else None
        previous_chunk = (
            world.get_or_create_chunk_by_position(previous) if previous else None
        )

        if (
            block_chunk
            and block in block_chunk.blocks
            and block_chunk.blocks[block].on_block_interaction(stack, button, modifiers)
        ):
            return

        if (
            block_chunk
            and not stack.is_empty()
            and stack.item.on_block_interaction(
                stack, block_chunk.blocks.get(block, None), button, modifiers
            )
        ):
            return

        if (button == mouse.RIGHT) or (
            (button == mouse.LEFT) and (modifiers & key.MOD_CTRL)
        ):
            # ON OSX, control + left click = right click.
            if previous and not stack.is_empty():
                old_block = previous_chunk.blocks.get(previous)

                if old_block:
                    state2 = old_block.on_block_merging(stack, block_raw)
                    if state2 is True:
                        pass  # todo: reduce stack amount
                elif b := stack.item.create_block_to_be_placed(stack):
                    world.add_block(previous, b)

                    if b.on_block_placed(stack, block, block_raw) is False:
                        world.remove_block(b)
                    else:
                        b.update_render_state()

        elif button == mouse.LEFT and block and block_chunk:
            self.player.update_breaking_block()

        elif button == mouse.MIDDLE and block and block_chunk:
            instance = block_chunk.blocks[block]

            slot = self.player.inventory.find_item(instance.NAME)

            if slot is None:
                itemstack = self.player.inventory.get_selected_itemstack()
                self.player.inventory.get_selected_slot().set_stack(
                    ItemStack(instance.NAME)
                )
                if not itemstack.is_empty():
                    self.player.inventory.insert(itemstack)

            elif slot not in self.player.inventory.slots[:9]:
                itemstack = self.player.inventory.get_selected_itemstack()
                self.player.inventory.get_selected_slot().set_stack(slot.itemstack)
                slot.set_stack(itemstack)

            else:
                self.player.inventory.selected_slot = self.player.inventory.slots.index(
                    slot
                )
                if self.player.breaking_block is not None:
                    self.player.update_breaking_block(force_reset=True)

        return

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        self.player.breaking_block = None

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.player.inventory.selected_slot = int(
            (self.player.inventory.selected_slot - scroll_y) % 9
        )
        if self.player.breaking_block is not None:
            self.player.update_breaking_block(force_reset=True)

    def on_mouse_motion(
        self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
    ):
        m = 0.15

        x, y = self.player.rotation
        x, y = x + dx * m, y + dy * m

        # y = max(-90.0, min(90.0, y))
        y = max(-89.9, min(89.9, y))

        self.player.rotation = (x, y)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == key.W:
            self.player.strafe[0] -= 1

        elif symbol == key.S:
            self.player.strafe[0] += 1

        elif symbol == key.A:
            self.player.strafe[1] -= 1

        elif symbol == key.D:
            self.player.strafe[1] += 1

        elif symbol == key.SPACE:
            if self.player.flying:
                self.player.key_dy = 1
            elif self.player.dy == 0:
                self.player.dy = JUMP_SPEED

            if self.player.gamemode == 1:
                if time.time() - self.last_space_press <= 0.3:
                    self.player.flying = not self.player.flying

                    if self.player.flying:
                        self.player.key_dy = 1

                    self.last_space_press = 0
                else:
                    self.last_space_press = time.time()

        elif symbol == key.T:
            self.player.chat.show_container()
            self.player.chat.ignore_next_t = True
            self.player.world.window.set_exclusive_mouse(False)
            return pyglet.event.EVENT_HANDLED

        elif symbol in (key.LSHIFT, key.RSHIFT):
            self.player.key_dy = -1

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == key.W:
            self.player.strafe[0] = 0
        elif symbol == key.S:
            self.player.strafe[0] = 0
        elif symbol == key.A:
            self.player.strafe[1] = 0
        elif symbol == key.D:
            self.player.strafe[1] = 0
        elif symbol in (key.SPACE, key.LSHIFT, key.RSHIFT):
            self.player.key_dy = 0

    def on_tick(self, dt: float):
        sector = sectorize(self.player.position)
        if sector != self.player.sector:
            self.player.change_chunks(self.player.sector, sector)

            if self.player.sector is None:
                self.player.world.process_entire_queue()

            self.player.sector = sector

        self.player.update_breaking_block_state(dt)
