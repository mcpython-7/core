from mcpython.containers.ItemStack import ItemStack
from mcpython.world.blocks.AbstractBlock import (
    AbstractBlock,
    BLOCK_REGISTRY,
)
from mcpython.world.blocks.FenceGateLikeBlock import FenceGateLikeBlock
from mcpython.world.blocks.GrowToStructureBlock import GrowToStructureBlock
from mcpython.world.blocks.StairsLikeBlock import StairsLikeBlock
from mcpython.world.blocks.SlabLikeBlock import SlabLikeBlock
from mcpython.world.blocks.FenceLikeBlock import FenceLikeBlock
from mcpython.world.blocks.LogLikeBlock import LogLikeBlock
from mcpython.world.items.AbstractItem import (
    AbstractItem,
    create_basic_item,
    create_item_for_block,
    ITEM_REGISTRY,
)
from mcpython.world.util import Facing


def add_wooden_set(
    wood_name: str, namespace="minecraft", log=True, sapling=True, leaves=False
):

    @BLOCK_REGISTRY.register
    class Planks(AbstractBlock):
        NAME = f"{namespace}:{wood_name}_planks"

    Log = StrippedLog = Wood = StrippedWood = None
    if log:

        @BLOCK_REGISTRY.register
        class Log(LogLikeBlock):
            NAME = f"{namespace}:{wood_name}_log"

            # todo: add stripping mechanic

        @BLOCK_REGISTRY.register
        class StrippedLog(LogLikeBlock):
            NAME = f"{namespace}:stripped_{wood_name}_log"

        @BLOCK_REGISTRY.register
        class Wood(LogLikeBlock):
            NAME = f"{namespace}:{wood_name}_wood"

            # todo: add stripping mechanic

        @BLOCK_REGISTRY.register
        class StrippedWood(LogLikeBlock):
            NAME = f"{namespace}:stripped_{wood_name}_wood"

    @BLOCK_REGISTRY.register
    class Fence(FenceLikeBlock):
        NAME = f"{namespace}:{wood_name}_fence"

    @BLOCK_REGISTRY.register
    class FenceGate(FenceGateLikeBlock):
        NAME = f"{namespace}:{wood_name}_fence_gate"

    @BLOCK_REGISTRY.register
    class Slab(SlabLikeBlock):
        NAME = f"{namespace}:{wood_name}_slab"

    @BLOCK_REGISTRY.register
    class Stairs(StairsLikeBlock):
        NAME = f"{namespace}:{wood_name}_stairs"

    Leaves = None
    if leaves:

        @BLOCK_REGISTRY.register
        class Leaves(AbstractBlock):
            NAME = f"{namespace}:{wood_name}_leaves"
            TRANSPARENT = True

            def is_solid(self, face: Facing) -> bool:
                return False

            def get_tint_colors(self) -> list[tuple[float, float, float, float]] | None:
                return [(145 / 255, 189 / 255, 89 / 255, 1)]

    Sapling = None
    if sapling:

        @BLOCK_REGISTRY.register
        class Sapling(GrowToStructureBlock):
            NAME = f"{namespace}:{wood_name}_sapling"
            # todo: make tag
            GROWTH_SUPPORT = [
                "minecraft:dirt",
                "minecraft:coarse_dirt",
                "minecraft:grass_block",
            ]
            TRANSPARENT = True
            NO_COLLISION = True

            def on_block_placed(
                self,
                itemstack: ItemStack | None,
                onto: tuple[int, int, int] | None = None,
                hit_position: tuple[float, float, float] | None = None,
            ) -> bool:
                x, y, z = self.position
                block = self.chunk.blocks.get((x, y - 1, z))
                if block is None or block.NAME not in self.GROWTH_SUPPORT:
                    return False

            def on_block_updated(self):
                x, y, z = self.position
                block = self.chunk.blocks.get((x, y - 1, z))
                if block is None or block.NAME not in self.GROWTH_SUPPORT:
                    self.chunk.remove_block(self)
                    # todo: drop item

            def is_solid(self, face: Facing) -> bool:
                return False

    create_item_for_block(Planks)

    if log:
        create_item_for_block(Log)
        create_item_for_block(StrippedLog)
        create_item_for_block(Wood)
        create_item_for_block(StrippedWood)

    create_item_for_block(Fence)
    create_item_for_block(FenceGate)
    create_item_for_block(Slab)
    create_item_for_block(Stairs)

    if leaves:
        create_item_for_block(Leaves)

    if sapling:
        create_item_for_block(Sapling)


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
add_wooden_set("bamboo", log=False, sapling=False, leaves=False)
add_wooden_set("birch")
add_wooden_set("dark_oak")
add_wooden_set("jungle")
add_wooden_set("oak")
add_wooden_set("spruce")
add_wooden_set("mangrove", sapling=False)
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
