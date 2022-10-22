import typing

import pyglet

from mcpython.client.rendering import Window
from mcpython.inventory.Slot import DefaultSlot, AbstractSlot
from mcpython.world.item.ItemStack import ItemStack
from mcpython.resources.ResourceManagement import MANAGER as RESOURCE_MANAGER


class InventoryConfig:
    def __init__(self, draw_size=(0, 0), alignment=(.5, .5)):
        self.draw_size = draw_size
        self.alignment = alignment

        self.background_sprite = None

        self.slot_definitions = []

    def add_slot(self, position: typing.Tuple[float, float], validator: typing.Callable[["DefaultSlot", ItemStack], bool] = lambda _, __: True, handler: typing.Callable[[DefaultSlot], typing.List[AbstractSlot]] = lambda e: [e]):
        self.slot_definitions.append((1, position, validator, handler))
        return self

    async def set_background_image_from_location(self, location: str):
        image = await RESOURCE_MANAGER.read_pyglet_image(location)
        self.draw_size = image.width, image.height
        self.background_sprite = pyglet.sprite.Sprite(image)
        return self

    def create_slots(self) -> typing.List[AbstractSlot]:
        slots = []

        for slot in self.slot_definitions:
            if slot[0] == 1:
                instance = DefaultSlot(*slot[1:3])
                slots += slot[3](instance)
            else:
                raise RuntimeError(slot[0])

        return slots

    def configure(self, inventory: "Inventory"):
        if self.background_sprite:
            inventory.on_foreground_draw.append(self.background_sprite.draw)


class Inventory:
    CONFIG: InventoryConfig = None

    @classmethod
    def setup(cls):
        pass

    @classmethod
    def create(cls):
        if cls.CONFIG is None:
            raise RuntimeError("No config set!")

        instance = cls(cls.CONFIG.create_slots(), cls.CONFIG.draw_size, cls.CONFIG.alignment)
        cls.CONFIG.configure(instance)
        return instance

    def __init__(self, slots: typing.List[AbstractSlot], draw_size: typing.Tuple[int, int], alignment=(.5, .5)):
        self.slots = slots
        self.draw_size = draw_size
        self.alignment = alignment
        self.on_background_draw = []
        self.on_foreground_draw = []

        self.batch = pyglet.graphics.Batch()

    async def setup_rendering(self):
        for slot in self.slots:
            slot.batch = self.batch
            await (await slot.get_underlying_itemstack()).copy_from(ItemStack("stone"))
            await slot.update_rendering_state(True)

    def draw(self):
        wx, wy = Window.WINDOW.get_size()
        sx, sy = self.draw_size
        cx, cy = self.alignment

        offset = wx * cx - sx / 2, wy * cy - sy / 2

        pyglet.gl.glTranslated(*offset, 0)

        for draw in self.on_background_draw:
            draw()

        self.batch.draw()

        for draw in self.on_foreground_draw:
            draw()

        pyglet.gl.glLoadIdentity()

