from __future__ import annotations

from mcpython.world.blocks.AbstractBlock import BLOCK_REGISTRY, AbstractBlock


@BLOCK_REGISTRY.register
class GrassBlock(AbstractBlock):
    NAME = "minecraft:grass_block"

    def get_block_state(self) -> dict[str, str]:
        return {"snowy": "false"}

    def get_tint_colors(self) -> list[tuple[float, float, float, float]] | None:
        return [(145 / 255, 189 / 255, 89 / 255, 1)]
