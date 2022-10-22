import typing

from mcpython.world.block.Block import Block


class LogBlock(Block):
    def get_all_valid_block_states(self) -> typing.List[str]:
        return ["axis=x", "axis=y", "axis=z"]

