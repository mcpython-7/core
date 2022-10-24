import functools
import itertools
import typing

from mcpython.world.block.Block import Block


class WallBlock(Block):
    def get_all_valid_block_states(self) -> typing.List[dict]:
        states = []
        statem = "false", "low", "tall"
        for a, b, c, d, state, e in itertools.product(range(2), repeat=6):
            state += 1

            states.append(
                {
                    "north": statem[a * state],
                    "east": statem[b * state],
                    "south": statem[c * state],
                    "west": statem[d * state],
                    "up": str(bool(e)).lower(),
                }
            )

        return states
