import typing

import pyglet

from mcpython.client.rendering.VertexManagement import CubeVertexCreator
from mcpython.world.block.BlockState import BlockState

pyglet.image.GL_TEXTURE_MAX_FILTER = pyglet.gl.GL_NEAREST


class BlockRenderingManager:
    def __init__(self):
        self.renderers: typing.List["BlockRenderer"] = []

    def bake(self):
        CubeVertexCreator.ATLAS.bake()

        for renderer in self.renderers:
            renderer.bake()


MANAGER = BlockRenderingManager()


class BlockRenderer:
    def __init__(self):
        self.cubes: typing.List[CubeVertexCreator] = []

    async def add_cube(self, size, offset, textures: typing.Iterable[str]):
        self.cubes.append(cube := CubeVertexCreator(size, offset, tuple(textures)))
        await cube.setup()

    def bake(self):
        for cube in self.cubes:
            cube.bake()

    async def add_to_batch(self, block: BlockState, batch: pyglet.graphics.Batch):
        block._set_blockstate_ref_cache(
            [cube.add_to_batch(block.world_position, batch) for cube in self.cubes]
        )

    async def remove_from_batch(self, block: BlockState, batch: pyglet.graphics.Batch):
        if block._get_blockstate_ref_cache() is None:
            return

        for e in block._get_blockstate_ref_cache():
            e.delete()

        block._set_blockstate_ref_cache(None)
