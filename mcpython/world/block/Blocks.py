from mcpython.world.block.Block import Block
from mcpython.world.block.BlockManagement import BLOCK_REGISTRY
from mcpython.world.block.SingleBlockStateBlock import SingleBlockStateBlock
from mcpython.world.block.SlabBlock import SlabBlock

# fmt: off
STONE = BLOCK_REGISTRY.register_lazy("minecraft:stone", lambda: Block().register_block_item())
DIRT = BLOCK_REGISTRY.register_lazy("minecraft:dirt", lambda: Block().register_block_item())
COARSE_DIRT = BLOCK_REGISTRY.register_lazy("minecraft:coarse_dirt", lambda: Block().register_block_item())
COBBLESTONE = BLOCK_REGISTRY.register_lazy("minecraft:cobblestone", lambda: Block().register_block_item())
DIAMOND_BLOCK = BLOCK_REGISTRY.register_lazy("minecraft:diamond_block", lambda: Block().register_block_item())
ANCIENT_DEBRIS = BLOCK_REGISTRY.register_lazy("minecraft:ancient_debris", lambda: Block().register_block_item())
ACACIA_SAPLING = BLOCK_REGISTRY.register_lazy("minecraft:acacia_sapling", lambda: Block().register_block_item())
ACACIA_LEAVES = BLOCK_REGISTRY.register_lazy("minecraft:acacia_leaves", lambda: Block().register_block_item())
BEACON = BLOCK_REGISTRY.register_lazy("minecraft:beacon", lambda: Block().register_block_item())
GRASS_BLOCK = BLOCK_REGISTRY.register_lazy("minecraft:grass_block", lambda: SingleBlockStateBlock({"snowy": "false"}).register_block_item())
OAK_SLAB = BLOCK_REGISTRY.register_lazy("minecraft:oak_slab", lambda: SlabBlock().register_block_item())
# fmt: on
