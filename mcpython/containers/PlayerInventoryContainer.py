from __future__ import annotations

from mcpython.containers.AbstractContainer import Container, Slot
from mcpython.containers.ItemStack import ItemStack
from mcpython.resources.ResourceManager import ResourceManager
from mcpython.world.items.AbstractItem import Stone, Dirt


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

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if not super().on_mouse_press(x, y, button, modifiers):
            return False

        print(x, y)

        return True
