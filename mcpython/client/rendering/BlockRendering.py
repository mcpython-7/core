import typing

import pyglet

from mcpython.client.rendering.BlockModel import BlockModel
from mcpython.client.rendering.BlockModel import BlockStateFile
from mcpython.client.rendering.VertexManagement import CubeVertexCreator
from mcpython.world.block.BlockState import BlockState

from mcpython.resources.ResourceManagement import MANAGER as RESOURCE_MANAGER

pyglet.image.GL_TEXTURE_MAX_FILTER = pyglet.gl.GL_NEAREST


class BlockRenderingManager:
    def __init__(self):
        self.renderers: typing.List["BlockRenderer"] = []
        self.block_models: typing.Dict[str, BlockModel] = {}
        self.block_states: typing.Dict[str, BlockStateFile] = {}

    async def lookup_block_state_file(self, name: str):
        if name in self.block_states:
            return self.block_states[name]

        data = await RESOURCE_MANAGER.read_json("assets/{}/blockstates/{}.json".format(*name.split(":")))
        blockstate = await BlockStateFile.from_data(name, data)
        self.block_states[name] = blockstate
        return blockstate

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
        for renderer in self.renderers:
            renderer.block_state = await self.lookup_block_state_file(renderer.block_name)

        for blockstate in self.block_states.values():
            for model_name in blockstate.get_required_models():
                await self.lookup_block_model(model_name)

            await blockstate.bake()

        for model in list(self.block_models.values()):
            await model.bake()

        CubeVertexCreator.ATLAS.bake()

        for model in list(self.block_models.values()):
            await model.after_texture_atlas_bake()


MANAGER = BlockRenderingManager()


class BlockRenderer:
    def __init__(self, block_name: str):
        self.block_name = block_name
        self.block_state = None

    async def add_to_batch(self, block: BlockState, batch: pyglet.graphics.Batch):
        data = await self.block_state.add_to_batch(block, batch)

        block._set_blockstate_ref_cache(data)

    async def remove_from_batch(self, block: BlockState, batch: pyglet.graphics.Batch):
        if block._get_blockstate_ref_cache() is None:
            return

        for e in block._get_blockstate_ref_cache():
            e.delete()

        block._set_blockstate_ref_cache(None)
