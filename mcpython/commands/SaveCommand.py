from mcpython.commands.Command import Command, FixedString, AnyString
from mcpython.config import TMP
from mcpython.containers.ItemStack import ItemStack
from mcpython.world.items.AbstractItem import AbstractItem


save_world_name = AnyString()
save_world = FixedString("save").then(save_world_name)
load_world_name = AnyString()
load_world = FixedString("load").then(load_world_name)
save_command = Command("save")
save_command.construct().then(save_world).then(load_world)


@save_world_name.on_execute
def execute_save_world(chat, entries):
    from mcpython.world.World import World

    w = World.INSTANCE
    name = entries[-1][1]
    w.storage.load_world(TMP / "worlds" / name)

    for chunk in w.chunks.values():
        w.storage.save_chunk(chunk)


@load_world_name.on_execute
def execute_load_world(chat, entries):
    from mcpython.world.World import World

    w = World.INSTANCE
    name = entries[-1][1]
    w.storage.load_world(TMP / "worlds" / name)

    for chunk in w.storage.saved_chunks:
        chunk = w.get_or_create_chunk_by_coord(chunk)
        w.storage.load_chunk(chunk)
