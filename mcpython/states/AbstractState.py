from __future__ import annotations

from abc import ABC

import typing

if typing.TYPE_CHECKING:
    from mcpython.rendering.Window import Window


class AbstractStatePart(ABC):
    def __init__(self):
        self._enabled = True
        self.state_parts: list[AbstractStatePart] = []

    def get_enabled(self):
        return self._enabled

    def set_enabled(self, enabled: bool):
        if self._enabled is enabled:
            return

        self._enabled = enabled
        if not self._enabled:
            self.on_deactivate()
        else:
            self.on_activate()

    enabled = property(get_enabled, set_enabled)

    def on_activate(self):
        for part in self.state_parts:
            if part.enabled:
                part.on_activate()

    def on_deactivate(self):
        for part in self.state_parts:
            if part.enabled:
                part.on_deactivate()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        for part in self.state_parts:
            if part.enabled:
                part.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        for part in self.state_parts:
            if part.enabled:
                part.on_mouse_release(x, y, button, modifiers)

    def on_mouse_motion(
        self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
    ):
        for part in self.state_parts:
            if part.enabled:
                part.on_mouse_motion(x, y, dx, dy, buttons, modifiers)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        for part in self.state_parts:
            if part.enabled:
                part.on_mouse_scroll(x, y, scroll_x, scroll_y)

    def on_key_press(self, symbol: int, modifiers: int):
        for part in self.state_parts:
            if part.enabled:
                part.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        for part in self.state_parts:
            if part.enabled:
                part.on_key_release(symbol, modifiers)

    def on_text(self, text: str):
        for part in self.state_parts:
            if part.enabled:
                part.on_text(text)

    def on_draw(self, window: Window):
        for part in self.state_parts:
            if part.enabled:
                part.on_draw(window)

    def on_resize(self, w: int, h: int):
        for part in self.state_parts:
            if part.enabled:
                part.on_resize(w, h)

    def on_tick(self, dt: float):
        for part in self.state_parts:
            if part.enabled:
                part.on_tick(dt)


class AbstractState(ABC):
    def __init__(self):
        self.state_parts: list[AbstractStatePart] = []

    def on_activate(self):
        from mcpython.rendering.Window import Window

        for part in self.state_parts:
            if part.enabled:
                part.on_activate()

        # call an on_resize() event as the size might have changed in between
        self.on_resize(*Window.INSTANCE.get_size())

        # call an on_mouse_motion event as the mouse might have moved
        self.on_mouse_motion(*Window.INSTANCE.mouse_position, 0, 0, 0, 0)

        # todo: maybe press all currently active keys and buttons?

    def on_deactivate(self):
        from mcpython.rendering.Window import Window

        for part in self.state_parts:
            if part.enabled:
                part.on_deactivate()

        # Release all currently pressed keys and mouse buttons when leaving the state
        for key, state in Window.INSTANCE.key_state_handler.data.items():
            if state:
                self.on_key_release(key, 0)

        for button, state in Window.INSTANCE.mouse_state_handler.data.items():
            if state and button not in ("x", "y"):
                self.on_mouse_release(button, 0)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        for part in self.state_parts:
            if part.enabled:
                part.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        for part in self.state_parts:
            if part.enabled:
                part.on_mouse_release(x, y, button, modifiers)

    def on_mouse_motion(
        self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
    ):
        for part in self.state_parts:
            if part.enabled:
                part.on_mouse_motion(x, y, dx, dy, buttons, modifiers)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        for part in self.state_parts:
            if part.enabled:
                part.on_mouse_scroll(x, y, scroll_x, scroll_y)

    def on_key_press(self, symbol: int, modifiers: int):
        for part in self.state_parts:
            if part.enabled:
                part.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        for part in self.state_parts:
            if part.enabled:
                part.on_key_release(symbol, modifiers)

    def on_text(self, text: str):
        for part in self.state_parts:
            if part.enabled:
                part.on_text(text)

    def on_draw(self, window: Window):
        for part in self.state_parts:
            if part.enabled:
                part.on_draw(window)

    def on_resize(self, w: int, h: int):
        for part in self.state_parts:
            if part.enabled:
                part.on_resize(w, h)

    def on_tick(self, dt: float):
        for part in self.state_parts:
            if part.enabled:
                part.on_tick(dt)
