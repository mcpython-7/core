import typing
from abc import ABC

from pyglet.math import Vec3

from mcpython.util.math import normalize


def is_in_range(start: Vec3, inner: Vec3, end: Vec3) -> bool:
    a, b, c = (min(a, b) for a, b in zip(start, end))
    d, e, f = inner
    g, h, i = (max(a, b) for a, b in zip(start, end))

    return a <= d <= g and b <= e <= h and c <= f <= i


class AbstractBoundingElement(ABC):
    def collides_with_point(self, base: Vec3, point: Vec3) -> bool:
        raise NotImplementedError

    def collides_with_ray(self, base: Vec3, source: Vec3, direction: Vec3) -> bool:
        raise NotImplementedError

    def draw_outline(self, base: Vec3):
        pass


async def collision_pass_ray(dimension, position: Vec3, direction: Vec3):
    direction = direction.normalize()
    max_steps = 20
    original_position = position

    from mcpython.world.AbstractDefinition import ChunkDoesNotExistException

    for _ in range(max_steps):
        normalized = normalize(*position)
        print(position, normalized)
        try:
            block_state = await dimension.get_block(*normalized)
        except ChunkDoesNotExistException:
            pass
        else:
            if block_state is not None and block_state.bounding_box.collides_with_ray(Vec3(*block_state.world_position), position - direction, direction):
                return block_state

        position += direction


class BoundingBox(AbstractBoundingElement):
    def __init__(self, size: Vec3, offset: Vec3 = Vec3(0, 0, 0)):
        self.size = size
        self.offset = offset

    def collides_with_point(self, base: Vec3, point: Vec3) -> bool:
        start = base + self.offset - self.size / 2
        end = base + self.offset + self.size / 2
        return is_in_range(start, point, end)

    def collides_with_ray(self, base: Vec3, source: Vec3, direction: Vec3) -> bool:
        offset = base - source + self.offset
        start = offset
        end = offset + self.size

        far = Vec3(*(round(e * 100) / 100 for e in (
            end[0] if direction[0] >= 0 else start[0],
            end[1] if direction[1] >= 0 else start[1],
            end[2] if direction[2] >= 0 else start[2],
        )))

        near = Vec3(*(round(e * 100) / 100 for e in (
            end[0] if direction[0] <= 0 else start[0],
            end[1] if direction[1] <= 0 else start[1],
            end[2] if direction[2] <= 0 else start[2],
        )))

        current = Vec3(0, 0, 0)

        step_size = min(self.size) * .99
        direction = Vec3(*(round(e * 100) / 100 for e in direction.normalize() * step_size))

        print(direction)

        while is_in_range(Vec3(0, 0, 0), current, far):
            if is_in_range(near, current, far):
                return True

            current += direction
            print(current, near, far)

        return False


class BoundingCollection(AbstractBoundingElement):
    def __init__(self, *items: AbstractBoundingElement):
        self.items = list(items)

    def collides_with_point(self, base: Vec3, point: Vec3) -> bool:
        for element in self.items:
            if element.collides_with_point(base, point):
                return True

        return False

    def collides_with_ray(self, base: Vec3, source: Vec3, direction: Vec3) -> bool:
        for element in self.items:
            if element.collides_with_ray(base, source, direction):
                return True

        return False

    def draw_outline(self, base: Vec3):
        for element in self.items:
            element.draw_outline(base)

