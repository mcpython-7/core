from mcpython.world.blocks.AbstractBlock import (
    AbstractBlock,
    LogLikeBlock,
    FenceLikeBlock,
    BLOCK_REGISTRY,
    SlabLikeBlock,
    StairsLikeBlock,
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

    @BLOCK_REGISTRY.register
    class Stairs(StairsLikeBlock):
        NAME = f"{namespace}:{wood_name}_stairs"

    create_item_for_block(Planks)
    create_item_for_block(Log)
    create_item_for_block(Wood)
    create_item_for_block(Fence)
    create_item_for_block(Slab)
    create_item_for_block(Stairs)


def add_simple_block(name: str):
    @BLOCK_REGISTRY.register
    class SimpleBlock(AbstractBlock):
        NAME = name if ":" in name else f"minecraft:{name}"

    create_item_for_block(SimpleBlock)


def add_simple_block_set(name: str, base_name: str = None):
    base_name = base_name or name

    @BLOCK_REGISTRY.register
    class Block(AbstractBlock):
        NAME = name if ":" in name else f"minecraft:{name}"

    @BLOCK_REGISTRY.register
    class Slab(SlabLikeBlock):
        NAME = (
            f"{base_name}_slab" if ":" in base_name else f"minecraft:{base_name}_slab"
        )

    @BLOCK_REGISTRY.register
    class Stairs(StairsLikeBlock):
        NAME = (
            f"{base_name}_stairs"
            if ":" in base_name
            else f"minecraft:{base_name}_stairs"
        )

    create_item_for_block(Block)
    create_item_for_block(Slab)
    create_item_for_block(Stairs)


add_wooden_set("acacia")
add_wooden_set("birch")
add_wooden_set("dark_oak")
add_wooden_set("jungle")
add_wooden_set("oak")
add_wooden_set("spruce")
add_wooden_set("mangrove")
add_wooden_set("cherry")

add_simple_block_set("bricks", "brick")

add_simple_block("dirt")
add_simple_block("coarse_dirt")

add_simple_block_set("stone")
add_simple_block_set("stone_bricks", "stone_brick")
add_simple_block_set("diorite")
add_simple_block_set("andesite")
add_simple_block_set("granite")

add_simple_block("minecraft:iron_block")
add_simple_block("minecraft:iron_ore")
add_simple_block("minecraft:deepslate_iron_ore")
add_simple_block("minecraft:gold_block")
add_simple_block("minecraft:gold_ore")
add_simple_block("minecraft:deepslate_gold_ore")
add_simple_block("minecraft:diamond_block")
add_simple_block("minecraft:diamond_ore")
add_simple_block("minecraft:deepslate_diamond_ore")
add_simple_block("minecraft:redstone_block")
# todo: redstone ore (more complex logic)
add_simple_block("minecraft:lapis_block")
add_simple_block("minecraft:lapis_ore")
add_simple_block("minecraft:deepslate_lapis_ore")
add_simple_block("minecraft:copper_ore")
add_simple_block("minecraft:deepslate_copper_ore")
add_simple_block("minecraft:coal_block")
add_simple_block("minecraft:coal_ore")
add_simple_block("minecraft:deepslate_coal_ore")
