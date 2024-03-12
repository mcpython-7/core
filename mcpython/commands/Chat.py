from __future__ import annotations

import time
import typing

import pyglet.text

from mcpython.commands.Command import COMMAND_REGISTRY
from mcpython.containers.AbstractContainer import Container
from pyglet.window import key
import clipboard

if typing.TYPE_CHECKING:
    from mcpython.rendering.Window import Window

KEY_MAPPING: dict[int, str] = {
    getattr(key, c.upper()): c for c in "abcdefghijklmnopqrstuvwxyz"
}
NUMBER_MAPPING: dict[int, str] = {getattr(key, f"_{c}"): c for c in "0123456789"}


class Chat(Container):
    def __init__(self):
        super().__init__((0, 0), None)
        self.render_anchor = (0, 0)
        self.render_offset = (10, 10)

        self.chat_output: list[pyglet.text.Label] = []
        self.chat_output_batch = pyglet.graphics.Batch()
        self.chat_output_rectangle = pyglet.shapes.Rectangle(
            -2, -2 + 30, 0, 0, color=(0, 0, 0, 200), batch=self.chat_output_batch
        )

        self.history = []
        self.text = ""
        self.text_label = pyglet.text.Label(self.text, font_size=20)
        self.background_shape = pyglet.shapes.Rectangle(
            -2, -2, 0, 0, color=(0, 0, 0, 200)
        )
        self.ignore_next_t = False
        self.last_chat_update = 0

    def draw_chat_output(self, window: Window):
        if time.time() - self.last_chat_update > 4 or self.open:
            return

        window.set_2d_centered_for_inventory(
            self, offset=(10, 40 + len(self.chat_output) * 30), scale=0.25
        )
        self.chat_output_batch.draw()

    def submit_text(self, text: str):
        label = pyglet.text.Label(text, font_size=20, batch=self.chat_output_batch)
        label.position = 2, 2 - len(self.chat_output) * 30, 0
        self.chat_output.append(label)
        self.chat_output_rectangle.height = len(self.chat_output) * 30 + 8
        self.chat_output_rectangle.width = max(
            self.chat_output_rectangle.width, label.content_width
        )
        self.chat_output_rectangle.y -= 30
        self.last_chat_update = time.time()

    def on_key_press(self, symbol: int, modifiers: int) -> bool:
        if symbol == key.V and modifiers & key.MOD_CTRL:
            self.text += clipboard.paste()
            return True

        if symbol == key.ENTER:
            self.on_enter_pressed()
            return True

        if symbol == key.BACKSPACE and self.text:
            self.text = self.text[:-1]
            return True

        return False

    # TODO Rename this here and in `on_key_press`
    def on_enter_pressed(self):
        if self.text.startswith("/"):
            if command := COMMAND_REGISTRY.get(
                self.text.split(" ")[0].removeprefix("/")
            ):
                command.run_command(self, self.text.removeprefix("/"))
            else:
                self.submit_text("ERROR: Command not found!")
        else:
            self.submit_text(self.text)

        self.history.append(self.text)
        self.text = ""
        self.hide_container()
        from mcpython.rendering.Window import Window

        Window.INSTANCE.set_exclusive_mouse(True)

    def on_text(self, text: str) -> bool:
        if self.ignore_next_t:
            self.ignore_next_t = False
            if text.lower() == "t":
                return False

        self.text += text
        return True

    def draw(self, window: Window):
        window.set_2d_centered_for_inventory(self, offset=(10, 10), scale=0.25)

        self.background_shape.width = self.text_label.content_width
        self.background_shape.height = self.text_label.content_height
        self.background_shape.draw()

        self.text_label.text = self.text
        self.text_label.draw()

        window.set_2d_centered_for_inventory(
            self, offset=(10, 40 + len(self.chat_output) * 30), scale=0.25
        )
        self.chat_output_batch.draw()

    def hide_container(self):
        super().hide_container()
        self.text = ""
