from __future__ import annotations

import typing

import pyglet.graphics
from pyglet.math import Mat4, Vec3, Vec4, Vec2

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
        offset = Vec3(
            self.relative_position[0] - self.container.visual_size[0] / 2,
            self.relative_position[1] - self.container.visual_size[1] / 2,
            0,
        )
        window.set_preview_3d(offset, Vec3(*self.container.visual_size))
        self.slot_batch.draw()
        window.set_2d_centered_for_inventory()

    def set_stack(self, stack: ItemStack) -> typing.Self:
        if self.slot_vertex_data:
            for entry in self.slot_vertex_data:
                entry.delete()
        self.slot_vertex_data.clear()

        self.itemstack = stack

        if self.itemstack.item is not None:
            from mcpython.rendering.Window import Window

            width, height = Window.INSTANCE.get_size()

            x = self.relative_position[0] - self.container.visual_size[0] / 2
            y = self.relative_position[1] - self.container.visual_size[1] / 2
            # print(x, y, width, height)

            self.slot_vertex_data.append(
                self.itemstack.item.MODEL.create_vertex_list(
                    self.slot_batch,
                    (0, 0, 0),
                    offset=Vec2(
                        x / width * 12.5,
                        y / height * 12.5,
                    ),
                ),
            )

        return self

    def on_resize(self, width: int, height: int):
        if self.slot_vertex_data:
            x = self.relative_position[0] - self.container.visual_size[0] / 2
            y = self.relative_position[1] - self.container.visual_size[1] / 2
            for item in self.slot_vertex_data:
                item.set_attribute_data(
                    "render_offset", (x / width * 12.5, y / height * 12.5) * item.count
                )


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

    def on_resize(self, width: int, height: int):
        for slot in self.slots:
            slot.on_resize(width, height)


CONTAINER_STACK: list[Container] = []
