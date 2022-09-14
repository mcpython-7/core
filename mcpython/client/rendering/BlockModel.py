import random
import traceback
import typing
from abc import ABC

import pyglet

from mcpython.client.rendering.VertexManagement import CubeVertexCreator
from mcpython.world.block.BlockState import BlockState
from mcpython.resources.ResourceManagement import MANAGER as RESOURCE_MANAGER


RENDERING_ORDER = [
    "up",
    "down",
    "north",
    "south",
    "east",
    "west",
]


class BlockModel:
    @classmethod
    async def load_from_file(cls, name: str, file: str) -> "BlockModel":
        data: dict = await RESOURCE_MANAGER.read_json(file)
        instance = cls(name, data["parent"] if "parent" in data else None)

        instance.textures.update(data.setdefault("textures", {}))

        for element in data.setdefault("elements", []):
            start = element["from"]
            end = element["to"]

            position = tuple((a + b) / 2 / 8 - .5 for a, b in zip(start, end))
            size = tuple(abs(a - b) / 16 for a, b in zip(start, end))

            cube = CubeVertexCreator(size, position, ("MISSING_TEXTURE",) * 6)
            cube.raw_textures = [None] * 6

            # todo: parse rotation & shade

            for key, face in element["faces"].items():
                index = RENDERING_ORDER.index(key)

                texture = face["texture"]
                # todo: parse cull-face
                # rotation = face["rotation"]  # todo: use by rotating some vertex data / uv data
                # todo: parse tint index

                cube.raw_textures[index] = texture
                cube.uvs[index] = tuple(face["uv"]) if "uv" in face else (0, 0, 1, 1)

            instance.cubes.append(cube)

        return instance

    def __init__(self, name: str, parent: typing.Union[str, "BlockModel"] = None):
        self.name = name
        self.parent = parent

        self.textures: typing.Dict[str, str] = {}
        self.cubes: typing.List[CubeVertexCreator] = []

        self.can_be_rendered = False
        self.baked = False

    async def bake(self):
        if self.baked:
            return

        self.baked = True

        if isinstance(self.parent, str):
            from mcpython.client.rendering.BlockRendering import MANAGER

            self.parent = await MANAGER.lookup_block_model(self.parent)
            await self.parent.bake()

            self.textures = self.parent.textures | self.textures

            if len(self.cubes) == 0:
                for cube in self.parent.cubes:
                    new_cube = await cube.copy(("MISSING_TEXTURE",) * 6)
                    new_cube.raw_textures = cube.raw_textures
                    self.cubes.append(new_cube)

        try:
            for cube in self.cubes:
                cube.texture_paths = [
                    "assets/{}/textures/{}.png".format(*self.lookup_texture(t).split(":")) if t is not None else "MISSING_TEXTURE"
                    for t in cube.raw_textures
                ]
                await cube.setup()

            self.can_be_rendered = True
        except ValueError:
            # print(cube, self.name, cube.raw_textures, self.textures)
            # traceback.print_exc()
            self.can_be_rendered = False

            for cube in self.cubes:
                cube.texture_paths = ("MISSING_TEXTURE",) * 6

    async def after_texture_atlas_bake(self):
        if not self.can_be_rendered:
            return

        for cube in self.cubes:
            cube.bake()

    async def add_to_batch(self, block: BlockState, batch: pyglet.graphics.Batch) -> list:
        if not self.can_be_rendered:
            raise RuntimeError(f"tried to render not render-able model {self.name}!")

        data = []

        for cube in self.cubes:
            data.append(cube.add_to_batch(block.world_position, batch))

        return data

    def lookup_texture(self, texture: str):
        if ":" in texture:
            return texture

        texture = texture.removeprefix("#")

        if texture in self.textures:
            return self.lookup_texture(self.textures[texture])

        if "#" + texture in self.textures:
            return self.lookup_texture(self.textures[texture])

        if texture.startswith("block/"):
            return "minecraft:"+texture

        raise ValueError(texture)

