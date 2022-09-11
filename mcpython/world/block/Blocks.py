from mcpython.world.block.Block import Block
from mcpython.world.block.BlockManagement import BLOCK_REGISTRY


STONE = BLOCK_REGISTRY.register_lazy("minecraft:stone", lambda: Block())
DIRT = BLOCK_REGISTRY.register_lazy("minecraft:dirt", lambda: Block())
