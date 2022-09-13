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

    async def add_cube(self, size, offset, texture: str):
        self.cubes.append(cube := CubeVertexCreator(size, offset, texture))
        await cube.setup()

    def bake(self):
        for cube in self.cubes:
            cube.bake()

    async def add_to_batch(self, block: BlockState, batch: pyglet.graphics.Batch):
        block._set_blockstate_ref_cache([
            cube.add_to_batch(block.world_position, batch)
            for cube in self.cubes
        ])
