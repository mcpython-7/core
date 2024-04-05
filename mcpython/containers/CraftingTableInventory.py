from __future__ import annotations

import typing


from mcpython.containers.AbstractContainer import Container, Slot, SlotRenderCopy
from mcpython.crafting.GridRecipes import GridRecipeManager
from mcpython.resources.ResourceManager import ResourceManager


class CraftingTableContainer(Container):
    def __init__(self):
        super().__init__(
            (175, 165),
            ResourceManager.load_image(
                "assets/minecraft/textures/gui/container/crafting_table.png"
            )
            .get_region((0, 0), (175, 165))
            .to_pyglet(),
        )

        self.crafting_slots = [
            Slot(
                self,
                (30 + 18 * 0, 97 + 18 * 0),
                discoverable=False,
                is_picked_up_into=False,
            ),
            Slot(
                self,
                (30 + 18 * 1, 97 + 18 * 0),
                discoverable=False,
                is_picked_up_into=False,
            ),
            Slot(
                self,
                (30 + 18 * 2, 97 + 18 * 0),
                discoverable=False,
                is_picked_up_into=False,
            ),
            Slot(
                self,
                (30 + 18 * 0, 97 + 18 * 1),
                discoverable=False,
                is_picked_up_into=False,
            ),
            Slot(
                self,
                (30 + 18 * 1, 97 + 18 * 1),
                discoverable=False,
                is_picked_up_into=False,
            ),
            Slot(
                self,
                (30 + 18 * 2, 97 + 18 * 1),
                discoverable=False,
                is_picked_up_into=False,
            ),
            Slot(
                self,
                (30 + 18 * 0, 97 + 18 * 2),
                discoverable=False,
                is_picked_up_into=False,
            ),
            Slot(
                self,
                (30 + 18 * 1, 97 + 18 * 2),
                discoverable=False,
                is_picked_up_into=False,
            ),
            Slot(
                self,
                (30 + 18 * 2, 97 + 18 * 2),
                discoverable=False,
                is_picked_up_into=False,
            ),
            Slot(
                self,
                (123, 115),
                discoverable=False,
                is_picked_up_into=False,
                allow_player_insertion=False,
                allow_right_click=False,
            ),
        ]
        self.crafting_provider = GridRecipeManager(
            self,
            (3, 3),
            (
                (
                    self.crafting_slots[0],
                    self.crafting_slots[3],
                    self.crafting_slots[6],
                ),
                (
                    self.crafting_slots[1],
                    self.crafting_slots[4],
                    self.crafting_slots[7],
                ),
                (
                    self.crafting_slots[2],
                    self.crafting_slots[5],
                    self.crafting_slots[8],
                ),
            ),
            self.crafting_slots[9],
        )

        from mcpython.rendering.Window import Window

        player_inventory = Window.INSTANCE.player.inventory

        self.slots = (
            [
                SlotRenderCopy(
                    self,
                    (8 + 18 * i, 8),
                    player_inventory.slots[i],
                )
                for i in range(9)
            ]
            + [
                SlotRenderCopy(
                    self,
                    (8 + 18 * i, 30),
                    player_inventory.slots[i + 9],
                )
                for i in range(9)
            ]
            + [
                SlotRenderCopy(
                    self,
                    (8 + 18 * i, 48),
                    player_inventory.slots[i + 18],
                )
                for i in range(9)
            ]
            + [
                SlotRenderCopy(
                    self,
                    (8 + 18 * i, 66),
                    player_inventory.slots[i + 27],
                )
                for i in range(9)
            ]
            # Crafting Slots
            + self.crafting_slots
        )

    def hide_container(self):
        super().hide_container()
        #
        # for slot in self.slots[:9]:
        #     self.insert(slot.itemstack)
        #     slot.set_stack(ItemStack.EMPTY, update=False)
        #
        # self.slots[-1].set_stack(ItemStack.EMPTY, update=False)
        # self.crafting_provider.current_recipe = None

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if not super().on_mouse_press(x, y, button, modifiers):
            return False

        print(x, y)

        return True
