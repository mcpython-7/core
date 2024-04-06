from __future__ import annotations


import pyglet

from mcpython.containers.AbstractContainer import CONTAINER_STACK
from mcpython.rendering.Window import Window
from mcpython.states.AbstractState import AbstractStatePart
from mcpython.world.entity.PlayerEntity import PlayerEntity


class InventoryController(AbstractStatePart):
    def __init__(self, player: PlayerEntity):
        super().__init__()
        self.player = player

        # The label that is displayed in the top left of the canvas.
        self.label = pyglet.text.Label(
            "",
            font_name="Arial",
            font_size=18,
            x=10,
            y=10,
            anchor_x="left",
            anchor_y="top",
            color=(0, 0, 0, 255),
        )

        # The crosshairs at the center of the screen.
        self.reticle: tuple[pyglet.shapes.Line, pyglet.shapes.Line] | None = None

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        for container in CONTAINER_STACK:
            if container.on_mouse_press(
                *container.window_to_relative_world(
                    (x, y),
                    self.player.world.window.get_size(),
                    self.player.world.window.inventory_scale,
                ),
                button,
                modifiers,
            ):
                return

    def on_mouse_motion(
        self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
    ):
        for container in CONTAINER_STACK:
            container.on_mouse_motion(
                *container.window_to_relative_world(
                    (x, y),
                    self.player.world.window.get_size(),
                    self.player.world.window.inventory_scale,
                ),
                dx / self.player.world.window.inventory_scale,
                dy / self.player.world.window.inventory_scale,
                buttons,
                modifiers,
            )

    def on_key_press(self, symbol: int, modifiers: int):
        for container in CONTAINER_STACK:
            if container.on_key_press(symbol, modifiers):
                return

    def on_text(self, text: str):
        for container in CONTAINER_STACK:
            if container.on_text(text):
                return pyglet.event.EVENT_HANDLED

    def on_draw(self, window: Window):
        window.set_2d()
        self.draw_label()
        self.draw_reticle()

        self.player.draw_inventories(window)

    def on_resize(self, w: int, h: int):
        # label
        self.label.y = h - 10
        # reticle
        x, y = w // 2, h // 2
        n = 10

        self.reticle = (
            pyglet.shapes.Line(x - n, y, x + n, y, color=(0, 0, 0, 255), width=2),
            pyglet.shapes.Line(x, y - n, x, y + n, color=(0, 0, 0, 255), width=2),
        )

        for container in CONTAINER_STACK:
            container.on_resize(w, h)

    def draw_label(self):
        """Draw the label in the top left of the screen."""
        x, y, z = self.player.position
        self.label.text = "%02d (%.2f, %.2f, %.2f) %d (%d) %d" % (
            pyglet.clock.get_frequency(),
            x,
            y,
            z,
            len(self.player.world.chunks),
            len(
                self.player.world.get_or_create_chunk_by_position(
                    self.player.position
                ).blocks
            ),
            len(
                self.player.world.get_or_create_chunk_by_position(
                    self.player.position
                ).entities
            ),
        )
        self.label.draw()

    def draw_reticle(self):
        """Draw the crosshairs in the center of the screen."""
        self.reticle[0].draw()
        self.reticle[1].draw()
