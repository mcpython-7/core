from mcpython.commands.Command import Command, ItemName, IntegerLiteral
from mcpython.containers.ItemStack import ItemStack
from mcpython.world.items.AbstractItem import AbstractItem

count = IntegerLiteral(min=1)
item_name = ItemName().then(count)
give_command = Command("give")
give_command.construct().then(item_name)


@item_name.on_execute
def run_give(player, entries):
    player.inventory.insert(ItemStack(entries[1][1]))
    player.chat.submit_text(f"Given <PLAYER> 1x {entries[1][1].NAME}")


@count.on_execute
def run_give_with_count(player, entries):
    item: type[AbstractItem] = entries[1][1]
    count = min(entries[2][1], item.MAX_STACK_SIZE)
    player.inventory.insert(ItemStack(item, count))
    player.chat.submit_text(f"Given <PLAYER> {count}x {entries[1][1].NAME}")
