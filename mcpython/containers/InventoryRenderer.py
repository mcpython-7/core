from __future__ import annotations

import typing

import pyglet.graphics
from pyglet.math import Vec2

from mcpython.rendering.NineSplitTexture import NineSplitTexture
from mcpython.resources.ResourceManager import ResourceManager


class InventoryRenderConfig:
    """
    A class holding the information how to render the inventory

    WARNING: overriding the instance attributes on the class will mutate ALL default instances.
    This can be a desired effect, but also might not be what you want to do
    """

    BACKGROUND = NineSplitTexture(
        ResourceManager.load_image(
            "assets/minecraft/textures/gui/demo_background.png"
        ).get_region((0, 0), (248, 166)),
        border=4,
    )

    SLOT_TEXTURE = ResourceManager.load_image(
        "assets/minecraft/textures/gui/sprites/container/slot.png"
    ).to_pyglet()


class InventoryRenderer:
    class InventoryRendererInstance:
        def __init__(
            self,
            inventory: InventoryRenderer,
            batch: pyglet.graphics.Batch,
            offset: tuple[int, int],
        ):
            self.inventory = inventory
            self.batch = batch
            self.vertex_list = inventory.create_batched(batch, offset)

        def draw(self):
            self.batch.draw()

    def __init__(
        self,
        size: tuple[int, int],
        config: InventoryRenderConfig = InventoryRenderConfig(),
    ):
        self.size = size
        self.config = config

        self.items: list[
            typing.Callable[[pyglet.graphics.Batch, tuple[int, int]], list]
        ] = []

    def add_slot(self, position: tuple[int, int]):
        x, y = position
        self.items.append(
            lambda batch, offset: [
                pyglet.sprite.Sprite(
                    self.config.SLOT_TEXTURE,
                    x + offset[0],
                    y + offset[1],
                    batch=batch,
                )
            ]
        )

    def add_texture(
        self,
        texture: pyglet.image.AbstractImage | str,
        position: tuple[int, int],
        scale=1.0,
    ):
        if isinstance(texture, str):
            texture = ResourceManager.load_pyglet_image(texture)

        x, y = position

        def create(batch, offset):
            sprite = pyglet.sprite.Sprite(
                texture,
                x + offset[0],
                y + offset[1],
                batch=batch,
            )
            sprite.scale = scale
            return [sprite]

        self.items.append(create)

    def add_nine_split_texture(
        self,
        texture: NineSplitTexture,
        position: tuple[int, int],
        size: tuple[int, int],
    ):
        self.items.append(
            lambda batch, offset: texture.create_vertex_list(
                Vec2(*size),
                batch,
                Vec2(
                    position[0] + offset[0],
                    position[1] + offset[1],
                ),
            )
        )

    def create_batched(
        self, batch: pyglet.graphics.Batch, offset: tuple[int, int] = (0, 0)
    ) -> list:
        vertex_list = [
            self.config.BACKGROUND.create_vertex_list(
                Vec2(*self.size),
                batch,
                offset=Vec2(*offset),
            )
        ] + [func(batch, offset) for func in self.items]

        return vertex_list

    def instantiate(
        self, offset: tuple[int, int], batch: pyglet.graphics.Batch = None
    ) -> InventoryRendererInstance:
        return self.InventoryRendererInstance(
            self, batch or pyglet.graphics.Batch(), offset
        )
