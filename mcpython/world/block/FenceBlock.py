import functools
import itertools
import typing

from mcpython.world.block.Block import Block


class FenceBlock(Block):
    def get_all_valid_block_states(self) -> typing.List[dict]:
        states = []
        for a, b, c, d in itertools.product(range(2), repeat=4):
            states.append(
                {
                    "north": str(bool(a)).lower(),
                    "east": str(bool(b)).lower(),
                    "south": str(bool(c)).lower(),
                    "west": str(bool(d)).lower(),
                }
            )

        return states
