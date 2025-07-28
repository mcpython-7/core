from __future__ import annotations

from mcpython.world.blocks.AbstractBlock import BLOCK_REGISTRY, AbstractBlock


@BLOCK_REGISTRY.register
class Bedrock(AbstractBlock):
    NAME = "minecraft:bedrock"
    BREAKABLE = False
