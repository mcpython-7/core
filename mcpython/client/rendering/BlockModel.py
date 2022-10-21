import random
import traceback
import typing
from abc import ABC

import pyglet

from mcpython.client.rendering.VertexManagement import CubeVertexCreator
from mcpython.world.block.BlockState import BlockState
from mcpython.resources.ResourceManagement import MANAGER as RESOURCE_MANAGER


# see https://minecraft.fandom.com/wiki/Tutorials/Models for specs


RENDERING_ORDER = [
    "up",
    "down",
    "east",
    "north",
    "south",
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

            size = tuple(abs(a - b) / 16 for a, b in zip(start, end))
            position = tuple(0.5 - (a + b) / 32 for a, b in zip(start, end))

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
                cube.uvs[index] = tuple(e / 16 for e in face["uv"]) if "uv" in face else (0, 0, 1, 1)

            instance.cubes.append(cube)

        return instance

    def __init__(self, name: str, parent: typing.Union[str, "BlockModel"] = None):
        self.name = name
        self.parent = parent

        self.textures: typing.Dict[str, str] = {}
        self.cubes: typing.List[CubeVertexCreator] = []

        self.rotation = 0, 0, 0

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
                    "assets/{}/textures/{}.png".format(
                        *self.lookup_texture(t).split(":")
                    )
                    if t is not None
                    else "MISSING_TEXTURE"
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

    async def add_to_batch(
        self, block: BlockState, batch: pyglet.graphics.Batch, rotation: typing.Tuple[float, float, float]
    ) -> list:
        if not self.can_be_rendered:
            raise RuntimeError(f"tried to render not render-able model {self.name}!")

        data = []

        for cube in self.cubes:
            data.append(cube.add_to_batch(block.world_position, batch, rotation=tuple(a + b for a, b in zip(self.rotation, rotation))))

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
            return "minecraft:" + texture

        raise ValueError(texture)


class BlockStateFile:
    class ModelLink:
        @classmethod
        async def from_data(cls, data: dict | list) -> "BlockStateFile.ModelLink":
            if isinstance(data, dict):
                instance = cls(data["model"])

                rot = [0, 0, 0]
                if "x" in data:
                    rot[0] = data["x"]
                if "y" in data:
                    rot[1] = data["y"]
                if "z" in data:
                    rot[2] = data["z"]

                instance.rotation = tuple(rot)

            elif isinstance(data, list):
                instance = cls()

                instance.models += [
                    await BlockStateFile.ModelLink.from_data(e) for e in data
                ]

            else:
                instance = cls()

            return instance

        def __init__(self, *model_name: str):
            self.model_names = list(model_name)
            self.models: typing.List[BlockStateFile.ModelLink | BlockModel] = []

            self.rotation = 0, 0, 0
            self.uv_lock = False
            self.weight = 1

        async def bake(self):
            from mcpython.client.rendering.BlockRendering import MANAGER

            for name in self.model_names:
                self.models.append(model := await MANAGER.lookup_block_model(name))

                if not model.baked:
                    await model.bake()

            for model in self.models:
                if isinstance(model, BlockStateFile.ModelLink):
                    await model.bake()

        async def add_to_batch(
            self, block: BlockState, batch: pyglet.graphics.Batch, rotation=(0, 0, 0)
        ) -> list:
            if not self.models:
                return []

            return await random.choice(self.models).add_to_batch(block, batch, rotation=tuple(a + b for a, b in zip(self.rotation, rotation)))

        def get_model_names(self) -> typing.List[str]:
            return self.model_names + sum(
                (
                    model.get_model_names()
                    for model in self.models
                    if isinstance(model, BlockStateFile.ModelLink)
                ),
                [],
            )

    class MultipartCondition:
        @classmethod
        async def from_data(cls, data: dict):
            instance = cls(BlockStateFile.ModelLink.from_data(data), when=data.setdefault("when", None))
            return instance

        def __init__(self, model: "BlockStateFile.ModelLink", when: dict = None):
            self.model = model
            self.when = when

        async def add_to_batch(
            self, block: BlockState, batch: pyglet.graphics.Batch
        ) -> list:
            return await self.model.add_to_batch(block, batch)

        async def bake(self):
            await self.model.bake()

        def check_match(self, block: BlockState) -> bool:
            state = block.block_state
            return self.when is None or all(key in state and state[key] == value for key, value in self.when.items())

    @classmethod
    async def from_data(cls, name: str, data: dict):
        instance = cls()

        if "variants" in data:
            if "multipart" in data:
                raise ValueError

            for key, model in data["variants"].items():
                if key == "" or key == "default":
                    key = {}
                else:
                    key = {e.split("=")[0]: e.split("=")[1] for e in key.split(",")}

                link = await BlockStateFile.ModelLink.from_data(model)
                instance.variants.append((key, link))

        elif "multipart" in data:
            for entry in data["multipart"]:
                instance.multipart_items.append(
                    (
                        await BlockStateFile.MultipartCondition.from_data(
                            entry.setdefault("when", {})
                        ),
                        await BlockStateFile.ModelLink.from_data(entry["apply"]),
                    )
                )
        else:
            raise ValueError

        return instance

    def __init__(self):
        self.variants: typing.List[typing.Tuple[dict, BlockStateFile.ModelLink]] = []
        self.multipart_items: typing.List[
            typing.Tuple[BlockStateFile.MultipartCondition, BlockStateFile.ModelLink]
        ] = []

    def get_required_models(self) -> typing.List[str]:
        return sum([e[1].get_model_names() for e in self.variants], []) + sum(
            [e[1].get_model_names() for e in self.multipart_items], []
        )

    async def bake(self):
        for _, model in self.variants:
            await model.bake()

        for _, model in self.multipart_items:
            await model.bake()

    async def add_to_batch(
        self, block: BlockState, batch: pyglet.graphics.Batch
    ) -> list:
        for key, model in self.variants:
            if key == block.block_state:
                return await model.add_to_batch(block, batch)

        data = []

        for condition, model in self.multipart_items:
            if condition.check_match(block):
                data += await model.add_to_batch(block, batch)

        return data
