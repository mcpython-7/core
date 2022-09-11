import asyncio
import logging
import os
from asyncio import log as _async_log

local = os.path.dirname(os.path.dirname(__file__))

_async_log.logger.disabled = True

os.makedirs(local+"/cache/logs", exist_ok=True)
logging.basicConfig(format="[%(name)s][%(levelname)s]: %(message)s", level=logging.DEBUG)

from mcpython.resources.ResourceManagement import (
    MANAGER as RESOURCE_MANAGER,
    ArchiveResourcePath,
    FolderResourcePath,
)
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

    logging.info(f"MC VERSION {version_data['name']}")

    from mcpython.client.state.GameState import GameState

    GameState.register()

    from mcpython.client.state.StateManager import MANAGER as STATE_MANAGER
    await STATE_MANAGER.activate_state(GameState)

    from mcpython.world.TaskScheduler import WORKER
    WORKER.start()


if __name__ == "__main__":
    from mcpython.client.rendering.Window import WINDOW

    asyncio.run(setup())

    import pyglet

    pyglet.app.run()
