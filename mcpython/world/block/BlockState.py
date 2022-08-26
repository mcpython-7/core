import typing
from mcpython.world.block.Block import Block


class BlockState:
    def __init__(self, block_type: Block = None):
        self.block_type = block_type

        self.chunk_section = None
        self.position: typing.Tuple[int, int, int] = None

    async def on_addition(self):
        pass

    async def on_remove(self, force=False, player=None) -> bool:
        pass
