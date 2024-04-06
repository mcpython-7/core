import math

import pyglet


class NineSplitTexture:
    def __init__(self, texture: pyglet.image.Texture, border=3):
        self.texture = texture
        self.border = border

        width, height = texture.width, texture.height

        self.fragments = [
            [
                texture.get_region(0, 0, border, border),
                texture.get_region(0, border, border, height - 2 * border),
                texture.get_region(0, height - border, border, border),
            ],
            [
                texture.get_region(border, 0, width - 2 * border, border),
                texture.get_region(
                    border, border, width - 2 * border, height - 2 * border
                ),
                texture.get_region(border, height - border, width - 2 * border, border),
            ],
            [
                texture.get_region(width - border, 0, border, border),
                texture.get_region(width - border, border, border, height - 2 * border),
                texture.get_region(width - border, height - border, border, border),
            ],
        ]

    def create_sprite_list(self, size: tuple[int, int], offset=(0, 0), batch=None):
        if size[0] < 2 * self.border or size[1] < 2 * self.border:
            raise ValueError(
                f"Texture size is too small, must be at least {self.border * 2} pixels in both dimensions!"
            )

        x, y = offset
        w, h = self.texture.width, self.texture.height

        iw, ih = self.fragments[1][1].width, self.fragments[1][1].height

        sprites = [
            pyglet.sprite.Sprite(self.fragments[0][0], x=-x, y=-y, batch=batch),
            pyglet.sprite.Sprite(
                self.fragments[2][0], x=size[0] - x - self.border, y=-y, batch=batch
            ),
            pyglet.sprite.Sprite(
                self.fragments[0][2], x=-x, y=size[1] - y - self.border, batch=batch
            ),
            pyglet.sprite.Sprite(
                self.fragments[2][2],
                x=size[0] - x - self.border,
                y=size[1] - y - self.border,
                batch=batch,
            ),
        ]
        hbox_count = (size[0] - self.border * 2) // iw
        vbox_count = (size[1] - self.border * 2) // ih

        # bottom border
        sprites.extend(
            pyglet.sprite.Sprite(
                self.fragments[1][0], x=self.border + i * iw, y=0, batch=batch
            )
            for i in range(hbox_count)
        )
        if (size[0] - 2 * self.border) % iw:
            sprites.append(
                pyglet.sprite.Sprite(
                    self.fragments[1][0].get_region(
                        0, 0, (size[0] - 2 * self.border) % iw, self.border
                    ),
                    x=self.border + hbox_count * iw,
                    y=0,
                    batch=batch,
                )
            )

        # top border
        sprites.extend(
            pyglet.sprite.Sprite(
                self.fragments[1][2],
                x=self.border + i * iw,
                y=size[1] - y - self.border,
                batch=batch,
            )
            for i in range(hbox_count)
        )
        if (size[0] - 2 * self.border) % iw > 0:
            sprites.append(
                pyglet.sprite.Sprite(
                    self.fragments[1][2].get_region(
                        0,
                        0,
                        (size[0] - 2 * self.border) % iw,
                        self.border,
                    ),
                    x=self.border + hbox_count * iw,
                    y=size[1] - y - self.border,
                    batch=batch,
                )
            )

        # left border
        sprites.extend(
            pyglet.sprite.Sprite(
                self.fragments[0][1], x=0, y=self.border + i * ih, batch=batch
            )
            for i in range(vbox_count)
        )
        if (size[1] - 2 * self.border) % ih > 0:
            sprites.append(
                pyglet.sprite.Sprite(
                    self.fragments[0][1].get_region(
                        0, 0, self.border, (size[1] - 2 * self.border) % ih
                    ),
                    x=0,
                    y=self.border + vbox_count * ih,
                    batch=batch,
                )
            )

        # right border
        sprites.extend(
            pyglet.sprite.Sprite(
                self.fragments[2][1],
                x=size[0] - x - self.border,
                y=self.border + i * ih,
                batch=batch,
            )
            for i in range(vbox_count)
        )
        if (size[1] - 2 * self.border) % ih > 0:
            sprites.append(
                pyglet.sprite.Sprite(
                    self.fragments[2][1].get_region(
                        0, 0, self.border, (size[1] - 2 * self.border) % ih
                    ),
                    x=size[0] - x - self.border,
                    y=self.border + vbox_count * ih,
                    batch=batch,
                )
            )

        # Main body
        for x in range(hbox_count):
            for y in range(vbox_count):
                sprites.append(
                    pyglet.sprite.Sprite(
                        self.fragments[1][1],
                        x=self.border + x * iw,
                        y=self.border + y * ih,
                        batch=batch,
                    )
                )

        # Top Extra
        if (size[1] - 2 * self.border) % ih > 0:
            for x in range(hbox_count):
                sprites.append(
                    pyglet.sprite.Sprite(
                        self.fragments[1][1].get_region(
                            0, 0, iw, (size[1] - 2 * self.border) % ih
                        ),
                        x=self.border + x * iw,
                        y=self.border + (vbox_count) * ih,
                        batch=batch,
                    )
                )

        # Right Extra
        if (size[0] - 2 * self.border) % iw > 0:
            for y in range(vbox_count):
                sprites.append(
                    pyglet.sprite.Sprite(
                        self.fragments[1][1].get_region(
                            0, 0, (size[0] - 2 * self.border) % iw, ih
                        ),
                        x=self.border + (hbox_count) * iw,
                        y=self.border + y * ih,
                        batch=batch,
                    )
                )

        # Top Right Extra
        if (size[0] - 2 * self.border) % iw > 0 and (
            size[1] - 2 * self.border
        ) % ih > 0:
            sprites.append(
                pyglet.sprite.Sprite(
                    self.fragments[1][1].get_region(
                        0,
                        0,
                        (size[0] - 2 * self.border) % iw,
                        (size[1] - 2 * self.border) % ih,
                    ),
                    x=self.border + (hbox_count) * iw,
                    y=self.border + (vbox_count) * ih,
                    batch=batch,
                )
            )

        return sprites
