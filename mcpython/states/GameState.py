from __future__ import annotations

from pyglet.window import key

from mcpython.containers.AbstractContainer import CONTAINER_STACK
from mcpython.rendering.Window import Window
from mcpython.states.AbstractState import AbstractState
from mcpython.states import InventoryController, PlayerController, WorldController


class GameState(AbstractState):
    NUM_KEYS = [
        key._1,
        key._2,
        key._3,
        key._4,
        key._5,
        key._6,
        key._7,
        key._8,
        key._9,
    ]

    def __init__(self, window: Window):
        super().__init__()
        self.state_parts = [
            WorldController.WorldController(window.world),
            PlayerController.PlayerController(window.player),
            InventoryController.InventoryController(window.player),
        ]
        self.window = window

    def on_key_press(self, symbol: int, modifiers: int):
        super().on_key_press(symbol, modifiers)

        # todo: add escape state!
        if symbol == key.ESCAPE:
            for container in CONTAINER_STACK:
                container.on_close_with_escape()

            self.window.set_exclusive_mouse(not self.window.exclusive)

        elif symbol == key.E:
            if self.window.player.chat.open:
                pass

            elif self.window.player.inventory.open:
                self.window.set_exclusive_mouse(True)
                self.window.player.inventory.hide_container()
            else:
                self.window.set_exclusive_mouse(False)
                self.window.player.inventory.show_container()

        elif symbol in self.NUM_KEYS and self.window.exclusive:
            index = symbol - self.NUM_KEYS[0]
            self.window.player.inventory.selected_slot = index
            if self.window.player.breaking_block is not None:
                self.window.player.update_breaking_block(force_reset=True)
