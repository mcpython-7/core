import json
import os
import typing

import pyglet
from pyglet.gl import GL_TRIANGLES
from pyglet.image import Texture
from pyglet.math import Vec3
from pyglet.model import Material

from mcpython.client.rendering.Groups import TexturedMaterialGroup
from mcpython.resources.ResourceManagement import MANAGER as RESOURCE_MANAGER
from mcpython.resources.TextureAtlas import TextureAtlas
from mcpython.resources.TextureAtlas import TextureInfo


local = os.path.dirname(__file__)


with open(local+"/vertices.json") as f:
    CUBE_VERTEX_DEF = json.load(f)
    CUBE_VERTEX_DEF = [
        Vec3(*CUBE_VERTEX_DEF[3*i:3*i+3]) for i in range(len(CUBE_VERTEX_DEF) // 3)
    ]


with open(local+"/tex_coords.json") as f:
    CUBE_TEX_COORDS = json.load(f)


def _inner_product(a: Vec3, b: Vec3):
    return Vec3(a.x * b.x, a.y * b.y, a.z * b.z)


class CubeVertexCreator:
    MATERIAL = Material(
        "stone",
        (1, 1, 1),
        (1, 1, 1),
        (1, 1, 1),
        (1, 1, 1),
        (1, 1, 1),
    )

    ATLAS = TextureAtlas()

    def __init__(self, size: typing.Tuple[float, float, float], offset: typing.Tuple[float, float, float], texture: str):
        self.size = Vec3(*size)
        self.offset = Vec3(*offset)
        self.texture_path = texture
        self.texture_info: TextureInfo = None

        self.texture: Texture = None
        self.texture_group: TexturedMaterialGroup = None
        self.tex_coords = None

        self._had_setup = False

    async def setup(self):
        self._had_setup = True

        self.texture_info = self.ATLAS.add_texture(self.texture_path, await RESOURCE_MANAGER.read_pillow_image(self.texture_path))

    def bake(self):
        self.texture = self.ATLAS.pyglet_texture
        self.texture_group = TexturedMaterialGroup(self.MATERIAL, self.texture, parent=None)
        self.tex_coords = tuple(self.texture_info.prepare_tex_coords(CUBE_TEX_COORDS))

    def add_to_batch(self, position: typing.Tuple[float, float, float], batch: pyglet.graphics.Batch, scale=1.0):
        count = len(CUBE_VERTEX_DEF)

        pos = Vec3(*position) + self.offset.scale(scale)
        delta = self.size.scale(scale / 2)

        vertices = [pos + _inner_product(delta, e) for e in CUBE_VERTEX_DEF]

        return self.texture_group.program.vertex_list(
            count, GL_TRIANGLES, batch, self.texture_group,
            vertices=('f', sum(map(tuple, vertices), tuple())),
            uvCoord=('f', self.tex_coords),
        )