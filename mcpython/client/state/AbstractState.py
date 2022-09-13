import typing
from abc import ABC
from mcpython.backend.EventHandler import EventHandler
from mcpython.client.rendering.Window import WINDOW


class AbstractState(ABC):
    NAME: str = None

    # set by manager
    INSTANCE: "AbstractState" = None

    @classmethod
    @typing.final
    def register(cls):
        from mcpython.client.state.StateManager import MANAGER

        MANAGER.register_state(cls)

    def __init__(self):
        self.window_handler: EventHandler = WINDOW.event_handler.create_child_handler(f"event handler for state {self.NAME}")
        self._is_set_up = False

    async def setup(self):
        pass

    async def on_activate(self):
        pass

    async def on_deactivate(self):
        pass
