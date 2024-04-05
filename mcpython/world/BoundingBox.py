import typing

import pyglet.graphics.vertexdomain
from pyglet.gl import GL_LINES
from pyglet.math import Vec3

from mcpython.rendering.util import COLORED_LINE_GROUP, cube_line_vertices


class IAABB:
    def __init__(self, offset: Vec3):
        self.offset = offset

    def get_vertex_positions(self) -> list[Vec3]:
        raise NotImplementedError

    def create_vertex_list(
        self, batch: pyglet.graphics.Batch, position: Vec3
    ) -> pyglet.graphics.vertexdomain.VertexList:
        vertices = self.get_vertex_positions()

        return pyglet.graphics.get_default_shader().vertex_list(
            len(vertices),
            GL_LINES,
            batch,
            COLORED_LINE_GROUP,
            position=(
                "f",
                sum(
                    map(
                        lambda e: tuple(e + self.offset + position),
                        vertices,
                    ),
                    (),
                ),
            ),
            colors=("f", (0, 0, 0, 255) * len(vertices)),
        )

    def check_axis_intersection(self, axis: int, relative_position: Vec3) -> float:
        raise NotImplementedError

    def point_intersect(self, relative_position: Vec3) -> bool:
        raise NotImplementedError


class AABB(IAABB):
    def __init__(self, offset: Vec3, size: Vec3):
        super().__init__(offset)
        self.size = size

    def get_vertex_positions(self) -> list[Vec3]:
        return cube_line_vertices(Vec3(0, 0, 0), self.size, 1.01)

    def check_axis_intersection(self, axis: int, relative_position: Vec3) -> float:
        diff = (relative_position - self.offset)[axis] + 0.5
        return abs(self.size[axis] / 2 - diff) if abs(diff) < self.size[axis] / 2 else 0

    def point_intersect(self, relative_position: Vec3) -> bool:
        diff = relative_position - self.offset + Vec3(0.5, 0.5, 0.5)
        return all(0 <= d <= s for d, s in zip(diff, self.size))


class AABBGroup(IAABB):
    def __init__(self, offset: Vec3 = Vec3(0, 0, 0)):
        super().__init__(offset)
        self.boxes: list[IAABB] = []

    def add_box(self, box: IAABB) -> typing.Self:
        self.boxes.append(box)
        return self

    def get_vertex_positions(self) -> list[Vec3]:
        return sum(
            (
                [v + box.offset for v in box.get_vertex_positions()]
                for box in self.boxes
            ),
            [],
        )

    def check_axis_intersection(self, axis: int, relative_position: Vec3) -> float:
        return max(
            box.check_axis_intersection(axis, relative_position) for box in self.boxes
        )

    def point_intersect(self, relative_position: Vec3) -> bool:
        return any(box.point_intersect(relative_position) for box in self.boxes)
