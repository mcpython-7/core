from __future__ import annotations

import typing

from mcpython.rendering.Models import Model
from mcpython.world.blocks import AbstractBlock

if typing.TYPE_CHECKING:
    from mcpython.containers.AbstractContainer import Slot


class AbstractItem:
    NAME: str | None = None
    MODEL: Model | None = None
    MAX_STACK_SIZE = 64

    def __init__(self):
        raise RuntimeError("Items are static!")

    @classmethod
    def on_slot_insert(cls, slot: Slot):
        pass


def create_item_for_block(
    block: type[AbstractBlock.AbstractBlock],
) -> type[AbstractItem]:
    class BlockItem(AbstractItem):
        NAME = block.NAME
        MODEL = Model.by_name("{}:item/{}".format(*NAME.split(":")))

    return BlockItem


Dirt = create_item_for_block(AbstractBlock.Dirt)
Sand = create_item_for_block(AbstractBlock.Sand)
Bricks = create_item_for_block(AbstractBlock.Bricks)
Stone = create_item_for_block(AbstractBlock.Stone)
Bedrock = create_item_for_block(AbstractBlock.Bedrock)
