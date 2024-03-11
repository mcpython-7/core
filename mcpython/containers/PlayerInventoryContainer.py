from __future__ import annotations

import typing

import pyglet.sprite

from mcpython.containers.AbstractContainer import Container, Slot, SlotRenderCopy
from mcpython.containers.ItemStack import ItemStack
from mcpython.resources.ResourceManager import ResourceManager
from mcpython.world.items.AbstractItem import Stone, Dirt

if typing.TYPE_CHECKING:
    from mcpython.rendering.Window import Window


class PlayerInventoryContainer(Container):
    def __init__(self):
        super().__init__(
            (175, 165),
            ResourceManager.load_image(
                "assets/minecraft/textures/gui/container/inventory.png"
            )
            .get_region((0, 0), (175, 165))
            .to_pyglet(),
        )
        i = 0
        self.slots = (
            [
                Slot(
                    self,
                    (8 + 18 * i, 8),
                ).set_stack(ItemStack(Dirt))
                for i in range(9)
            ]
            + [
                Slot(
                    self,
                    (8 + 18 * i, 30),
                )
                for i in range(9)
            ]
            + [
                Slot(
                    self,
                    (8 + 18 * i, 48),
                )
                for i in range(9)
            ]
            + [
                Slot(
                    self,
                    (8 + 18 * i, 66),
                )
                for i in range(9)
            ]
        )
        self.selected_slot = 0

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if not super().on_mouse_press(x, y, button, modifiers):
            return False

        print(x, y)

        return True


class HotbarContainer(Container):
    def __init__(self, player_inventory: PlayerInventoryContainer):
        super().__init__(
            (182, 22),
            ResourceManager.load_image(
                "assets/minecraft/textures/gui/sprites/hud/hotbar.png"
            ).to_pyglet(),
        )
        self.hotbar_selection = ResourceManager.load_image(
            "assets/minecraft/textures/gui/sprites/hud/hotbar_selection.png"
        ).to_pyglet()
        self.hotbar_selection_sprite = pyglet.sprite.Sprite(self.hotbar_selection)

        self.player_inventory = player_inventory
        self.render_anchor = (0.5, 0.1)
        self.render_offset = (0, 0)
        self.image_anchor = (0.5, 0)

        self.slots = [
            SlotRenderCopy(self, (3 + 20 * i, 15), player_inventory.slots[i])
            for i in range(9)
        ]

    def draw(self, window: Window):
        super().draw(window)
        pos = self.slots[self.player_inventory.selected_slot]._calculate_offset(window)
        self.hotbar_selection_sprite.position = (pos.x - 5, pos.y - 5, 0)
        self.hotbar_selection_sprite.draw()
