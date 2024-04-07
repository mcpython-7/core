from __future__ import annotations

import enum
import typing

import pyglet.text
from pyglet.math import Vec2

from mcpython.rendering.NineSplitTexture import NineSplitTexture
from mcpython.resources.ResourceManager import ResourceManager
from mcpython.states.ui.AbstractUIPart import AbstractUIPart


BUTTON_NORMAL = NineSplitTexture(
    ResourceManager.load_pyglet_image(
        "assets/minecraft/textures/gui/sprites/widget/button.png"
    )
)
BUTTON_DISABLED = NineSplitTexture(
    ResourceManager.load_pyglet_image(
        "assets/minecraft/textures/gui/sprites/widget/button_disabled.png"
    )
)
BUTTON_HIGHLIGHTED = NineSplitTexture(
    ResourceManager.load_pyglet_image(
        "assets/minecraft/textures/gui/sprites/widget/button_highlighted.png"
    )
)


class ButtonState(enum.Enum):
    NORMAL = 0
    DISABLED = 1
    HIGHLIGHTED = 2


class UIPartButton(AbstractUIPart):
    def __init__(
        self,
        position: tuple[int, int],
        size: tuple[int, int],
        text: str,
        font_size=10,
        window_alignment=(0, 0),
        item_alignment=(0, 0),
    ):
        super().__init__(position, window_alignment, item_alignment)
        self.size = size
        self.text = text
        self._state = ButtonState.NORMAL
        self.normal_batch = pyglet.graphics.Batch()
        self.normal_vertex_list = BUTTON_NORMAL.create_vertex_list(
            Vec2(*self.size), self.normal_batch, Vec2(*self.position)
        )
        self.disabled_batch = pyglet.graphics.Batch()
        self.disabled_vertex_list = BUTTON_DISABLED.create_vertex_list(
            Vec2(*self.size), self.disabled_batch, Vec2(*self.position)
        )
        self.highlighted_batch = pyglet.graphics.Batch()
        self.highlighted_vertex_list = BUTTON_HIGHLIGHTED.create_vertex_list(
            Vec2(*self.size), self.highlighted_batch, Vec2(*self.position)
        )
        self.label = pyglet.text.Label(
            self.text,
            anchor_x="center",
            anchor_y="center",
            x=size[0] / 2 + position[0],
            y=size[1] / 2 + position[1],
            color=(255, 255, 255, 255),
            font_size=font_size,
        )
        self._on_press = []

    def on_press(self, func: typing.Callable[[UIPartButton], None]):
        self._on_press.append(func)
        return self

    def get_state(self):
        return self._state

    def set_state(self, state: ButtonState):
        self._state = state

    state = property(get_state, set_state)

    def get_visual_size(self) -> tuple[int, int]:
        return self.size

    def on_mouse_motion(
        self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
    ):
        if self._state == ButtonState.DISABLED:
            return

        x, y = self.transform_to_relative(x, y)
        w, h = self.size

        if 0 <= x <= w and 0 <= y <= h:
            self.state = ButtonState.HIGHLIGHTED
        else:
            self.state = ButtonState.NORMAL

    def on_deactivate(self):
        if self._state == ButtonState.DISABLED:
            self._state = ButtonState.NORMAL

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if self._state == ButtonState.DISABLED:
            return

        x, y = self.transform_to_relative(x, y)
        w, h = self.size

        if 0 <= x <= w and 0 <= y <= h:
            for func in self._on_press:
                func(self)

    def on_draw(self, window):
        window.set_2d_for_ui(self.window_alignment, self.item_alignment, self.size)

        if self.state == ButtonState.NORMAL:
            self.normal_batch.draw()

        elif self.state == ButtonState.HIGHLIGHTED:
            self.highlighted_batch.draw()

        else:
            self.disabled_batch.draw()

        self.label.draw()
