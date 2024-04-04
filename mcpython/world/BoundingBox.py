import pyglet.graphics.vertexdomain
from pyglet.gl import GL_LINES
from pyglet.math import Vec3

from mcpython.rendering.util import COLORED_LINE_GROUP, cube_line_vertices


class AABB:
    def __init__(self, offset: Vec3, size: Vec3):
        self.offset = offset
        self.size = size

    def create_vertex_list(
        self, batch: pyglet.graphics.Batch, position: Vec3
    ) -> pyglet.graphics.vertexdomain.VertexList:
        return pyglet.graphics.get_default_shader().vertex_list(
            24,
            GL_LINES,
            batch,
            COLORED_LINE_GROUP,
            position=(
                "f",
                cube_line_vertices(position + self.offset, self.size, 1.01),
            ),
            colors=("f", (0, 0, 0, 255) * 24),
        )

    def check_axis_intersection(self) -> float:
        pass
