import typing

from mcpython.world.block.Block import Block
from mcpython.world.block.BlockState import BlockState
from mcpython.world.item.Item import Item


__all__ = ["BlockItem"]


class BlockItem(Item):
    block_type: Block | BlockState = None

    def set_block_type(self, block_type: Block | BlockState):
        self.block_type = block_type
        return self

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
        return self.block_type

