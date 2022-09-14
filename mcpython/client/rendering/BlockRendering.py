import typing

import pyglet

from mcpython.client.rendering.BlockModel import BlockModel
from mcpython.client.rendering.VertexManagement import CubeVertexCreator
from mcpython.world.block.BlockState import BlockState

pyglet.image.GL_TEXTURE_MAX_FILTER = pyglet.gl.GL_NEAREST


class BlockRenderingManager:
    def __init__(self):
        self.renderers: typing.List["BlockRenderer"] = []
        self.block_models: typing.Dict[str, BlockModel] = {}

    async def lookup_block_model(self, name: str) -> BlockModel:
        if name not in self.block_models:
            return await self.load_block_model(name)

        return self.block_models[name]

    async def load_block_model(self, name: str) -> BlockModel:
        if ":" not in name:
            name = "minecraft:" + name

        model = await BlockModel.load_from_file(name, "assets/{}/models/{}.json".format(*name.split(":")))
        self.block_models[name] = model
        return model

    async def bake(self):
        for model in list(self.block_models.values()):
            await model.bake()

        CubeVertexCreator.ATLAS.bake()

        for model in list(self.block_models.values()):
            await model.after_texture_atlas_bake()


MANAGER = BlockRenderingManager()


class BlockRenderer:
    def __init__(self):
        self.block_models: typing.List[BlockModel] = []

    async def add_block_model(self, block_model: BlockModel | None):
        if isinstance(block_model, str):
            block_model = await MANAGER.lookup_block_model(block_model)

        self.block_models.append(block_model)

    async def add_to_batch(self, block: BlockState, batch: pyglet.graphics.Batch):
        data = []

        for model in self.block_models:
            data += await model.add_to_batch(block, batch)

        block._set_blockstate_ref_cache(data)

    async def remove_from_batch(self, block: BlockState, batch: pyglet.graphics.Batch):
        if block._get_blockstate_ref_cache() is None:
            return

        for e in block._get_blockstate_ref_cache():
            e.delete()

        block._set_blockstate_ref_cache(None)
