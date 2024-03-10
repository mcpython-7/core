from __future__ import annotations

import typing

import pyglet.graphics
from pyglet.math import Mat4, Vec3

from mcpython.containers.ItemStack import ItemStack

if typing.TYPE_CHECKING:
    from mcpython.rendering.Window import Window


class Slot:
    def __init__(self, container: Container, relative_position: tuple[int, int]):
        self.container = container
        self.relative_position = relative_position
        self.itemstack: ItemStack | None = None
        self.slot_batch = pyglet.graphics.Batch()
        self.slot_vertex_data: list[pyglet.graphics.vertexdomain.VertexList] = []

    def draw(self, window: Window):
        window.set_preview_3d(
            -Vec3(
                self.container.visual_size[0] - self.relative_position[0],
                self.container.visual_size[1] - self.relative_position[1],
                0,
            )
        )
        self.slot_batch.draw()
        window.set_2d_centered_for_inventory()

    def set_stack(self, stack: ItemStack) -> typing.Self:
        if self.slot_vertex_data:
            for entry in self.slot_vertex_data:
                entry.delete()
        self.slot_vertex_data.clear()

        self.itemstack = stack

        if self.itemstack.item is not None:
            self.slot_vertex_data.append(
                self.itemstack.item.MODEL.create_vertex_list(self.slot_batch, (0, 0, 0))
            )

        return self


class Container:
    def __init__(
        self, visual_size: tuple[int, int], texture: pyglet.image.AbstractImage | None
    ):
        self.visual_size = visual_size
        self.slots: list[Slot] = []
        self.texture = texture

        if texture:
            self.sprite = pyglet.sprite.Sprite(self.texture)
            self.sprite.scale_x = visual_size[0] / self.texture.width
            self.sprite.scale_y = visual_size[1] / self.texture.height
        else:
            self.sprite = None

        self.open = False

    def draw(self, window: Window):
        if self.sprite:
            self.sprite.position = (
                -self.visual_size[0] / 2,
                -self.visual_size[1] / 2,
                0,
            )
            self.sprite.draw()

        for slot in self.slots:
            slot.draw(window)

    def show_container(self):
        self.open = True
        CONTAINER_STACK.append(self)

    def hide_container(self):
        self.open = False
        CONTAINER_STACK.remove(self)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if not self.open:
            return False

        return (
            -self.visual_size[0] / 2 <= x <= self.visual_size[0] / 2
            and -self.visual_size[1] / 2 <= y <= self.visual_size[1] / 2
        )


CONTAINER_STACK: list[Container] = []
