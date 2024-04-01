from mcpython.world.blocks.AbstractBlock import (
    AbstractBlock,
    LogLikeBlock,
    FenceLikeBlock,
    BLOCK_REGISTRY,
    SlabLikeBlock,
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

    @BLOCK_REGISTRY.register
    class Fence(FenceLikeBlock):
        NAME = f"{namespace}:{wood_name}_fence"

    @BLOCK_REGISTRY.register
    class Slab(SlabLikeBlock):
        NAME = f"{namespace}:{wood_name}_slab"

    create_item_for_block(Planks)
    create_item_for_block(Log)
    create_item_for_block(Wood)
    create_item_for_block(Fence)
    create_item_for_block(Slab)


def add_simple_block(name: str):
    @BLOCK_REGISTRY.register
    class SimpleBlock(AbstractBlock):
        NAME = name if ":" in name else f"minecraft:{name}"

    create_item_for_block(SimpleBlock)


add_wooden_set("acacia")
add_wooden_set("birch")
add_wooden_set("dark_oak")
add_wooden_set("jungle")
add_wooden_set("oak")
add_wooden_set("spruce")
add_wooden_set("mangrove")
add_wooden_set("cherry")

add_simple_block("bricks")

add_simple_block("dirt")
add_simple_block("coarse_dirt")

add_simple_block("stone")
add_simple_block("diorite")
add_simple_block("andesite")
add_simple_block("granite")
