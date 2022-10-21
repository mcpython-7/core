import typing

from mcpython.world.block.Block import Block


class SlabBlock(Block):
    def get_all_valid_block_states(self) -> typing.List[dict]:
        return [{"type": "bottom"}, {"type": "top"}, {"type": "double"}]

