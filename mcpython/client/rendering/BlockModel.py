import random
import typing
from abc import ABC

import pyglet

from mcpython.client.rendering.VertexManagement import CubeVertexCreator
from mcpython.world.block.BlockState import BlockState
from mcpython.resources.ResourceManagement import MANAGER as RESOURCE_MANAGER


class BlockModelFile:
    class BlockModelFileLink:
        @classmethod
        async def from_data(cls, data: dict | list) -> typing.List["BlockModelFile.BlockModelFileLink"]:
            result = []

            if isinstance(data, list):
                for entry in data:
                    result.append(cls(await BlockModelFile.from_name(entry["model"])))
            else:
                result.append(cls(await BlockModelFile.from_name(data["model"])))

            return result

        def __init__(self, model: "BlockModelFile"):
            self.model = model

        async def add_to_batch(self, block: BlockState, batch: pyglet.graphics.Batch):
            return self.model.add_to_batch(block, batch)

    @classmethod
    async def from_name(cls, name: str):
        return await cls.from_file("assets/{}/models/{}.json".format(*name.split(":")), name)

    @classmethod
    async def from_file(cls, filename: str, name: str = None):
        data = await RESOURCE_MANAGER.read_json(filename)
        return await cls.from_data(data, name or f"{filename.split('/')[1]}:{filename.split('/')[3:]}")

    @classmethod
    async def from_data(cls, data: dict, name: str):
        instance = cls(None if "parent" not in data else await cls.from_name(data["parent"]))
        return instance

    def __init__(self, parent: "BlockModelFile"):
        self.parent = parent
        self.elements: typing.List[CubeVertexCreator] = []

    def add_element(self, element: CubeVertexCreator):
        self.elements.append(element)

    async def add_to_batch(self, block: BlockState, batch: pyglet.graphics.Batch):
        pass


class BlockStateFile:
    class AbstractBlockStateEntry(ABC):
        @classmethod
        async def from_data(cls, data: dict) -> "BlockStateFile.AbstractBlockStateEntry":
            raise NotImplementedError

        def bake(self):
            pass

        def check_for_match(self, block: BlockState) -> bool | None:
            raise NotImplementedError

        async def add_to_batch(self, block: BlockState, batch: pyglet.graphics.Batch):
            raise NotImplementedError

    class DefaultBlockStateEntry(AbstractBlockStateEntry):
        @classmethod
        async def from_data(cls, key: str, data: dict | list) -> "BlockStateFile.DefaultBlockStateEntry":
            instance = cls({a.split("=")[0]: a.split("=")[1] for a in key.split(",")})

            instance.models += await BlockModelFile.BlockModelFileLink.from_data(data)

            return instance

        def __init__(self, key: typing.Dict[str, str]):
            self.key = key
            self.models: typing.List[BlockModelFile.BlockModelFileLink] = []

        def check_for_match(self, block: BlockState) -> bool | None:
            if block.block_state == self.key:
                return True

        async def add_to_batch(self, block: BlockState, batch: pyglet.graphics.Batch) -> list:
            data = []

            model = random.choice(self.models)
            data += model.add_to_batch(block, batch)

            return data

    class MultipartBlockStateEntry(AbstractBlockStateEntry):
        pass

    @classmethod
    async def decode_by_name(cls, name: str):
        return await cls.decode_by_file("assets/{}/blockstates/{}.json".format(*name.split(":")), name)

    @classmethod
    async def decode_by_file(cls, filename: str, name: str = None):
        data = await RESOURCE_MANAGER.read_json(filename)
        return await cls.decode_from_data(data, name or f"{filename.split('/')[1]}:{filename.split('/')[2:]}")

    @classmethod
    async def decode_from_data(cls, data: dict, name: str):
        if "variants" in data == "multipart" in data:
            if "variants" in data:
                raise ValueError(f"Cannot decode model {name}: both 'variants' and 'multipart' are present, but only one is allowed!")

            raise ValueError(f"Cannot decode model {name}: either 'variants' or 'multipart' must be present!")

        instance = cls()

        if "variants" in data:
            if isinstance(data["variants"], list):
                for key, entry in data["variants"].items():
                    instance.parts.append(await BlockStateFile.DefaultBlockStateEntry.from_data(key, entry))
            else:
                instance.parts.append(await BlockStateFile.DefaultBlockStateEntry.from_data("", data["variants"]))
        else:
            for entry in data["multipart"]:
                instance.parts.append(await BlockStateFile.MultipartBlockStateEntry.from_data(entry))

    def __init__(self):
        self.parts: typing.List[BlockStateFile.AbstractBlockStateEntry] = []

    async def add_to_batch(self, block: BlockState, batch: pyglet.graphics.Batch) -> list:
        data = []

        for part in self.parts:
            state = part.check_for_match(block)

            if state is not None:
                data += part.add_to_batch(block, batch)

                if state is True:
                    return data

        return data

