import asyncio

import pyglet
from mcpython.backend.EventHandler import EventHandler


class GameWindow(pyglet.window.Window):
    def __init__(self):
        super().__init__()
        self.set_caption("mcpython 7 - development version")
        self.set_size(800, 600)
        self.event_handler = EventHandler()
        self.event_handler.register_event_type("on_draw")

    def on_draw(self, dt: float = 0):
        pyglet.gl.glClearColor(1, 1, 1, 1)
        self.clear()

        asyncio.get_event_loop().run_until_complete(self.event_handler.invoke_event("on_draw", run_parallel=False, ignore_exceptions=True))


WINDOW = GameWindow()

