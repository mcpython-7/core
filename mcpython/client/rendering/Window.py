import asyncio
import time
import typing

import pyglet
from pyglet.math import Mat4

from mcpython.backend.EventHandler import EventHandler


class GameWindow(pyglet.window.Window):
    def __init__(self):
        super().__init__()
        self.set_caption("mcpython 7 - development version")
        self.set_size(800, 600)

        self.event_handler = EventHandler()
        self.event_handler.register_event_type("on_draw")  # dt
        self.event_handler.register_event_type("on_tick")  # dt
        # symbol, modifiers, time since last press (or -1)
        self.event_handler.register_event_type("on_key_press:cancelable")
        # symbol, modifiers, time since last press (or -1)
        self.event_handler.register_event_type("on_key_press")
        # symbol, modifiers, duration
        self.event_handler.register_event_type("on_key_release:cancelable")
        # symbol, modifiers, duration
        self.event_handler.register_event_type("on_key_release")

        # x, y, dx, dy, button, modifiers
        self.event_handler.register_event_type("on_mouse_motion:cancelable")
        # x, y, dx, dy, button, modifiers
        self.event_handler.register_event_type("on_mouse_motion")

        # width, height
        self.event_handler.register_event_type("on_resize")

        self._key_press_duration: typing.Dict[int, float] = {}
        self._last_key_press_time: typing.Dict[int, float] = {}
        self.__mouse_position = (0, 0)

        self.key_handler = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.key_handler)

        pyglet.clock.schedule_interval(self.on_tick, 1 / 20)

    def get_mouse_position(self):
        return self.__mouse_position

    mouse_position = property(get_mouse_position)

    def on_activate(self):
        # Clear these dicts as we cannot be sure that all is correct
        self._key_press_duration.clear()
        self._last_key_press_time.clear()

    def on_draw(self, dt: float = 0):
        pyglet.gl.glClearColor(1, 1, 1, 1)
        self.clear()

        asyncio.get_event_loop().run_until_complete(
            self.event_handler.invoke_event(
                "on_draw", args=(dt,), run_parallel=False, ignore_exceptions=True
            )
        )

    def on_tick(self, dt: float):
        asyncio.get_event_loop().run_until_complete(
            self.event_handler.invoke_event(
                "on_tick", args=(dt,), ignore_exceptions=True
            )
        )

    def on_key_press(self, symbol, modifiers):
        self._key_press_duration[symbol] = time.time()

        if symbol in self._last_key_press_time:
            last_invoke = time.time() - self._last_key_press_time[symbol]
        else:
            last_invoke = -1

        asyncio.get_event_loop().run_until_complete(
            self.event_handler.invoke_cancelable(
                "on_key_press:cancelable",
                args=(symbol, modifiers, last_invoke),
                ignore_exceptions=True,
            )
        )
        asyncio.get_event_loop().run_until_complete(
            self.event_handler.invoke_event(
                "on_key_press",
                args=(symbol, modifiers, last_invoke),
                ignore_exceptions=True,
            )
        )

    def on_key_release(self, symbol, modifiers):
        self._last_key_press_time[symbol] = time.time()

        duration = time.time() - self._key_press_duration[symbol]

        asyncio.get_event_loop().run_until_complete(
            self.event_handler.invoke_cancelable(
                "on_key_release:cancelable",
                args=(symbol, modifiers, duration),
                ignore_exceptions=True,
            )
        )
        asyncio.get_event_loop().run_until_complete(
            self.event_handler.invoke_event(
                "on_key_release",
                args=(symbol, modifiers, duration),
                ignore_exceptions=True,
            )
        )

    def on_mouse_motion(self, x, y, dx, dy):
        self.__mouse_position = x, y

        asyncio.get_event_loop().run_until_complete(
            self.event_handler.invoke_cancelable(
                "on_mouse_motion:cancelable",
                args=(x, y, dx, dy, 0, 0),
                ignore_exceptions=True,
            )
        )
        asyncio.get_event_loop().run_until_complete(
            self.event_handler.invoke_event(
                "on_mouse_motion",
                args=(x, y, dx, dy, 0, 0),
                ignore_exceptions=True,
            )
        )

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.__mouse_position = x, y

        asyncio.get_event_loop().run_until_complete(
            self.event_handler.invoke_cancelable(
                "on_mouse_motion:cancelable",
                args=(x, y, dx, dy, buttons, modifiers),
                ignore_exceptions=True,
            )
        )
        asyncio.get_event_loop().run_until_complete(
            self.event_handler.invoke_event(
                "on_mouse_motion",
                args=(x, y, dx, dy, buttons, modifiers),
                ignore_exceptions=True,
            )
        )

    def on_resize(self, width, height):
        super().on_resize(width, height)

        asyncio.get_event_loop().run_until_complete(
            self.event_handler.invoke_event(
                "on_resize",
                args=(width, height),
                ignore_exceptions=True,
            )
        )

    def set_2d(self):
        width, height = self.get_size()
        self.projection = Mat4.orthogonal_projection(0, width, 0, height, -255, 255)

    def set_3d(self):
        width, height = self.get_size()
        self.projection = Mat4.perspective_projection(width / height, .1, 100)


WINDOW = GameWindow()
