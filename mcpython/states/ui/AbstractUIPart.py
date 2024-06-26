from __future__ import annotations

from abc import ABC
import typing

import pyglet

from mcpython.states.AbstractState import AbstractStatePart


if typing.TYPE_CHECKING:
    from mcpython.rendering.Window import Window


class AbstractUIPart(AbstractStatePart, ABC):
    def __init__(
        self, position: tuple[int, int], window_alignment=(0, 0), item_alignment=(0, 0)
    ):
        super().__init__()
        self.position = position
        self.window_alignment = window_alignment
        self.item_alignment = item_alignment
        self.general_batch = pyglet.graphics.Batch()

    def transform_to_relative(self, x: int, y: int) -> tuple[int, int]:
        from mcpython.rendering.Window import Window

        width, height = Window.INSTANCE.get_size()
        w, h = self.get_visual_size()

        return (
            (x - width * self.window_alignment[0]) / Window.INSTANCE.inventory_scale
            + w * self.item_alignment[0]
            - self.position[0],
            (y - height * self.window_alignment[0]) / Window.INSTANCE.inventory_scale
            + h * self.item_alignment[1]
            - self.position[1],
        )

    def get_visual_size(self) -> tuple[int, int]:
        raise NotImplementedError

    def on_draw(self, window: Window):
        window.set_2d_for_ui(
            self.window_alignment, self.item_alignment, self.get_visual_size()
        )
        self.general_batch.draw()
