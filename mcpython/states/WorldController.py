from __future__ import annotations

import time

import pyglet
from pyglet.gl import (
    glBlendFunc,
    GL_SRC_ALPHA,
    GL_ONE_MINUS_SRC_ALPHA,
    glEnable,
    glDisable,
    GL_BLEND,
    GL_CULL_FACE,
)
from pyglet.math import Vec3

from mcpython.rendering.Window import Window
from mcpython.states.AbstractState import AbstractStatePart
from mcpython.world.World import World
from mcpython.world.blocks.AbstractBlock import AbstractBlock


class WorldController(AbstractStatePart):
    def __init__(self, world: World):
        super().__init__()
        self.world = world
        self.last_tick = time.time()

        self.focused_block: AbstractBlock | None = None
        self.focused_box_vertex: pyglet.graphics.vertexdomain.VertexList | None = None
        self.focused_batch = pyglet.graphics.Batch()

    def on_draw(self, window: Window):
        window.set_3d()
        self.world.batch.draw()

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)
        glDisable(GL_CULL_FACE)
        self.world.alpha_batch.draw()

        if window.player.breaking_block:
            if window.player.breaking_block_provider is None:
                from mcpython.rendering.Models import BreakingTextureProvider

                window.player.breaking_block_provider = BreakingTextureProvider()
            window.set_3d(offset=Vec3(*window.player.breaking_block.position))
            window.player.breaking_block_provider.update(
                1
                - window.player.breaking_block_timer
                / window.player.breaking_block_total_timer
                if window.player.breaking_block_timer
                else 0
            )
            window.player.breaking_block_provider.draw()

        glDisable(GL_BLEND)

        self.draw_focused_block(window)

    def draw_focused_block(self, window: Window):
        """Draw black edges around the block that is currently under the
        crosshairs.

        """
        vector = window.player.get_sight_vector()
        if block := window.player.hit_test(window.player.position, vector)[0]:
            instance = self.world.get_or_create_chunk_by_position(block).blocks.get(
                block
            )
            if instance is None:
                return

            if instance != self.focused_block:
                self.focused_block = instance

                if self.focused_box_vertex:
                    self.focused_box_vertex.delete()

                self.focused_box_vertex = (
                    instance.get_bounding_box().create_vertex_list(
                        self.focused_batch, Vec3(*instance.position)
                    )
                )

            self.focused_batch.draw()

        else:
            self.focused_block = None

            if self.focused_box_vertex:
                self.focused_box_vertex.delete()
                self.focused_box_vertex = None

    def on_tick(self, dt: float):
        self.world.process_queue()

        m = 20
        dt = min(dt, 0.2)
        for _ in range(m):
            self.world.entity_tick(dt / m)

        delta = time.time() - self.last_tick
        self.last_tick = time.time()
        for _ in range(int(delta * 20)):
            self.world.tick()
