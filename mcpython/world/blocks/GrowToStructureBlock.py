from __future__ import annotations

from mcpython.world.blocks.AbstractBlock import AbstractBlock
from mcpython.world.serialization.DataBuffer import WriteBuffer, ReadBuffer
from mcpython.world.worldgen.WorldgenManager import Structure


class GrowToStructureBlock(AbstractBlock):
    STRUCTURE: Structure = None
    GROWTH_STAGES = 3

    def __init__(self, position: tuple[int, int, int]):
        super().__init__(position)
        self.pending_growth = self.GROWTH_STAGES

    def on_random_update(self):
        if self.pending_growth == 0:
            return

        self.pending_growth -= 1
        if self.pending_growth == 0:
            self.grow()

    def inner_encode(self, buffer: WriteBuffer):
        super().inner_encode(buffer)
        buffer.write_uint8(self.pending_growth)

    @classmethod
    def inner_decode(cls, obj: GrowToStructureBlock, buffer: ReadBuffer):
        super().inner_decode(obj, buffer)
        obj.pending_growth = buffer.read_uint8()

    def grow(self):
        if self.STRUCTURE:
            self.STRUCTURE.place(self.chunk.world, self.position)
