import asyncio
import os

from mcpython.client.rendering.Window import WINDOW
from mcpython.resources.ResourceManagement import (
    MANAGER as RESOURCE_MANAGER,
    ArchiveResourcePath,
    FolderResourcePath,
)
from mcpython.client.state.StateManager import MANAGER as STATE_MANAGER
from mcpython.client.state.GameState import GameState
from mcpython.world.World import WORLD
from mcpython.backend.Registry import init as init_registries


local = os.path.dirname(os.path.dirname(__file__))


async def setup():
    from mcpython.world.block import Blocks

    await init_registries()

    await WORLD.setup_default()

    RESOURCE_MANAGER.register_path(FolderResourcePath(local))
    RESOURCE_MANAGER.register_path(ArchiveResourcePath(local + "/cache/assets.zip"))
    RESOURCE_MANAGER.register_path(FolderResourcePath(local+"/cache"))
    await RESOURCE_MANAGER.setup()

    version_data = await RESOURCE_MANAGER.read_json("version.json")

    print("MC VERSION", version_data["name"])

    GameState.register()
    await STATE_MANAGER.activate_state(GameState)


if __name__ == "__main__":
    asyncio.run(setup())

    import pyglet

    pyglet.app.run()
