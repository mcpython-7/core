import typing

from mcpython.world.block.Block import Block


class FenceBlock(Block):
    def get_all_valid_block_states(self) -> typing.List[dict]:
        return [{"north": "true", "south": "true"}]
