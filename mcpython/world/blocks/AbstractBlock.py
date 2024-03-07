import abc


def tex_coord(x: int, y: int, n=4) -> tuple[float, ...]:
    """Return the bounding vertices of the texture square."""
    m = 1.0 / n
    dx = x * m
    dy = y * m
    # fmt: off
    return (
        dx, dy, dx + m, dy, dx + m, dy + m,  # Triangle 1
        dx, dy, dx + m, dy + m, dx, dy + m,  # Triangle 2
    )
    # fmt: on


def tex_coords(
    top: tuple[int, int], bottom: tuple[int, int], side: tuple[int, int], n=4
) -> list[float]:
    """Return a list of the texture squares for the top, bottom and side."""
    top = tex_coord(*top, n=n)
    bottom = tex_coord(*bottom, n=n)
    side = tex_coord(*side, n=n)
    result = []
    result.extend(top)
    result.extend(bottom)
    result.extend(side * 4)
    return result


class AbstractBlock(abc.ABC):
    NAME: str | None = None
    TEXTURE_COORDINATES: list[float] | None = None

    def __init__(self, position: tuple[int, int, int]):
        self.position = position

    def __repr__(self):
        return f"{self.__class__.__name__}{self.position}"


class GrassBlock(AbstractBlock):
    NAME = "minecraft:grass_block"
    TEXTURE_COORDINATES = tex_coords((1, 0), (0, 1), (0, 0))


class Sand(AbstractBlock):
    NAME = "minecraft:sand"
    TEXTURE_COORDINATES = tex_coords((1, 1), (1, 1), (1, 1))


class Bricks(AbstractBlock):
    NAME = "minecraft:bricks"
    TEXTURE_COORDINATES = tex_coords((2, 0), (2, 0), (2, 0))


class Stone(AbstractBlock):
    NAME = "minecraft:stone"
    TEXTURE_COORDINATES = tex_coords((2, 1), (2, 1), (2, 1))
