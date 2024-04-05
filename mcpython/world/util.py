from __future__ import annotations

import enum

from pyglet.math import Vec3

SECTOR_SIZE = 16


class Facing(enum.Enum):
    UP = ((0, 1, 0),)
    DOWN = ((0, -1, 0),)
    NORTH = ((0, 0, -1),)
    SOUTH = ((0, 0, 1),)
    EAST = ((-1, 0, 0),)
    WEST = ((1, 0, 0),)

    def __init__(self, offset: tuple[int, int, int]):
        super().__init__()
        self.offset = offset
        self.opposite: Facing = None

    def __eq__(self, other):
        return isinstance(other, Facing) and self.offset == other.offset

    def __hash__(self):
        return hash(self.offset)

    def position_offset(self, position: tuple[int, int, int]) -> tuple[int, int, int]:
        return (
            self.offset[0] + position[0],
            self.offset[1] + position[1],
            self.offset[2] + position[2],
        )


Facing.UP.opposite = Facing.DOWN
Facing.DOWN.opposite = Facing.UP
Facing.NORTH.opposite = Facing.SOUTH
Facing.SOUTH.opposite = Facing.NORTH
Facing.WEST.opposite = Facing.EAST
Facing.EAST.opposite = Facing.WEST


def normalize(position: tuple[float, float, float] | Vec3) -> tuple[int, int, int]:
    """Accepts `position` of arbitrary precision and returns the block
    containing that position.

    Parameters
    ----------
    position : tuple of len 3

    Returns
    -------
    block_position : tuple of ints of len 3

    """
    x, y, z = position
    x, y, z = (int(round(x)), int(round(y)), int(round(z)))
    return x, y, z


def sectorize(position: tuple[float, float, float] | Vec3) -> tuple[int, int]:
    """Returns a tuple representing the sector for the given `position`.

    Parameters
    ----------
    position : tuple of len 3

    Returns
    -------
    sector : tuple of len 3

    """
    x, y, z = normalize(position)
    x, y, z = x // SECTOR_SIZE, y // SECTOR_SIZE, z // SECTOR_SIZE
    return x, z
