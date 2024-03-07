import pyglet
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.gl import GL_TRIANGLES
from pyglet.math import Mat4, Vec3

batch = pyglet.graphics.Batch()
window = pyglet.window.Window(1280, 720)

vertex_source = """
#version 330
layout(location = 0) in vec2 vertices;
layout(location = 1) in vec4 colors;

out vec4 new_color;

uniform mat4 vp;
uniform mat4 model_mat;

void main(){

    gl_Position = vp * model_mat * vec4(vertices, 0.0f, 1.0f);
    new_color = colors;   
}


"""

fragment_source = """
#version 330
in vec4 new_color;

out vec4 out_color;

void main(){

    out_color = new_color;

}

"""

vert_shader = Shader(vertex_source, 'vertex')
frag_shader = Shader(fragment_source, 'fragment')
program = ShaderProgram(vert_shader, frag_shader)

view_mat = Mat4.from_translation(Vec3(x=0, y=0, z=-1))
proj_mat = Mat4.orthogonal_projection(left=0, right=1280, bottom=0, top=720, z_near=0.1, z_far=100)

vp = proj_mat @ view_mat

translation_mat = Mat4.from_translation(Vec3(x=640, y=360, z=0))
rotation_mat = Mat4.from_rotation(angle=10, vector=Vec3(0, 0, 1))
scale_mat = Mat4.from_scale(Vec3(2, 2, 0))

# model_mat = translation_mat @ rotation_mat @ scale_mat


program["vp"] = vp
program["model_mat"] = translation_mat

# TRIS
# program.vertex_list(3, GL_TRIANGLES,
#                     batch=batch,
#                     vertices=("f", (-0.5, -0.5,
#                                     0.5, -0.5,
#                                     0.0, 0.5)),
#                     colors=("Bn", (255, 0, 0, 255,
#                                    0, 255, 0, 255,
#                                    0, 0, 255, 255)))

# QUADS
vertices = [-0.5, -0.5, 0.5,
            0.5, -0.5, 0.5,
            0.5, 0.5, 0.5,
            -0.5, 0.5, 0.5,

            -0.5, -0.5, -0.5,
            0.5, -0.5, -0.5,
            0.5, 0.5, -0.5,
            -0.5, 0.5, -0.5, ]

indices = [0, 1, 2, 2, 3, 0,
           4, 5, 6, 6, 7, 4,
           4, 5, 1, 1, 0, 4,
           6, 7, 3, 3, 2, 6,
           5, 6, 2, 2, 1, 5,
           7, 4, 0, 0, 3, 7, ]

colors = (255, 0, 0, 255,
          0, 255, 0, 255,
          0, 0, 255, 255,
          255, 255, 255, 255,

          255, 0, 0, 255,
          0, 255, 0, 255,
          0, 0, 255, 255,
          255, 255, 255, 255)

program.vertex_list_indexed(8, GL_TRIANGLES, batch=batch,
                            indices=indices, vertices=('f', vertices),
                            colors=('Bn', colors)

                            )


@window.event
def on_draw():
    window.clear()
    batch.draw()


if __name__ == '__main__':
    pyglet.app.run()
