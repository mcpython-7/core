from mcpython.commands.Command import Command, ItemName
from mcpython.containers.ItemStack import ItemStack

item_name = ItemName()
give_command = Command("give").construct().then(item_name)


@item_name.on_execute
def run_give(chat, entries):
    from mcpython.rendering.Window import Window

    Window.INSTANCE.player_inventory.insert(ItemStack(entries[1][1]))
    chat.submit_text(f"Given <PLAYER> 1x {entries[1][1].NAME}")
