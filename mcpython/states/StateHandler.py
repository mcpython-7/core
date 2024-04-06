from __future__ import annotations

import typing

from mcpython.states.AbstractState import AbstractState, AbstractStatePart


if typing.TYPE_CHECKING:
    from mcpython.rendering.Window import Window


class StateHandler:
    def __init__(self):
        self._states: dict[str, AbstractState] = {}
        self._current_state: AbstractState | None = None

    def find_active_part[T](self, part_type: type[T]) -> T | None:
        if self._current_state is None:
            return

        for part in self._current_state.state_parts:
            if isinstance(part, part_type):
                return part

    @property
    def current_state(self) -> AbstractState:
        return self._current_state

    def register_state(self, name: str, state: AbstractState) -> typing.Self:
        self._states[name] = state
        return self

    def change_state(self, new_state: str | AbstractState | None) -> typing.Self:
        if self._current_state is not None:
            self._current_state.on_deactivate()

        self._current_state = (
            self._states[new_state] if isinstance(new_state, str) else new_state
        )

        if self._current_state is not None:
            self._current_state.on_activate()

        return self

    def handle_on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if self._current_state is None:
            return
        return self._current_state.on_mouse_press(x, y, button, modifiers)

    def handle_on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if self._current_state is None:
            return
        return self._current_state.on_mouse_release(x, y, button, modifiers)

    def handle_on_mouse_motion(
        self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
    ):
        if self._current_state is None:
            return
        return self._current_state.on_mouse_motion(x, y, dx, dy, buttons, modifiers)

    def handle_on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self._current_state is None:
            return
        return self._current_state.on_mouse_scroll(x, y, scroll_x, scroll_y)

    def handle_on_key_press(self, symbol: int, modifiers: int):
        if self._current_state is None:
            return
        return self._current_state.on_key_press(symbol, modifiers)

    def handle_on_key_release(self, symbol: int, modifiers: int):
        if self._current_state is None:
            return
        return self._current_state.on_key_release(symbol, modifiers)

    def handle_on_text(self, text: str):
        if self._current_state is None:
            return
        return self._current_state.on_text(text)

    def handle_on_draw(self, window: Window):
        if self._current_state is None:
            return
        return self._current_state.on_draw(window)

    def handle_on_resize(self, w: int, h: int):
        if self._current_state is None:
            return
        return self._current_state.on_resize(w, h)

    def handle_on_tick(self, dt: float):
        if self._current_state is None:
            return
        return self._current_state.on_tick(dt)
