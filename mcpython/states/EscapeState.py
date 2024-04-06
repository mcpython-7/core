from __future__ import annotations

from pyglet.window import key

from mcpython.rendering.Window import Window
from mcpython.states.AbstractState import AbstractState
from mcpython.states import WorldController, InventoryController
from mcpython.states.ui.UIPartButton import UIPartButton


class EscapeState(AbstractState):
    def __init__(self, window: Window, game_state: AbstractState):
        super().__init__()
        self.world_controller = WorldController.WorldController(window.world)
        self.inventory_controller = InventoryController.InventoryController(
            window.player
        )
        self.state_parts = [
            self.world_controller,
            self.inventory_controller,
            UIPartButton(
                (0, 0),
                (150, 20),
                "Back to the Game",
                window_alignment=(0.5, 0.5),
                item_alignment=(0.5, 0.5),
            ).on_press(
                lambda _: self.state_handler.change_state(self.game_state)
                == self.window.set_exclusive_mouse(True)
            ),
        ]
        self.window = window
        self.game_state = game_state

    def on_activate(self):
        super().on_activate()
        self.window.set_exclusive_mouse(False)

    def on_key_press(self, symbol: int, modifiers: int):
        super().on_key_press(symbol, modifiers)

        if symbol == key.ESCAPE:
            self.state_handler.change_state(self.game_state)
            self.window.set_exclusive_mouse(True)
