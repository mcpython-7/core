from __future__ import annotations

import typing
from abc import ABC

from mcpython.rendering.Models import Model
from mcpython.resources.Registry import IRegisterAble, Registry
from mcpython.world.blocks import AbstractBlock
from mcpython.world.serialization.DataBuffer import (
    AbstractDataFixer,
    ReadBuffer,
    WriteBuffer,
)
from mcpython.world.util import normalize

if typing.TYPE_CHECKING:
    from mcpython.containers.AbstractContainer import Slot
    from mcpython.containers.ItemStack import ItemStack


ITEMS: list[type[AbstractItem]] = []


class AbstractItem(IRegisterAble, ABC):
    NAME: str | None = None
    MODEL: Model | None = None
    MAX_STACK_SIZE = 64
    TRANSPARENT = False

    VERSION = 0
    DATA_FIXERS: dict[int, AbstractDataFixer] = {}

    @classmethod
    def decode_metadata(cls, stack: ItemStack, buffer: ReadBuffer):
        pass

    @classmethod
    def encode_metadata(cls, stack: ItemStack, buffer: WriteBuffer):
        pass

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
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

    @classmethod
    def get_custom_hover_info(cls, itemstack: ItemStack) -> list[str]:
        """
        Returns a list of strings to be added to the hover text
        First Element is the topmost element.
        Width is dynamic based on context size.
        """
        return []

    @classmethod
    def get_tint_colors(
        cls, itemstack: ItemStack, slot: Slot
    ) -> list[tuple[float, float, float, float]] | None:
        pass


ITEM_REGISTRY = Registry("minecraft:item", AbstractItem)


def create_item_for_block(
    block: type[AbstractBlock.AbstractBlock],
) -> type[AbstractItem]:
    probe_block = block((0, 0, 0))

    @ITEM_REGISTRY.register
    class BlockItem(AbstractItem):
        NAME = block.NAME
        MODEL = Model.by_name("{}:item/{}".format(*NAME.split(":")))
        TRANSPARENT = block.TRANSPARENT

        @classmethod
        def create_block_to_be_placed(
            cls, stack: ItemStack
        ) -> AbstractBlock.AbstractBlock | None:
            return block((0, 0, 0))

        @classmethod
        def get_tint_colors(
            cls, itemstack: ItemStack, slot: Slot
        ) -> list[tuple[float, float, float, float]] | None:
            from mcpython.rendering.Window import Window

            probe_block.position = pos = normalize(Window.INSTANCE.player.position)
            probe_block.chunk = Window.INSTANCE.world.get_or_create_chunk_by_position(
                pos
            )
            return probe_block.get_tint_colors()

    return typing.cast(type[AbstractItem], BlockItem)


def create_basic_item(name: str) -> type[AbstractItem]:
    @ITEM_REGISTRY.register
    class BasicItem(AbstractItem):
        NAME = name
        MODEL = Model.by_name("{}:item/{}".format(*NAME.split(":")))

    return typing.cast(type[AbstractItem], BasicItem)


Bedrock = create_item_for_block(AbstractBlock.Bedrock)
CraftingTable = create_item_for_block(AbstractBlock.CraftingTable)
Sand = create_item_for_block(AbstractBlock.Sand)
Stick = create_basic_item("minecraft:stick")
IronIngot = create_basic_item("minecraft:iron_ingot")
RawIron = create_basic_item("minecraft:raw_iron")
IronNugget = create_basic_item("minecraft:iron_nugget")
CopperIngot = create_basic_item("minecraft:copper_ingot")
RawIngot = create_basic_item("minecraft:raw_copper")
GoldIngot = create_basic_item("minecraft:gold_ingot")
RawGold = create_basic_item("minecraft:raw_gold")
GoldNugget = create_basic_item("minecraft:gold_nugget")
Diamond = create_basic_item("minecraft:diamond")
Redstone = create_basic_item("minecraft:redstone")  # for now, this is item-only
LapisLazuli = create_basic_item("minecraft:lapis_lazuli")
Coal = create_basic_item("minecraft:coal")
GrassBlock = create_item_for_block(AbstractBlock.GrassBlock)
ShortGrass = create_item_for_block(AbstractBlock.ShortGrass)
