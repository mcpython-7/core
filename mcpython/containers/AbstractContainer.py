from __future__ import annotations

import math
import typing

import pyglet.graphics
from pyglet.math import Mat4, Vec3, Vec4, Vec2
from pyglet.window import mouse

from mcpython.containers.ItemStack import ItemStack

if typing.TYPE_CHECKING:
    from mcpython.rendering.Window import Window


class Slot:
    def __init__(self, container: Container, relative_position: tuple[int, int]):
        self.container = container
        self.relative_position = relative_position
        self.itemstack: ItemStack = ItemStack.EMPTY
        self.slot_batch = pyglet.graphics.Batch()
        self.slot_vertex_data: list[pyglet.graphics.vertexdomain.VertexList] = []
        self.number_label = pyglet.text.Label(font_size=4)
        self.number_label.position = (
            relative_position[0] + 18 - container.visual_size[0] / 2,
            relative_position[1] - container.visual_size[1] / 2,
            0,
        )

    def update_position(self, relative_position: tuple[float, float]):
        self.relative_position = relative_position
        self.number_label.position = (
            relative_position[0] + 18 - self.container.visual_size[0] / 2,
            relative_position[1] - self.container.visual_size[1] / 2,
            0,
        )

    def __repr__(self):
        return f"{self.__class__.__name__}@{self.relative_position}({self.itemstack})"

    def draw(self, window: Window):
        offset = Vec3(
            self.relative_position[0] - self.container.visual_size[0] / 2,
            self.relative_position[1] - self.container.visual_size[1] / 2,
            0,
        )
        window.set_preview_3d(offset)
        self.slot_batch.draw()
        window.set_2d_centered_for_inventory()

        if not self.itemstack.is_empty():
            self.number_label.draw()

    def set_stack(self, stack: ItemStack | None) -> typing.Self:
        if self.slot_vertex_data:
            for entry in self.slot_vertex_data:
                entry.delete()

        self.slot_vertex_data.clear()

        self.itemstack = stack or ItemStack.EMPTY

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
            self.number_label.text = str(self.itemstack.count)

            self.itemstack.item.on_slot_insert(self)

        return self

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> bool:
        from mcpython.rendering.Window import Window

        moving_slot = Window.INSTANCE.moving_player_slot

        if self.itemstack.is_empty():
            if moving_slot.itemstack.is_empty():
                return False

            if button == mouse.LEFT:
                self.set_stack(moving_slot.itemstack)
                moving_slot.set_stack(ItemStack.EMPTY)

            elif button == mouse.RIGHT:
                self.set_stack(moving_slot.itemstack.set_amount(1))
                moving_slot.set_stack(moving_slot.itemstack.add_amount(-1))
                return True

            return True

        if moving_slot.itemstack.is_empty():
            if self.itemstack.is_empty():
                return False

            if button == mouse.LEFT:
                moving_slot.set_stack(self.itemstack)
                self.set_stack(ItemStack.EMPTY)
                return True

            if button == mouse.RIGHT:
                transfer_amount = math.floor(self.itemstack.count / 2)
                self.set_stack(self.itemstack.add_amount(-transfer_amount))
                moving_slot.set_stack(self.itemstack.set_amount(transfer_amount))
                return True

        if moving_slot.itemstack.is_compatible(self.itemstack):
            if button == mouse.LEFT:
                transfer_amount = min(
                    self.itemstack.item.MAX_STACK_SIZE - self.itemstack.count,
                    moving_slot.itemstack.count,
                )
                if transfer_amount == 0:
                    return True

                self.set_stack(self.itemstack.add_amount(transfer_amount))
                moving_slot.set_stack(
                    moving_slot.itemstack.add_amount(-transfer_amount)
                )
                return True

            if button == mouse.RIGHT:
                if self.itemstack.count < self.itemstack.item.MAX_STACK_SIZE:
                    self.set_stack(self.itemstack.add_amount(1))
                    moving_slot.set_stack(moving_slot.itemstack.add_amount(-1))

                return True

        return False


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

        if not (0 <= x <= self.visual_size[0] and 0 <= y <= self.visual_size[1]):
            return False

        for slot in self.slots:
            if (
                slot.relative_position[0] <= x <= slot.relative_position[0] + 18
                and slot.relative_position[1] <= y <= slot.relative_position[1] + 18
            ) and slot.on_mouse_press(x, y, button, modifiers):
                break

        return True

    def on_resize(self, width: int, height: int):
        # for slot in self.slots:
        #     slot.on_resize(width, height)
        pass


CONTAINER_STACK: list[Container] = []
