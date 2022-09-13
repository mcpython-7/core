import pyglet

from mcpython.client.rendering.VertexManagement import CubeVertexCreator
from mcpython.world.block.BlockState import BlockState

pyglet.image.GL_TEXTURE_MAX_FILTER = pyglet.gl.GL_NEAREST


class BlockRenderer:
    RENDERER = CubeVertexCreator((1, 1, 1), (0, 0, 0), "assets/minecraft/textures/block/stone.png")

    async def add_to_batch(self, block: BlockState, batch: pyglet.graphics.Batch):
        if not self.RENDERER._had_setup:
            await self.RENDERER.setup()
            self.RENDERER.ATLAS.bake()
            self.RENDERER.bake()

        block._set_blockstate_ref_cache(self.RENDERER.add_to_batch(block.world_position, batch))
