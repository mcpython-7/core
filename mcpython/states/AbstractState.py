from abc import ABC


class AbstractState(ABC):
    NAME: str = None

    def on_activate(self):
        from mcpython.rendering.Window import Window

        # call an on_resize() event as the size might have changed in between
        self.on_resize(*Window.INSTANCE.get_size())

        # call an on_mouse_motion event as the mouse might have moved
        self.on_mouse_motion(*Window.INSTANCE.mouse_position, 0, 0, 0, 0)

        # todo: maybe press all currently active keys and buttons?

    def on_deactivate(self):
        from mcpython.rendering.Window import Window

        # Release all currently pressed keys and mouse buttons when leaving the state
        for key, state in Window.INSTANCE.key_state_handler.data.items():
            if state:
                self.on_key_release(key, 0)

        for button, state in Window.INSTANCE.mouse_state_handler.data.items():
            if state and button not in ("x", "y"):
                self.on_mouse_release(button, 0)

    def on_mouse_press(self, button: int, modifiers: int):
        pass

    def on_mouse_release(self, button: int, modifiers: int):
        pass

    def on_mouse_motion(
        self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
    ):
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        pass

    def on_key_release(self, symbol: int, modifiers: int):
        pass

    def on_draw(self):
        pass

    def on_resize(self, w: int, h: int):
        pass

    def on_tick(self):
        pass
