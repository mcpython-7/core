import asyncio

from mcpython.inventory.Inventory import InventoryConfig, Inventory


class HotbarInventory(Inventory):
    @classmethod
    async def setup(cls):
        cls.CONFIG = await InventoryConfig(alignment=(.5, 0)).add_slot((0, 0)).set_background_image_from_location("assets/minecraft/textures/gui/widgets.png")

