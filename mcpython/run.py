import asyncio
import os

from mcpython.client.rendering.Window import WINDOW
from mcpython.resources.ResourceManagement import MANAGER as RESOURCE_MANAGER, ArchiveResourcePath
from mcpython.client.state.StateManager import MANAGER as STATE_MANAGER
from mcpython.client.state.GameState import GameState


local = os.path.dirname(os.path.dirname(__file__))


async def setup():
    RESOURCE_MANAGER.register_path(ArchiveResourcePath(local+"/cache/assets.zip"))
    await RESOURCE_MANAGER.setup()

    version_data = await RESOURCE_MANAGER.read_json("version.json")

    print("MC VERSION", version_data["name"])

    GameState.register()
    await STATE_MANAGER.activate_state(GameState)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(setup())

    import pyglet
    pyglet.app.run()
