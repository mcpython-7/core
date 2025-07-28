import itertools
import math

import pyglet
from pyglet.gl import GL_TRIANGLES
from pyglet.math import Vec2

from mcpython.rendering.util import LAYERED_ITEM_SHADER, LAYERED_ITEM_GROUP


class NineSplitTexture:
    def __init__(self, texture: pyglet.image.Texture, border=3):
        self.texture = texture
        self.border = border

        width, height = texture.width, texture.height

        self.fragments = [
            [
                (0, 0, border, border),
                (0, border, border, height - 2 * border),
                (0, height - border, border, border),
            ],
            [
                (border, 0, width - 2 * border, border),
                (border, border, width - 2 * border, height - 2 * border),
                (border, height - border, width - 2 * border, border),
            ],
            [
                (width - border, 0, border, border),
                (width - border, border, border, height - 2 * border),
                (width - border, height - border, border, border),
            ],
        ]
        self.group = pyglet.model.TexturedMaterialGroup(
            pyglet.model.SimpleMaterial(
                "XY",
                [1.0, 1.0, 1.0, 1.0],
                [1.0, 1.0, 1.0, 1.0],
                [1.0, 1.0, 1.0, 1.0],
                [0.0, 0.0, 0.0, 1.0],
                100,
                "texture.png",
            ),
            LAYERED_ITEM_SHADER,
            self.texture.get_texture(),
        )

    def create_vertex_list(
        self, size: Vec2, batch: pyglet.graphics.Batch, offset: Vec2 = Vec2(0, 0)
    ):
        if size[0] < 2 * self.border or size[1] < 2 * self.border:
            raise ValueError(
                f"Texture size is too small, must be at least {self.border * 2} pixels in both dimensions!"
            )

        # LAYERED_ITEM_SHADER, LAYERED_ITEM_GROUP
        vertices: list[Vec2] = []
        texture_coordinates: list[Vec2] = []

        def create_rectangle(x: int, y: int, sx: int, sy: int, tx: int, ty: int, *_):
            nonlocal vertices, texture_coordinates
            vertices += [
                Vec2(x, y),
                Vec2(x, y + sy),
                Vec2(x + sx, y + sy),
                Vec2(x, y),
                Vec2(x + sx, y + sy),
                Vec2(x + sx, y),
            ]
            texture_coordinates += [
                Vec2(tx, ty),
                Vec2(tx, ty + sy),
                Vec2(tx + sx, ty + sy),
                Vec2(tx, ty),
                Vec2(tx + sx, ty + sy),
                Vec2(tx + sx, ty),
            ]

        w, h = size
        tw, th = self.texture.width, self.texture.height

        # lower left corner
        create_rectangle(0, 0, self.border, self.border, *self.fragments[0][0])

        # lower right corner
        create_rectangle(
            w - self.border, 0, self.border, self.border, *self.fragments[2][0]
        )

        # upper left corner
        create_rectangle(
            0, h - self.border, self.border, self.border, *self.fragments[0][2]
        )

        # upper right corner
        create_rectangle(
            w - self.border,
            h - self.border,
            self.border,
            self.border,
            *self.fragments[2][2],
        )

        xbox = (w - self.border * 2) // (tw - self.border * 2)
        xrem = (w - self.border * 2) % (tw - self.border * 2)
        ybox = (h - self.border * 2) // (th - self.border * 2)
        yrem = (h - self.border * 2) % (th - self.border * 2)

        # lower & upper border
        for x in range(xbox):
            # lower
            create_rectangle(
                self.border + x * (tw - self.border * 2),
                0,
                tw - self.border * 2,
                self.border,
                *self.fragments[1][0],
            )
            # upper
            create_rectangle(
                self.border + x * (tw - self.border * 2),
                h - self.border,
                tw - self.border * 2,
                self.border,
                *self.fragments[1][2],
            )
            # main remainder upper
            create_rectangle(
                self.border + x * (tw - self.border * 2),
                self.border + ybox * (th - self.border * 2),
                tw - self.border * 2,
                yrem,
                *self.fragments[1][1],
            )
        if xrem > 0:
            # lower
            create_rectangle(
                self.border + xbox * (tw - self.border * 2),
                0,
                xrem,
                self.border,
                *self.fragments[1][0],
            )
            # upper
            create_rectangle(
                self.border + xbox * (th - self.border * 2),
                h - self.border,
                xrem,
                self.border,
                *self.fragments[1][2],
            )

        # left and right border
        for y in range(ybox):
            # left
            create_rectangle(
                0,
                self.border + y * (th - self.border * 2),
                self.border,
                th - self.border * 2,
                *self.fragments[0][1],
            )
            # right
            create_rectangle(
                w - self.border,
                self.border + y * (th - self.border * 2),
                self.border,
                th - self.border * 2,
                *self.fragments[2][1],
            )
            # main body rem right
            create_rectangle(
                self.border + xbox * (tw - self.border * 2),
                self.border + y * (th - self.border * 2),
                xrem,
                th - self.border * 2,
                *self.fragments[1][1],
            )
        if yrem > 0:
            # left
            create_rectangle(
                0,
                self.border + ybox * (th - self.border * 2),
                self.border,
                yrem,
                *self.fragments[0][1],
            )
            # right
            create_rectangle(
                w - self.border,
                self.border + ybox * (th - self.border * 2),
                self.border,
                yrem,
                *self.fragments[2][1],
            )

        # main block
        for x, y in itertools.product(range(xbox), range(ybox)):
            create_rectangle(
                self.border + x * (tw - self.border * 2),
                self.border + y * (th - self.border * 2),
                tw - self.border * 2,
                th - self.border * 2,
                *self.fragments[1][1],
            )

        # main block upper right rem
        if xrem > 0 and yrem > 0:
            create_rectangle(
                self.border + xbox * (tw - self.border * 2),
                self.border + ybox * (th - self.border * 2),
                xrem,
                yrem,
                *self.fragments[1][1],
            )

        return LAYERED_ITEM_SHADER.vertex_list(
            len(vertices),
            GL_TRIANGLES,
            batch,
            self.group,
            position=("f", sum((tuple(x + offset) for x in vertices), ())),
            tex_coords=(
                "f",
                sum(((x / tw, y / th) for x, y in texture_coordinates), ()),
            ),
        )
