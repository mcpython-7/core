import copy
import json
import math
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


with open(local + "/vertices.json") as f:
    CUBE_VERTEX_DEF = json.load(f)
    CUBE_VERTEX_DEF = [
        [
            Vec3(*part[3 * i : 3 * i + 3])
            for i in range(len(part) // 3)
        ]
        for part in CUBE_VERTEX_DEF
    ]


with open(local + "/tex_coords.json") as f:
    CUBE_TEX_COORDS = json.load(f)


def _inner_product(a: Vec3, b: Vec3):
    return Vec3(a.x * b.x, a.y * b.y, a.z * b.z)


def _rotate_point(point: Vec3, rotation: Vec3, center=Vec3(0, 0, 0)):
    point -= center

    return Vec3(
        point[0] * math.cos(rotation[1]) - point[2] * math.sin(rotation[1]),
        point[1],
        point[2] * math.cos(rotation[1]) + point[0] * math.sin(rotation[1]),
    ) + center


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

    def __init__(
        self,
        size: typing.Tuple[float, float, float] | Vec3,
        offset: typing.Tuple[float, float, float] | Vec3,
        textures: typing.Tuple[str, str, str, str, str, str],
    ):
        self.size = Vec3(*size)
        self.offset = Vec3(*offset)
        self.texture_paths = textures
        self.texture_infos: typing.List[TextureInfo] = []
        self.uvs: typing.List[typing.Tuple[float, float, float, float]] = [
            (0, 0, 1, 1)
        ] * 6

        self.texture: Texture = None
        self.texture_group: TexturedMaterialGroup = None
        self.tex_coords = None

        self._had_setup = False

    async def copy(self, textures: typing.Iterable[str] = None):
        instance = type(self)(self.size, self.offset, tuple(textures) if textures else copy.deepcopy(self.texture_paths))
        instance.uvs = self.uvs.copy()
        await instance.setup()
        return instance

    async def setup(self):
        self._had_setup = True

        self.texture_infos.clear()

        for texture in self.texture_paths:
            if texture == "MISSING_TEXTURE":
                info = self.ATLAS.add_texture(texture, None)
            else:
                info = self.ATLAS.add_texture(
                    texture, await RESOURCE_MANAGER.read_pillow_image(texture)
                )

            self.texture_infos.append(info)

    def bake(self):
        self.texture = self.ATLAS.pyglet_texture
        self.texture_group = TexturedMaterialGroup(
            self.MATERIAL, self.texture, parent=None
        )
        self.tex_coords = copy.deepcopy(CUBE_TEX_COORDS)

        for i, texture in enumerate(self.texture_infos):
            texture.prepare_tex_coords(self.tex_coords, i, uv=self.uvs[i])

    def add_to_batch(
        self,
        position: typing.Tuple[float, float, float],
        batch: pyglet.graphics.Batch,
        scale=1.0,
        rotation=(0, 0, 0),
        center=Vec3(0, 0, 0),
    ):
        enabled = (True,) * 6
        count = len(CUBE_VERTEX_DEF[0]) * enabled.count(True)

        rotation = Vec3(*rotation)

        pos = Vec3(*position)
        delta = self.size * (scale / 2)
        vertices = sum(([pos + _rotate_point(_inner_product(delta, e) + self.offset, rotation, center=center) for e in part] for i, part in enumerate(CUBE_VERTEX_DEF) if enabled[i]), [])

        return self.texture_group.program.vertex_list(
            count,
            GL_TRIANGLES,
            batch,
            self.texture_group,
            vertices=("f", sum(map(tuple, vertices), tuple())),
            uvCoord=("f", sum((e for i, e in enumerate(self.tex_coords) if enabled[i]), [])),
        )
