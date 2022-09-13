import typing

from mcpython.backend.Registry import IRegistryEntry
from mcpython.world.block.Block import Block
from mcpython.world.block.BlockState import BlockState


class Item(IRegistryEntry):
    REGISTRY = "minecraft:item"

    def __init__(self):
        self.maximum_stack_size = 64

    def set_maximum_stack_size(self, stack_size: int):
        self.maximum_stack_size = stack_size
        return self

    def get_maximum_stack_size(self):
        return self.maximum_stack_size

    def get_block_to_set(
        self,
        itemstack,
        section,
        position: typing.Tuple[int, int, int],
        player,
        hand,
        button: int,
        modifiers: int,
    ) -> typing.Optional[Block | BlockState]:
        pass

    def on_started_to_break_block_with(
        self,
        itemstack,
        blockstate: BlockState,
        player,
        hand,
        button: int,
        modifiers: int,
    ) -> bool | float:
        """
        Invoked before the player starts to break a block with this item.
        Allows to modify the behaviour.

        :param itemstack: the itemstack used
        :param blockstate: the block to break
        :param player: the player breaking
        :param hand: the hand the player is using
        :param button: the button used (most likely left)
        :param modifiers: the modifiers used
        :return: False to cancel breaking, True for normal breaking, or a float (second) for break-time
        """
        return True

    def on_block_broken_with(
        self,
        itemstack,
        blockstate: BlockState,
        player,
        hand,
        button: int,
        modifiers: int,
    ) -> bool:
        return True

    async def on_player_interaction(
        self, itemstack, blockstate: typing.Optional[BlockState], player, hand, button, modifiers
    ) -> bool:
        return False

    def on_item_count_changed(self, itemstack, previous: int, new: int):
        pass

    def on_itemstack_copied(self, source_stack, target_stack):
        pass
