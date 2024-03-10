from __future__ import annotations

from mcpython.containers.AbstractContainer import Container, Slot
from mcpython.containers.ItemStack import ItemStack
from mcpython.resources.ResourceManager import ResourceManager
from mcpython.world.items.AbstractItem import Stone


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
        self.slots = [
            Slot(
                self,
                (0, 0),
            ).set_stack(ItemStack(Stone)),
        ]

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if not super().on_mouse_press(x, y, button, modifiers):
            return False

        print(x, y)

        return True
