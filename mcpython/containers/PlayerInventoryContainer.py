from __future__ import annotations

import typing

import pyglet.sprite

from mcpython.containers.AbstractContainer import Container, Slot, SlotRenderCopy
from mcpython.containers.ItemStack import ItemStack
from mcpython.crafting.GridRecipes import GridRecipeManager
from mcpython.resources.ResourceManager import ResourceManager
from mcpython.world.items.AbstractItem import ITEMS

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
        self.player_crafting_slots = [
            Slot(self, (98, 114), discoverable=False, is_picked_up_into=False),
            Slot(self, (98 + 18, 114), discoverable=False, is_picked_up_into=False),
            Slot(self, (98, 114 + 18), discoverable=False, is_picked_up_into=False),
            Slot(
                self,
                (98 + 18, 114 + 18),
                discoverable=False,
                is_picked_up_into=False,
            ),
            Slot(
                self,
                (154, 122),
                discoverable=False,
                is_picked_up_into=False,
                allow_player_insertion=False,
                allow_right_click=False,
            ),
        ]
        self.player_crafting_provider = GridRecipeManager(
            self,
            (2, 2),
            (
                (self.player_crafting_slots[0], self.player_crafting_slots[2]),
                (self.player_crafting_slots[1], self.player_crafting_slots[3]),
            ),
            self.player_crafting_slots[4],
        )

        self.slots = (
            [
                Slot(self, (8 + 18 * i, 8), on_update=self._on_hotbar_update)
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
            # Crafting Slots
            + self.player_crafting_slots
        )

        self.selected_slot = 0

    def _on_hotbar_update(self, slot: Slot, itemstack: ItemStack):
        if self.slots.index(slot) == self.selected_slot:
            from mcpython.rendering.Window import Window

            Window.INSTANCE.player.update_breaking_block(force_reset=True)

    def hide_container(self):
        super().hide_container()

        for slot in self.player_crafting_slots[:4]:
            self.insert(slot.itemstack)
            slot.set_stack(ItemStack.EMPTY, update=False)

        self.player_crafting_slots[-1].set_stack(ItemStack.EMPTY, update=False)
        self.player_crafting_provider.current_recipe = None

    def get_selected_slot(self) -> Slot:
        return self.slots[self.selected_slot]

    def get_selected_itemstack(self) -> ItemStack:
        return self.slots[self.selected_slot].itemstack

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if not super().on_mouse_press(x, y, button, modifiers):
            return False

        print(x, y)

        return True


class HotbarContainer(Container):
    SHOULD_DRAW_MOVING_SLOT = False

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
        self.hotbar_selection_sprite.position = (pos.x - 4, pos.y - 5, 0)
        self.hotbar_selection_sprite.draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> bool:
        # we don't allow interaction with these slots
        return False

    def on_close_with_escape(self):
        pass
