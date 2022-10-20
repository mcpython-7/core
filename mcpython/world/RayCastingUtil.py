import typing

from pyglet.math import Vec3

from mcpython.util.math import normalize
from mcpython.world.AbstractDefinition import AbstractDimension
from mcpython.world.AbstractDefinition import ChunkDoesNotExistException
from mcpython.world.block.BlockState import BlockState


async def cast_into_world(dimension: AbstractDimension, position: typing.Tuple[float, float, float], direction: typing.Tuple[float, float, float], source=None) -> typing.Tuple[BlockState, typing.Tuple[float, float, float]] | None:
    position = Vec3(*position)

    step = Vec3(*direction).normalize() * .3

    previous_other = normalize(*position), normalize(*position)

    chunk = await (await dimension.get_chunk_for_position(0, 0, 0)).get_section(0)

    # print(position, direction)

    for _ in range(200):
        position += step

        norm = normalize(*position)

        # print(position, norm)

        try:
            block = await dimension.get_block(norm)
        except ChunkDoesNotExistException:
            continue

        if block is None:
            continue

        if await block.check_collision(tuple(position), source):
            return block, previous_other[0]

        if norm != previous_other[1]:
            previous_other = previous_other[1], norm

