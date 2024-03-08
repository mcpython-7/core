from __future__ import annotations

import pyglet
from mcpython.world.blocks.AbstractBlock import atlas

default_vert_src = """#version 330 core
in vec3 position;
in vec2 tex_coords;

out vec2 texture_coords;
out vec3 vertex_position;

uniform WindowBlock
{
    mat4 projection;
    mat4 view;
} window;

uniform mat4 model;

void main()
{
    vec4 pos = window.view * model * vec4(position, 1.0);
    gl_Position = window.projection * pos;

    vertex_position = pos.xyz;
    texture_coords = tex_coords;
}
"""
default_frag_src = """#version 330 core
in vec2 texture_coords;
in vec3 vertex_position;
out vec4 final_colors;

uniform sampler2D our_texture;

void main()
{
    final_colors = (texture(our_texture, texture_coords));
}
"""
shader = pyglet.gl.current_context.create_program(
    (default_vert_src, "vertex"), (default_frag_src, "fragment")
)
matgroup = pyglet.model.TexturedMaterialGroup(
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
    atlas.get_texture(),
)
matgroup_black_line = pyglet.graphics.ShaderGroup(pyglet.graphics.get_default_shader())


def cube_vertices(x: float, y: float, z: float, n: float) -> list[float]:
    """Return the vertices of the cube at position x, y, z with size 2*n."""
    # fmt: off
    return [
        # Top
        x-n, y+n, z-n, x-n, y+n, z+n, x+n, y+n, z+n,  # Triangle 1
        x-n, y+n, z-n, x+n, y+n, z+n, x+n, y+n, z-n,  # Triangle 2

        # Bottom
        x-n, y-n, z-n, x+n, y-n, z-n, x+n, y-n, z+n,  # Triangle 1
        x-n, y-n, z-n, x+n, y-n, z+n, x-n, y-n, z+n,  # Triangle 2

        # Left
        x-n, y-n, z-n, x-n, y-n, z+n, x-n, y+n, z+n,  # Triangle 1
        x-n, y-n, z-n, x-n, y+n, z+n, x-n, y+n, z-n,  # Triangle 2

        # Right
        x+n, y-n, z+n, x+n, y-n, z-n, x+n, y+n, z-n,  # Triangle 1
        x+n, y-n, z+n, x+n, y+n, z-n, x+n, y+n, z+n,  # Triangle 2

        # Front
        x-n, y-n, z+n, x+n, y-n, z+n, x+n, y+n, z+n,  # Triangle 1
        x-n, y-n, z+n, x+n, y+n, z+n, x-n, y+n, z+n,  # Triangle 2

        # Back
        x+n, y-n, z-n, x-n, y-n, z-n, x-n, y+n, z-n,  # Triangle 1
        x+n, y-n, z-n, x-n, y+n, z-n, x+n, y+n, z-n   # Triangle 2
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


TEXTURE_PATH = "texture.png"
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
