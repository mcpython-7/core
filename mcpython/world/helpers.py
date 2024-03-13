from mcpython.world.blocks.AbstractBlock import (
    AbstractBlock,
    LogLikeBlock,
    BLOCK_REGISTRY,
)
from mcpython.world.items.AbstractItem import (
    AbstractItem,
    create_basic_item,
    create_item_for_block,
    ITEM_REGISTRY,
)


def add_wooden_set(wood_name: str, namespace="minecraft"):
    @BLOCK_REGISTRY.register
    class Planks(AbstractBlock):
        NAME = f"{namespace}:{wood_name}_planks"

    @BLOCK_REGISTRY.register
    class Log(LogLikeBlock):
        NAME = f"{namespace}:{wood_name}_log"

    @BLOCK_REGISTRY.register
    class Wood(LogLikeBlock):
        NAME = f"{namespace}:{wood_name}_wood"

    create_item_for_block(Planks)
    create_item_for_block(Log)
    create_item_for_block(Wood)


add_wooden_set("acacia")
add_wooden_set("birch")
add_wooden_set("dark_oak")
add_wooden_set("jungle")
add_wooden_set("oak")
add_wooden_set("spruce")
add_wooden_set("mangrove")
add_wooden_set("cherry")
