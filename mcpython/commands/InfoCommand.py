from mcpython.commands.Command import Command, FixedString
from mcpython.containers.ItemStack import ItemStack
from mcpython.world.items.AbstractItem import AbstractItem

tags = FixedString("tags")
block = FixedString("block")
info_command = Command("info")
info_command.construct().then(tags).then(block)


@tags.on_execute
def execute_info_tags(player, results):
    itemstack = player.inventory.get_selected_itemstack()
    if itemstack.is_empty():
        player.chat.submit_text("Itemstack is empty")
    else:
        player.chat.submit_text(
            f"Itemstack: {itemstack.count}x {itemstack.item.NAME}, tags:"
        )
        for tag in itemstack.item.TAGS:
            player.chat.submit_text(tag)


@block.on_execute
def execute_block_info(player, results):
    vector = player.get_sight_vector()
    pos, *_ = player.hit_test(player.position, vector)
    instance = player.world.get_or_create_chunk_by_position(pos).blocks.get(pos)

    if instance is None:
        player.chat.submit_text("<NO BLOCK>")
    else:
        player.chat.submit_text(f"Block: '{instance.NAME}'")
        player.chat.submit_text(f"State: {instance.get_block_state()}")
        player.chat.submit_text(f"Tags: {', '.join(instance.TAGS)}")
