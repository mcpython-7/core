import typing

from mcpython.client.state.AbstractState import AbstractState


class _StateManager:
    def __init__(self):
        self.states: typing.Dict[str, AbstractState] = {}
        self.__active_state: AbstractState | None = None

    def register_state(self, state: typing.Type[AbstractState]):
        if state.NAME is None:
            raise ValueError(f"'NAME' of {state} not set!")

        self.states[state.NAME] = state.INSTANCE = state()
        return state

    async def activate_state(
        self, name: str | AbstractState | typing.Type[AbstractState] | None
    ):
        try:
            is_sub = issubclass(name, AbstractState)
        except TypeError:
            pass
        else:
            if is_sub:
                name = name.NAME

        if self.__active_state is not None:
            await self.__active_state.on_deactivate()
            self.__active_state.window_handler.disable()

        self.__active_state = name if not isinstance(name, str) else self.states[name]

        if self.__active_state is not None:
            if not self.__active_state._is_set_up:
                await self.__active_state.setup()

            await self.__active_state.on_activate()
            self.__active_state.window_handler.enable()


MANAGER = _StateManager()
