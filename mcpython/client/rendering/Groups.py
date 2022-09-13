import os

from pyglet import gl as gl
from pyglet.graphics.shader import Shader
from pyglet.graphics.shader import ShaderProgram
from pyglet.model import BaseMaterialGroup


local = os.path.dirname(__file__)


class TexturedMaterialGroup(BaseMaterialGroup):
    default_vert_src = open(local+"/cube_vertex_shader.glsl").read()
    default_frag_src = open(local+"/cube_fragment_shader.glsl").read()

    PROGRAM = ShaderProgram(
        Shader(default_vert_src, "vertex"),
        Shader(default_frag_src, "fragment")
    )

    def __init__(self, material, texture, order=0, parent=None):
        super().__init__(material, self.PROGRAM, order, parent)
        self.texture = texture

    def set_state(self):
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glTexParameteri(self.texture.target, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glBindTexture(self.texture.target, self.texture.id)
        self.program.use()
        self.program['model'] = self.matrix

    def __hash__(self):
        return hash((self.texture.target, self.texture.id, self.program, self.order, self.parent))

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.material == other.material and
                self.texture.target == other.texture.target and
                self.texture.id == other.texture.id and
                self.program == other.program and
                self.order == other.order and
                self.parent == other.parent)
