from __future__ import annotations

from mcpython.rendering.Models import BlockStateFile
from mcpython.world.blocks.AbstractBlock import BLOCK_REGISTRY, AbstractBlock


@BLOCK_REGISTRY.register
class Sand(AbstractBlock):
    NAME = "minecraft:sand"
    STATE_FILE = BlockStateFile.by_name(NAME)

    def __init__(self, position):
        super().__init__(position)
        self.falling = False
        self.ticks_to_fall = 3

    def on_block_updated(self):
        if self.falling:
            return

        from mcpython.world.World import World

        block = self.chunk.blocks.get(
            (
                self.position[0],
                self.position[1] - 1,
                self.position[2],
            )
        )

        if not block or (isinstance(block, Sand) and block.falling):
            self.set_ticking(True)
            self.ticks_to_fall = 3
            self.falling = True
            if block:
                block.on_block_updated()

    def on_tick(self):
        if not self.falling:
            self.set_ticking(False)
            return

        self.ticks_to_fall -= 1
        if self.ticks_to_fall <= 0:
            self.fall()

    def fall(self):
        self.falling = False

        if (
            self.chunk.blocks.get(self.position, None) is self
            and (
                self.position[0],
                self.position[1] - 1,
                self.position[2],
            )
            not in self.chunk.blocks
        ):
            self.chunk.world.INSTANCE.remove_block(self.position, block_update=False)
            old_pos = self.position
            if self.position[1] > -20:
                self.chunk.add_block(
                    (self.position[0], self.position[1] - 1, self.position[2]), self
                )
            else:
                self.set_ticking(False)
            self.chunk.world.send_block_update(old_pos)
        else:
            self.set_ticking(False)
