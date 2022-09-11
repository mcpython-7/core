import PIL.Image
import pyglet

from mcpython.resources.ResourceManagement import MANAGER


class ResourceLocation:
    def __init__(self, location: str):
        self.location = location

    async def read_bytes(self) -> bytes:
        return await MANAGER.read_bytes(self.location)

    async def read_json(self):
        return await MANAGER.read_json(self.location)

    async def read_pillow_image(self) -> PIL.Image.Image:
        return await MANAGER.read_pillow_image(self.location)

    async def read_pyglet_image(self) -> pyglet.image.AbstractImage:
        return await MANAGER.read_pyglet_image(self.location)

    async def read_nbt(self):
        return await MANAGER.read_nbt(self.location)

