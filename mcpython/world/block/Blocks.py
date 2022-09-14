from mcpython.world.block.Block import Block
from mcpython.world.block.BlockManagement import BLOCK_REGISTRY


STONE = BLOCK_REGISTRY.register_lazy(
    "minecraft:stone", lambda: Block().register_block_item()
)
DIRT = BLOCK_REGISTRY.register_lazy(
    "minecraft:dirt", lambda: Block().register_block_item()
)
COARSE_DIRT = BLOCK_REGISTRY.register_lazy(
    "minecraft:coarse_dirt", lambda: Block().register_block_item()
)
COBBLESTONE = BLOCK_REGISTRY.register_lazy(
    "minecraft:cobblestone", lambda: Block().register_block_item()
)
DIAMOND_BLOCK = BLOCK_REGISTRY.register_lazy(
    "minecraft:diamond_block", lambda: Block().register_block_item()
)
ANCIENT_DEBRIS = BLOCK_REGISTRY.register_lazy(
    "minecraft:ancient_debris", lambda: Block().register_block_item()
)
