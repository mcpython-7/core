import asyncio

from mcpython.client.rendering.Window import WINDOW
from mcpython.client.state.StateManager import MANAGER
from mcpython.client.state.GameState import GameState


async def setup():
    GameState.register()
    await MANAGER.activate_state(GameState)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(setup())

    import pyglet
    pyglet.app.run()
