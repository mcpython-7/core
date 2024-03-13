from mcpython.commands.Command import Command, FixedString
from mcpython.containers.ItemStack import ItemStack
from mcpython.world.items.AbstractItem import AbstractItem

tags = FixedString("tags")
info_command = Command("info")
info_command.construct().then(tags)


@tags.on_execute
def execute_info_tags(chat, results):
    from mcpython.rendering.Window import Window

    itemstack = Window.INSTANCE.player_inventory.get_selected_itemstack()
    if itemstack.is_empty():
        chat.submit_text("Itemstack is empty")
    else:
        chat.submit_text(f"Itemstack: {itemstack.count}x {itemstack.item.NAME}, tags:")
        for tag in itemstack.item.TAGS:
            chat.submit_text(tag)
