from __future__ import annotations

import pathlib

import pyglet
from pyglet.math import Vec3

from mcpython.rendering.BlockModels import _TEXTURE_ATLAS


_GROUPS: list[pyglet.model.TexturedMaterialGroup] = []


def update_texture_atlas_references():
    _TEXTURE_ATLAS.refresh()
    for group in _GROUPS:
        group.texture = _TEXTURE_ATLAS.get_texture()


def create_shader_group(
    name: str,
) -> tuple[pyglet.graphics.Shader, pyglet.model.TexturedMaterialGroup]:
    path = pathlib.Path(__file__).parent
    vertex_file = path.joinpath("shaders", f"{name}_vertex.glsl")
    fragment_file = path.joinpath("shaders", f"{name}_fragment.glsl")

    shader = pyglet.gl.current_context.create_program(
        (vertex_file.read_text(), "vertex"), (fragment_file.read_text(), "fragment")
    )
    group = pyglet.model.TexturedMaterialGroup(
        pyglet.model.Material(
            "XY",
            [1.0, 1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0],
            [0.0, 0.0, 0.0, 1.0],
            100,
            "texture.png",
        ),
        shader,
        _TEXTURE_ATLAS.get_texture(),
    )
    _GROUPS.append(group)

    return shader, group


DEFAULT_BLOCK_SHADER, DEFAULT_BLOCK_GROUP = create_shader_group("default_block_shader")
COLORED_BLOCK_SHADER, COLORED_BLOCK_GROUP = create_shader_group("colored_block_shader")
COLORED_LINE_SHADER, COLORED_LINE_GROUP = create_shader_group("colored_outline_shader")


def cube_vertices(center: Vec3, size: Vec3) -> list[float]:
    x, y, z = center
    nx, ny, nz = size
    """Return the vertices of the cube at position x, y, z with size 2*n."""
    # fmt: off
    return [
        # Top
        x-nx, y+ny, z-nz, x-nx, y+ny, z+nz, x+nx, y+ny, z+nz,  # Triangle 1
        x-nx, y+ny, z-nz, x+nx, y+ny, z+nz, x+nx, y+ny, z-nz,  # Triangle 2

        # Bottom
        x-nx, y-ny, z-nz, x+nx, y-ny, z-nz, x+nx, y-ny, z+nz,  # Triangle 1
        x-nx, y-ny, z-nz, x+nx, y-ny, z+nz, x-nx, y-ny, z+nz,  # Triangle 2

        # Left
        x-nx, y-ny, z-nz, x-nx, y-ny, z+nz, x-nx, y+ny, z+nz,  # Triangle 1
        x-nx, y-ny, z-nz, x-nx, y+ny, z+nz, x-nx, y+ny, z-nz,  # Triangle 2

        # Right
        x+nx, y-ny, z+nz, x+nx, y-ny, z-nz, x+nx, y+ny, z-nz,  # Triangle 1
        x+nx, y-ny, z+nz, x+nx, y+ny, z-nz, x+nx, y+ny, z+nz,  # Triangle 2

        # Front
        x-nx, y-ny, z+nz, x+nx, y-ny, z+nz, x+nx, y+ny, z+nz,  # Triangle 1
        x-nx, y-ny, z+nz, x+nx, y+ny, z+nz, x-nx, y+ny, z+nz,  # Triangle 2

        # Back
        x+nx, y-ny, z-nz, x-nx, y-ny, z-nz, x-nx, y+ny, z-nz,  # Triangle 1
        x+nx, y-ny, z-nz, x-nx, y+ny, z-nz, x+nx, y+ny, z-nz   # Triangle 2
    ]
    # fmt: on


def cube_line_vertices(x: float, y: float, z: float, n: float) -> list[float]:
    """Return the vertices of the cube at position x, y, z with size 2*n."""
    # fmt: off
    return [
        # Top
        x-n, y+n, z-n, x-n, y+n, z+n,  # Line 1
        x-n, y+n, z+n, x+n, y+n, z+n,  # Line 2
        x+n, y+n, z+n, x+n, y+n, z-n,  # Line 3
        x+n, y+n, z-n, x-n, y+n, z-n,  # Line 4

        # Bottom
        x-n, y-n, z-n, x-n, y-n, z+n,  # Line 1
        x-n, y-n, z+n, x+n, y-n, z+n,  # Line 2
        x+n, y-n, z+n, x+n, y-n, z-n,  # Line 3
        x+n, y-n, z-n, x-n, y-n, z-n,  # Line 4

        # Vertical lines connecting top and bottom
        x-n, y+n, z-n, x-n, y-n, z-n,  # Line 1
        x-n, y+n, z+n, x-n, y-n, z+n,  # Line 2
        x+n, y+n, z+n, x+n, y-n, z+n,  # Line 3
        x+n, y+n, z-n, x+n, y-n, z-n   # Line 4
    ]
    # fmt: on


FACES = [
    (0, 1, 0),
    (0, -1, 0),
    (-1, 0, 0),
    (1, 0, 0),
    (0, 0, 1),
    (0, 0, -1),
]


def setup_fog():
    """Configure the OpenGL fog properties.
    todo
    """
    # # Enable fog. Fog "blends a fog color with each rasterized pixel fragment's
    # # post-texturing color."
    # glEnable(GL_FOG)
    # # Set the fog color.
    # glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1))
    # # Say we have no preference between rendering speed and quality.
    # glHint(GL_FOG_HINT, GL_DONT_CARE)
    # # Specify the equation used to compute the blending factor.
    # glFogi(GL_FOG_MODE, GL_LINEAR)
    # # How close and far away fog starts and ends. The closer the start and end,
    # # the denser the fog in the fog range.
    # glFogf(GL_FOG_START, 20.0)
    # glFogf(GL_FOG_END, 60.0)
