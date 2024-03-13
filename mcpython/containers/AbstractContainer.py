from __future__ import annotations

import math
import typing

import pyglet.graphics
from pyglet.math import Mat4, Vec3, Vec4, Vec2
from pyglet.window import mouse

from mcpython.containers.ItemStack import ItemStack
from mcpython.world.items.AbstractItem import AbstractItem

if typing.TYPE_CHECKING:
    from mcpython.rendering.Window import Window


class Slot:
    def __init__(
        self,
        container: Container,
        relative_position: tuple[int, int],
        enable_interaction=True,
        allow_player_insertion=True,
        is_picked_up_into=True,
        discoverable=True,
        allow_right_click=True,
        on_update: typing.Callable[[Slot, ItemStack], None] = None,
    ):
        self.container = container
        self._relative_position = relative_position
        self._itemstack: ItemStack = ItemStack.EMPTY
        self.slot_batch = pyglet.graphics.Batch()
        self.flat_batch = pyglet.graphics.Batch()
        self.slot_vertex_data: list[pyglet.graphics.vertexdomain.VertexList] = []
        self.number_label = pyglet.text.Label(font_size=4 * 4, bold=True)
        self.update_position(relative_position)
        self.enable_interaction = enable_interaction
        self.allow_player_insertion = allow_player_insertion
        self.is_picked_up_into = is_picked_up_into
        self.discoverable = discoverable
        self.allow_right_click = allow_right_click
        self.on_update = on_update

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
        window.set_2d_centered_for_inventory(self.container, offset=offset)
        self.flat_batch.draw()
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

    def set_stack(self, stack: ItemStack | None, update=True) -> typing.Self:
        if self.slot_vertex_data:
            for entry in self.slot_vertex_data:
                entry.delete()

        self.slot_vertex_data.clear()

        old_stack = self._itemstack
        self._itemstack = stack or ItemStack.EMPTY

        if self._itemstack.item is not None:
            self.slot_vertex_data.extend(
                self._itemstack.item.MODEL.create_vertex_list(
                    self.slot_batch,
                    (0, 0, 0),
                    flat_batch=self.flat_batch,
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

        if self.on_update:
            self.on_update(self, old_stack)

        if self.container.item_info_screen.bound_slot is self:
            self.container.item_info_screen.bind_to_slot(self)

        return self

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if not self.enable_interaction:
            return False

        from mcpython.rendering.Window import Window

        moving_slot = Window.INSTANCE.moving_player_slot

        if self.itemstack.is_empty() and self.allow_player_insertion:
            if moving_slot.itemstack.is_empty():
                return False

            if button == mouse.LEFT:
                self.set_stack(moving_slot.itemstack)
                moving_slot.set_stack(ItemStack.EMPTY)

            elif button == mouse.RIGHT and self.allow_right_click:
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

            if button == mouse.RIGHT and self.allow_right_click:
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

        if (
            moving_slot.itemstack.is_compatible(self.itemstack)
            and self.allow_player_insertion
        ):
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

            if button == mouse.RIGHT and self.allow_right_click:
                if self.itemstack.count < self.itemstack.item.MAX_STACK_SIZE:
                    self.set_stack(self.itemstack.add_amount(1))
                    moving_slot.set_stack(moving_slot.itemstack.add_amount(-1))

                return True

        elif button == mouse.LEFT and self.allow_player_insertion:
            itemstack = moving_slot.itemstack
            moving_slot.set_stack(self.itemstack)
            self.set_stack(itemstack)

        return False


class SlotRenderCopy(Slot):
    def __init__(
        self,
        container: Container,
        relative_position: tuple[int, int],
        mirror: Slot,
        enable_interaction=True,
        allow_player_insertion=True,
        is_picked_up_into=True,
        discoverable=True,
        allow_right_click=True,
        on_update: typing.Callable[[Slot, ItemStack], None] = None,
    ):
        super().__init__(
            container,
            relative_position,
            enable_interaction=enable_interaction,
            allow_player_insertion=allow_player_insertion,
            is_picked_up_into=is_picked_up_into,
            discoverable=discoverable,
            allow_right_click=allow_right_click,
            on_update=on_update,
        )
        self._mirror = mirror

    @property
    def itemstack(self):
        return self._mirror.itemstack

    def set_stack(self, stack: ItemStack | None, update=True) -> typing.Self:
        old_stack = self._mirror.itemstack
        self._mirror.set_stack(stack, update=update)
        if self.on_update:
            self.on_update(self, old_stack)
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
        self.item_info_screen = ItemInformationScreen()

        if texture:
            self.sprite = pyglet.sprite.Sprite(self.texture)
            self.sprite.scale_x = visual_size[0] / self.texture.width
            self.sprite.scale_y = visual_size[1] / self.texture.height
        else:
            self.sprite = None

        self.open = False

    def find_item(self, item: type[AbstractItem] | str) -> Slot | None:
        if isinstance(item, str):
            for slot in self.slots:
                if (
                    not slot.itemstack.is_empty()
                    and slot.itemstack.item.NAME == item
                    and slot.discoverable
                ):
                    return slot

            return

        for slot in self.slots:
            if slot.itemstack.item == item and slot.discoverable:
                return slot

    def insert(self, itemstack: ItemStack, merge=True, span=True) -> bool:
        if itemstack.is_empty():
            return True

        added_slots: list[tuple[Slot, int]] = []

        for slot in self.slots:
            if not slot.is_picked_up_into:
                continue

            if itemstack.is_empty():
                return True

            if slot.itemstack.is_empty():
                slot.set_stack(itemstack)
                return True

            if (
                merge
                and slot.itemstack.is_compatible(itemstack)
                and (
                    span
                    or slot.itemstack.count + itemstack.count
                    < slot.itemstack.item.MAX_STACK_SIZE
                )
            ):
                added = min(
                    itemstack.count,
                    slot.itemstack.item.MAX_STACK_SIZE - slot.itemstack.count,
                )
                slot.set_stack(slot.itemstack.add_amount(added))
                added_slots.append((slot, added))
                itemstack = itemstack.add_amount(-added)

        if itemstack.count == 0:
            return True

        for slot, count in added_slots:
            slot.set_stack(slot.itemstack.add_amount(-count))

        return False

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

        self.item_info_screen.draw(window)

    def show_container(self):
        self.open = True
        CONTAINER_STACK.append(self)

    def hide_container(self):
        self.open = False
        CONTAINER_STACK.remove(self)

    def get_container_at(self, rel_x: float, rel_y: float) -> Slot | None:
        for slot in self.slots:
            if (
                slot.relative_position[0] <= rel_x <= slot.relative_position[0] + 18
                and slot.relative_position[1] <= rel_y <= slot.relative_position[1] + 18
            ):
                return slot

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

    def on_mouse_motion(
        self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int
    ):
        slot = self.get_container_at(x, y)
        self.item_info_screen.bind_to_slot(slot)

    def on_key_press(self, symbol: int, modifiers: int) -> bool:
        return False

    def on_text(self, text: str) -> bool:
        return False

    def on_resize(self, width: int, height: int):
        # for slot in self.slots:
        #     slot.on_resize(width, height)
        pass


CONTAINER_STACK: list[Container] = []


class ItemInformationScreen:
    def __init__(self):
        self.labels_batch = pyglet.graphics.Batch()
        self.labels: list[pyglet.text.Label] = []
        self.background = pyglet.shapes.Rectangle(
            0, 0, 10, 10, color=(0, 0, 0, 255), batch=self.labels_batch
        )
        self.bound_slot: Slot | None = None

    def bind_to_slot(self, slot: Slot | None):
        if slot == self.bound_slot:
            return

        if slot and slot.itemstack.is_empty():
            slot = None

        self.bound_slot = slot

        for label in self.labels:
            label.delete()
        self.labels.clear()

        if slot is None:
            return

        # top-down
        self.labels.append(
            pyglet.text.Label(
                text=slot.itemstack.item.NAME,
                batch=self.labels_batch,
                color=(255, 255, 255, 255),
                font_size=25,
            )
        )
        self.labels.append(
            pyglet.text.Label(
                text=f"{len(slot.itemstack.item.TAGS)} tag(s)",
                batch=self.labels_batch,
                color=(200, 200, 200, 255),
                font_size=22,
            )
        )
        if len(slot.itemstack.item.TAGS) < 6:
            self.labels.extend(
                pyglet.text.Label(
                    text=tag,
                    batch=self.labels_batch,
                    color=(200, 200, 200, 255),
                    font_size=20,
                )
                for tag in slot.itemstack.item.TAGS
            )

        for line in slot.itemstack.item.get_custom_hover_info(slot.itemstack):
            self.labels.append(
                pyglet.text.Label(
                    text=line,
                    batch=self.labels_batch,
                    color=(210, 210, 210, 256),
                    font_size=22,
                )
            )

        height = 0
        width = 0
        for label in reversed(self.labels):
            label.x = 10
            label.y = height + 10
            height += label.content_height
            width = max(width, label.content_width)

        self.background.width = width + 20
        self.background.height = height + 20

    def draw(self, window: Window):
        if self.bound_slot is None:
            return

        window.set_2d_centered_for_inventory(
            self.bound_slot.container,
            offset=(self.bound_slot._calculate_offset(window) + Vec3(0, 15, 0)) * 4,
            scale=0.25,
        )
        self.labels_batch.draw()
