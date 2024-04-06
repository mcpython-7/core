from __future__ import annotations


import pyglet
from pyglet.gl import (
    glDisable,
    GL_DEPTH_TEST,
    glEnable,
    glClear,
    GL_DEPTH_BUFFER_BIT,
    GL_CULL_FACE,
)
from pyglet.math import Vec3, Mat4
from pyglet.window import key, mouse

from mcpython.config import (
    TICKS_PER_SEC,
)
from mcpython.containers.AbstractContainer import (
    Container,
)
from mcpython.rendering.util import (
    off_axis_projection_matrix,
)
from mcpython.states.StateHandler import StateHandler
from mcpython.world.World import World
from mcpython.world.blocks.AbstractBlock import AbstractBlock
from mcpython.world.entity.PlayerEntity import PlayerEntity


class Window(pyglet.window.Window):
    INSTANCE: Window = None

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        Window.INSTANCE = self

        self.key_state_handler = key.KeyStateHandler()
        self.mouse_state_handler = mouse.MouseStateHandler()

        self.push_handlers(self.key_state_handler, self.mouse_state_handler)

        # Whether or not the window exclusively captures the mouse.
        self.exclusive = False

        # Instance of the model that handles the world.
        self.world = World(self)

        self.player = PlayerEntity(self.world, Vec3(0, 100, 0), Vec3(0, 0, 0))

        self.inventory_scale = 2

        self.state_handler = StateHandler()

        from mcpython.states.GameState import GameState

        self.game_state = GameState(self)
        self.state_handler.register_state("minecraft:game", self.game_state)
        self.state_handler.change_state("minecraft:game")

        # This call schedules the `update()` method to be called
        # TICKS_PER_SEC. This is the main game event loop.
        pyglet.clock.schedule_interval(self.update, 1.0 / TICKS_PER_SEC)

    @property
    def mouse_position(self) -> tuple[int, int]:
        return self.mouse_state_handler["x"], self.mouse_state_handler["y"]

    def set_exclusive_mouse(self, exclusive: bool):
        """If `exclusive` is True, the game will capture the mouse, if False
        the game will ignore the mouse.

        """
        super(Window, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive
        self.player.strafe = [0, 0]
        self.player.key_dy = 0

    def update(self, dt: float):
        self.state_handler.handle_on_tick(dt)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        return self.state_handler.handle_on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        return self.state_handler.handle_on_mouse_release(x, y, button, modifiers)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        return self.state_handler.handle_on_mouse_motion(x, y, dx, dy, 0, 0)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        return self.state_handler.handle_on_mouse_motion(
            x, y, dx, dy, buttons, modifiers
        )

    def on_key_press(self, symbol: int, modifiers: int):
        return self.state_handler.handle_on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        return self.state_handler.handle_on_key_release(symbol, modifiers)

    def on_text(self, text):
        return self.state_handler.handle_on_text(text)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        return self.state_handler.handle_on_mouse_scroll(x, y, scroll_x, scroll_y)

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        return self.state_handler.handle_on_resize(width, height)

    def on_draw(self):
        """Called by pyglet to draw the canvas."""
        self.clear()
        self.state_handler.handle_on_draw(self)

    def set_2d(self):
        """Configure OpenGL to draw in 2d."""
        width, height = self.get_size()
        self.projection = Mat4.orthogonal_projection(0, width, 0, height, -255, 255)
        self.view = Mat4()
        glDisable(GL_DEPTH_TEST)

    def set_2d_centered_for_inventory(
        self, container: Container, scale=1, offset=(0, 0)
    ):
        width, height = self.get_size()
        self.projection = Mat4.orthogonal_projection(0, width, 0, height, -255, 255)
        self.view = (
            Mat4.from_translation(
                Vec3(
                    width * container.render_anchor[0],
                    height * container.render_anchor[1],
                    0,
                )
            )
            @ Mat4.from_scale(
                Vec3(self.inventory_scale * scale, self.inventory_scale * scale, 1)
            )
            @ Mat4.from_translation(Vec3(*offset))
        )
        glDisable(GL_DEPTH_TEST)

    def set_2d_for_ui(
        self,
        win_anchor: tuple[int, int],
        item_anchor: tuple[int, int],
        item_size: tuple[int, int],
    ):
        """Configure OpenGL to draw in 2d."""
        width, height = self.get_size()
        self.projection = Mat4.orthogonal_projection(0, width, 0, height, -255, 255)
        self.view = Mat4()
        self.view @= Mat4.from_translation(
            -Vec3(width * win_anchor[0], height * win_anchor[1], 0)
        )
        self.view @= Mat4.from_translation(
            Vec3(item_anchor[0] * item_size[0], item_anchor[1] * item_size[1], 0)
        )
        self.view @= Mat4.from_scale(
            Vec3(self.inventory_scale, self.inventory_scale, 1)
        )
        glDisable(GL_DEPTH_TEST)

    def set_3d(self, offset: Vec3 = None, rotation: Vec3 = None):
        """Configure OpenGL to draw in 3d.3"""
        self.projection = Mat4.perspective_projection(
            self.aspect_ratio, z_near=0.1, z_far=100, fov=45
        )
        position = self.player.position
        vector = self.player.get_sight_vector()
        self.view = Mat4.look_at(position, position + vector, Vec3(0, 1, 0))
        if offset:
            self.view @= Mat4.from_translation(offset)
        if rotation:
            self.view @= Mat4.from_rotation(rotation[0], Vec3(1, 0, 0))
            self.view @= Mat4.from_rotation(rotation[1], Vec3(0, 1, 0))
            self.view @= Mat4.from_rotation(rotation[2], Vec3(0, 0, 1))

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

    def set_preview_3d(self, offset: Vec3):
        self.projection = off_axis_projection_matrix(
            z_near=0.1,
            z_far=100,
            aspect=self.aspect_ratio,
            fov=45,
            off_center_x=offset[0],
            off_center_y=offset[1],
            size=self.get_size(),
        )

        # don't know why this is needed, but we need it here...
        extra_scale = self.get_size()[1] / 600

        glClear(GL_DEPTH_BUFFER_BIT)
        self.view = (
            Mat4()
            @ Mat4.look_at(Vec3(2, 2, 2), Vec3(0, 0, 0), Vec3(0, 1, 0))
            @ Mat4.from_scale(Vec3(0.08, 0.08, 0.08) / extra_scale)
        )

        glEnable(GL_DEPTH_TEST)

    def invalidate_focused_block(self):
        from mcpython.states.WorldController import WorldController

        state = self.state_handler.find_active_part(WorldController)
        if state or state.focused_block:
            state.focused_block = None
            state.focused_box_vertex.delete()
            state.focused_box_vertex = None
