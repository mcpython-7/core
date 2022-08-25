import pyglet

from mcpython.client.state.AbstractState import AbstractState
from mcpython.client.rendering.Window import WINDOW


class WorldRenderingContainer:
    def __init__(self):
        self.normal_3d_batch = pyglet.graphics.Batch()

        self.overlay_batch = pyglet.graphics.Batch()


RENDERING_CONTAINER: WorldRenderingContainer = None


class GameState(AbstractState):
    NAME = "minecraft:game"

    def __init__(self):
        super().__init__()

        global RENDERING_CONTAINER
        self._rendering_container = RENDERING_CONTAINER = WorldRenderingContainer()

    async def setup(self):
        self.window_handler.subscribe("on_draw", self.on_draw)

    async def on_draw(self, dt: float):
        WINDOW.set_3d()

        self._rendering_container.normal_3d_batch.draw()

        pyglet.gl.glClear(pyglet.gl.GL_DEPTH_BUFFER_BIT)

        WINDOW.set_2d()
        self._rendering_container.overlay_batch.draw()

        pyglet.gl.glClear(pyglet.gl.GL_DEPTH_BUFFER_BIT)



