from mcpython.commands.Command import Command, ItemName, IntegerLiteral
from mcpython.containers.ItemStack import ItemStack
from mcpython.world.items.AbstractItem import AbstractItem

count = IntegerLiteral(min=1)
item_name = ItemName().then(count)
give_command = Command("give")
give_command.construct().then(item_name)


@item_name.on_execute
def run_give(chat, entries):
    from mcpython.rendering.Window import Window

    Window.INSTANCE.player.inventory.insert(ItemStack(entries[1][1]))
    chat.submit_text(f"Given <PLAYER> 1x {entries[1][1].NAME}")


@count.on_execute
def run_give_with_count(chat, entries):
    item: type[AbstractItem] = entries[1][1]
    count = min(entries[2][1], item.MAX_STACK_SIZE)
    from mcpython.rendering.Window import Window

    Window.INSTANCE.player.inventory.insert(ItemStack(item, count))
    chat.submit_text(f"Given <PLAYER> {count}x {entries[1][1].NAME}")
