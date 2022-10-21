import typing

from mcpython.world.block.Block import Block


class StairsBlock(Block):
    def get_all_valid_block_states(self) -> typing.List[dict | str]:
        return [
            "facing=east,half=bottom,shape=inner_left",
            "facing=east,half=bottom,shape=inner_right",
            "facing=east,half=bottom,shape=outer_left",
            "facing=east,half=bottom,shape=outer_right",
            "facing=east,half=bottom,shape=straight",
            "facing=east,half=top,shape=inner_left",
            "facing=east,half=top,shape=inner_right",
            "facing=east,half=top,shape=outer_left",
            "facing=east,half=top,shape=outer_right",
            "facing=east,half=top,shape=straight",
            "facing=north,half=bottom,shape=inner_left",
            "facing=north,half=bottom,shape=inner_right",
            "facing=north,half=bottom,shape=outer_left",
            "facing=north,half=bottom,shape=outer_right",
            "facing=north,half=bottom,shape=straight",
            "facing=north,half=top,shape=inner_left",
            "facing=north,half=top,shape=inner_right",
            "facing=north,half=top,shape=outer_left",
            "facing=north,half=top,shape=outer_right",
            "facing=north,half=top,shape=straight",
            "facing=south,half=bottom,shape=inner_left",
            "facing=south,half=bottom,shape=inner_right",
            "facing=south,half=bottom,shape=outer_left",
            "facing=south,half=bottom,shape=outer_right",
            "facing=south,half=bottom,shape=straight",
            "facing=south,half=top,shape=inner_left",
            "facing=south,half=top,shape=inner_right",
            "facing=south,half=top,shape=outer_left",
            "facing=south,half=top,shape=outer_right",
            "facing=south,half=top,shape=straight",
            "facing=west,half=bottom,shape=inner_left",
            "facing=west,half=bottom,shape=inner_right",
            "facing=west,half=bottom,shape=outer_left",
            "facing=west,half=bottom,shape=outer_right",
            "facing=west,half=bottom,shape=straight",
            "facing=west,half=top,shape=inner_left",
            "facing=west,half=top,shape=inner_right",
            "facing=west,half=top,shape=outer_left",
            "facing=west,half=top,shape=outer_right",
            "facing=west,half=top,shape=straight",
        ]
