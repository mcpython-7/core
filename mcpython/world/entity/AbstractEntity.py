from __future__ import annotations

from abc import ABC

import typing

import pyglet.graphics.vertexdomain
from pyglet.math import Vec3

from mcpython.resources.Registry import Registry, IRegisterAble
from mcpython.world.util import sectorize

if typing.TYPE_CHECKING:
    from mcpython.rendering.Window import Window
    from mcpython.containers.ItemStack import ItemStack
    from mcpython.world.World import World


class AbstractEntity(IRegisterAble, ABC):
    def __init__(self, world: World, position: Vec3, rotation: Vec3):
        self.world = world
        self.chunk = self.world.get_or_create_chunk_by_position(position)
        self.chunk.entities.append(self)
        self._position = position
        self.rotation = rotation
        self.motion = Vec3(0, 0, 0)
        self.gravity_effect = 1

        # todo: use a shared batch with a special group
        self.batch = pyglet.graphics.Batch()
        self.vertex_data: list[pyglet.graphics.vertexdomain.VertexList] = []

    def get_position(self):
        return self._position

    def set_position(self, pos: Vec3):
        self._position = pos
        c = sectorize(pos)
        if self.chunk.position != c:
            chunk = self.world.get_or_create_chunk_by_position(pos)
            self.chunk.entities.remove(self)
            self.chunk = chunk
            self.chunk.entities.append(self)

    position = property(get_position, set_position)

    def try_pickup(self, itemstack: ItemStack) -> bool:
        return False

    def tick(self):
        pass

    def move_tick(self, dt: float):
        self.update_position(dt)

    def update_position(self, dt: float):
        self.position += self.motion * dt
        # todo: add constant to world
        self.motion += Vec3(0, 1, 0) * self.gravity_effect * dt * 9.81
        # todo: collision detection!

    def draw(self, window: Window):
        window.set_3d(self.position, self.rotation)
        self.batch.draw()


ENTITY_REGISTRY = Registry("minecraft:entities", AbstractEntity)

from mcpython.world.entity import PlayerEntity

ENTITY_REGISTRY.register(PlayerEntity.PlayerEntity)
