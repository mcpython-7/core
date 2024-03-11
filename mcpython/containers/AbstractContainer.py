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
    def __init__(
        self,
        container: Container,
        relative_position: tuple[int, int],
        enable_interaction=True,
    ):
        self.container = container
        self._relative_position = relative_position
        self._itemstack: ItemStack = ItemStack.EMPTY
        self.slot_batch = pyglet.graphics.Batch()
        self.slot_vertex_data: list[pyglet.graphics.vertexdomain.VertexList] = []
        self.number_label = pyglet.text.Label(font_size=4 * 4, bold=True)
        self.update_position(relative_position)
        self.enable_interaction = enable_interaction

    @property
    def itemstack(self):
        return self._itemstack

    @property
    def relative_position(self):
        return self._relative_position

    def update_position(self, relative_position: tuple[float, float]):
        self._relative_position = relative_position

    def __repr__(self):
        return f"{self.__class__.__name__}@{self._relative_position}({self.itemstack})"

    def draw(self, window: Window, offset: Vec3 = None):
        if not offset:
            offset = self._calculate_offset(window)

        window.set_preview_3d(offset + Vec3(8, 7, 0))
        self.slot_batch.draw()
        window.set_2d_centered_for_inventory(self.container, scale=0.25)

        if not self.itemstack.is_empty():
            self.number_label.position = (
                (offset[0] + 24 - self.number_label.content_width) * 4,
                (offset[1]) * 4,
                0,
            )
            self.number_label.draw()

        window.set_2d_centered_for_inventory(self.container)

    def _calculate_offset(self, window: Window):
        return Vec3(
            self._relative_position[0]
            - self.container.visual_size[0] / 2
            + (self.container.render_anchor[0] - 0.5)
            * window.get_size()[0]
            / window.inventory_scale,
            self._relative_position[1]
            - self.container.visual_size[1] / 2
            + (self.container.render_anchor[1] - 0.5)
            * window.get_size()[1]
            / window.inventory_scale,
            0,
        )

    def set_stack(self, stack: ItemStack | None) -> typing.Self:
        if self.slot_vertex_data:
            for entry in self.slot_vertex_data:
                entry.delete()

        self.slot_vertex_data.clear()

        self._itemstack = stack or ItemStack.EMPTY

        if self._itemstack.item is not None:
            from mcpython.rendering.Window import Window

            width, height = Window.INSTANCE.get_size()

            x = self._relative_position[0] - self.container.visual_size[0] / 2
            y = self._relative_position[1] - self.container.visual_size[1] / 2

            self.slot_vertex_data.append(
                self._itemstack.item.MODEL.create_vertex_list(
                    self.slot_batch,
                    (0, 0, 0),
                    offset=Vec2(
                        x / width * 12.5,
                        y / height * 12.5,
                    ),
                ),
            )
            self.number_label.text = str(self._itemstack.count)
            self.number_label.x = (
                self._relative_position[0]
                + 14
                - self.container.visual_size[0] / 2
                - self.number_label.content_width
            )

            self._itemstack.item.on_slot_insert(self)

        return self

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if not self.enable_interaction:
            return False

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

            elif button == mouse.MIDDLE:
                if not moving_slot.itemstack.is_empty():
                    self.set_stack(
                        moving_slot.itemstack.set_amount(
                            moving_slot.itemstack.item.MAX_STACK_SIZE
                        )
                    )
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

            elif button == mouse.MIDDLE:
                if not self.itemstack.is_empty():
                    moving_slot.set_stack(
                        self.itemstack.set_amount(self.itemstack.item.MAX_STACK_SIZE)
                    )
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


class SlotRenderCopy(Slot):
    def __init__(
        self,
        container: Container,
        relative_position: tuple[int, int],
        mirror: Slot,
        enable_interaction=True,
    ):
        super().__init__(
            container, relative_position, enable_interaction=enable_interaction
        )
        self._mirror = mirror

    @property
    def itemstack(self):
        return self._mirror.itemstack

    def set_stack(self, stack: ItemStack | None) -> typing.Self:
        self._mirror.set_stack(stack)
        return self

    def draw(self, window: Window, offset: Vec3 = None):
        if not offset:
            offset = self._calculate_offset(window)

        pos = self._mirror.relative_position
        self._mirror.update_position(self._relative_position)
        self._mirror.draw(window, offset)
        self._mirror.update_position(pos)


class Container:
    def __init__(
        self, visual_size: tuple[int, int], texture: pyglet.image.AbstractImage | None
    ):
        self.visual_size = visual_size
        self.slots: list[Slot] = []
        self.texture = texture
        self.render_offset = (0, 0)
        self.render_anchor = (0.5, 0.5)
        self.image_anchor = (0.5, 0.5)

        if texture:
            self.sprite = pyglet.sprite.Sprite(self.texture)
            self.sprite.scale_x = visual_size[0] / self.texture.width
            self.sprite.scale_y = visual_size[1] / self.texture.height
        else:
            self.sprite = None

        self.open = False

    def window_to_relative_world(
        self, coord: tuple[float, float], win_size: tuple[int, int], scale: float
    ) -> tuple[float, float]:
        x, y = coord
        x -= win_size[0] * self.render_anchor[0]
        y -= win_size[1] * self.render_anchor[1]
        x /= scale
        y /= scale
        x += self.render_offset[0] + self.visual_size[0] / 2
        y += self.render_offset[1] + self.visual_size[1] / 2
        return x, y

    def draw(self, window: Window):
        if self.sprite:
            self.sprite.position = (
                -self.visual_size[0] * self.image_anchor[0],
                -self.visual_size[1] * self.image_anchor[1],
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
