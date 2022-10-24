import itertools
import typing

from mcpython.world.block.Block import Block


class FenceGate(Block):
    def get_all_valid_block_states(self) -> typing.List[str]:
        states = [f"facing={a},in_wall={str(bool(b)).lower()},open={str(bool(c)).lower()}" for a, b, c in itertools.product(
            ["north", "east", "south", "west"],
            range(2),
            range(2),
        )]

        return states
