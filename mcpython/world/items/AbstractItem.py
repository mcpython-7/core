from __future__ import annotations

import typing
from abc import ABC

from mcpython.rendering.Models import Model
from mcpython.resources.Registry import IRegisterAble, Registry
from mcpython.world.blocks import AbstractBlock

if typing.TYPE_CHECKING:
    from mcpython.containers.AbstractContainer import Slot
    from mcpython.containers.ItemStack import ItemStack


ITEMS: list[type[AbstractItem]] = []


class AbstractItem(IRegisterAble, ABC):
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


ITEM_REGISTRY = Registry("minecraft:item", AbstractItem)


def create_item_for_block(
    block: type[AbstractBlock.AbstractBlock],
) -> type[AbstractItem]:
    @ITEM_REGISTRY.register
    class BlockItem(AbstractItem):
        NAME = block.NAME
        MODEL = Model.by_name("{}:item/{}".format(*NAME.split(":")))

        @classmethod
        def create_block_to_be_placed(
            cls, stack: ItemStack
        ) -> AbstractBlock.AbstractBlock | None:
            return block((0, 0, 0))

    return typing.cast(type[AbstractItem], BlockItem)


def create_basic_item(name: str) -> type[AbstractItem]:
    @ITEM_REGISTRY.register
    class BasicItem(AbstractItem):
        NAME = name
        MODEL = Model.by_name("{}:item/{}".format(*NAME.split(":")))

    return typing.cast(type[AbstractItem], BasicItem)


Dirt = create_item_for_block(AbstractBlock.Dirt)
Sand = create_item_for_block(AbstractBlock.Sand)
Bricks = create_item_for_block(AbstractBlock.Bricks)
Stone = create_item_for_block(AbstractBlock.Stone)
OakPlanks = create_item_for_block(AbstractBlock.OakPlanks)
OakLog = create_item_for_block(AbstractBlock.OakLog)
Bedrock = create_item_for_block(AbstractBlock.Bedrock)
Stick = create_basic_item("minecraft:stick")
