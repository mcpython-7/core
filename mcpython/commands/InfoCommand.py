from mcpython.commands.Command import Command, FixedString
from mcpython.containers.ItemStack import ItemStack
from mcpython.world.items.AbstractItem import AbstractItem

tags = FixedString("tags")
block = FixedString("block")
info_command = Command("info")
info_command.construct().then(tags).then(block)


@tags.on_execute
def execute_info_tags(chat, results):
    from mcpython.rendering.Window import Window

    itemstack = Window.INSTANCE.player.inventory.get_selected_itemstack()
    if itemstack.is_empty():
        chat.submit_text("Itemstack is empty")
    else:
        chat.submit_text(f"Itemstack: {itemstack.count}x {itemstack.item.NAME}, tags:")
        for tag in itemstack.item.TAGS:
            chat.submit_text(tag)


@block.on_execute
def execute_block_info(chat, results):
    from mcpython.rendering.Window import Window

    vector = Window.INSTANCE.get_sight_vector()
    pos, *_ = Window.INSTANCE.world.hit_test(Window.INSTANCE.player.position, vector)
    instance = Window.INSTANCE.world.get_or_create_chunk_by_position(pos).blocks.get(
        pos
    )

    if instance is None:
        chat.submit_text("<NO BLOCK>")
    else:
        chat.submit_text(f"Block: '{instance.NAME}'")
        chat.submit_text(f"State: {instance.get_block_state()}")
        chat.submit_text(f"Tags: {', '.join(instance.TAGS)}")
