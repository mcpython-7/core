from __future__ import annotations

import typing

from mcpython.rendering.Models import Model
from mcpython.world.blocks import AbstractBlock

if typing.TYPE_CHECKING:
    from mcpython.containers.AbstractContainer import Slot
    from mcpython.containers.ItemStack import ItemStack


ITEMS: list[type[AbstractItem]] = []


class AbstractItem:
    NAME: str | None = None
    MODEL: Model | None = None
    MAX_STACK_SIZE = 64

    @classmethod
    def __init_subclass__(cls, **kwargs):
        if cls.NAME is not None:
            ITEMS.append(cls)

    def __init__(self):
        raise RuntimeError("Items are static!")

    @classmethod
    def create_block_to_be_placed(
        cls, stack: ItemStack
    ) -> AbstractBlock.AbstractBlock | None:
        pass

    @classmethod
    def on_slot_insert(cls, slot: Slot):
        pass

    @classmethod
    def on_block_interaction(
        cls,
        itemstack: ItemStack,
        block: AbstractBlock.AbstractBlock | None,
        button: int,
        modifiers: int,
    ) -> bool:
        """
        Called when the item is used to interact with a block (None if no block is targeted).
        'button' and 'modifiers' are the mouse buttons pressed.
        Should return 'True' if the normal logic should NOT continue.
        """
        return False


def create_item_for_block(
    block: type[AbstractBlock.AbstractBlock],
) -> type[AbstractItem]:
    class BlockItem(AbstractItem):
        NAME = block.NAME
        MODEL = Model.by_name("{}:item/{}".format(*NAME.split(":")))

        @classmethod
        def create_block_to_be_placed(
            cls, stack: ItemStack
        ) -> AbstractBlock.AbstractBlock | None:
            return block((0, 0, 0))

    block.BLOCK_ITEM = BlockItem
    return BlockItem


Dirt = create_item_for_block(AbstractBlock.Dirt)
Sand = create_item_for_block(AbstractBlock.Sand)
Bricks = create_item_for_block(AbstractBlock.Bricks)
Stone = create_item_for_block(AbstractBlock.Stone)
OakPlanks = create_item_for_block(AbstractBlock.OakPlanks)
OakLog = create_item_for_block(AbstractBlock.OakLog)
Bedrock = create_item_for_block(AbstractBlock.Bedrock)
