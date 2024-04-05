from __future__ import annotations

import time

import pyglet
from pyglet.gl import (
    glDisable,
    GL_DEPTH_TEST,
    glEnable,
    glClear,
    GL_DEPTH_BUFFER_BIT,
    glBlendFunc,
    GL_BLEND,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_SRC_ALPHA,
    GL_CULL_FACE,
)
from pyglet.math import Vec3, Mat4
from pyglet.window import key, mouse

from mcpython.config import (
    JUMP_SPEED,
    TICKS_PER_SEC,
)
from mcpython.containers.AbstractContainer import (
    CONTAINER_STACK,
    Container,
)
from mcpython.containers.ItemStack import ItemStack
from mcpython.rendering.util import (
    off_axis_projection_matrix,
)
from mcpython.world.World import World
from mcpython.world.blocks.AbstractBlock import AbstractBlock
from mcpython.world.entity.AbstractEntity import AbstractEntity
from mcpython.world.entity.PlayerEntity import PlayerEntity
from mcpython.world.util import sectorize


class Window(pyglet.window.Window):
    INSTANCE: Window = None

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        Window.INSTANCE = self

        self.mouse_position = 0, 0

        # Whether or not the window exclusively captures the mouse.
        self.exclusive = False

        # Which sector the player is currently in.
        self.sector = None

        # The crosshairs at the center of the screen.
        self.reticle: tuple[pyglet.shapes.Line, pyglet.shapes.Line] | None = None
        self.focused_block: AbstractBlock | None = None
        self.focused_box_vertex: pyglet.graphics.vertexdomain.VertexList | None = None
        self.focused_batch = pyglet.graphics.Batch()

        # Convenience list of num keys.
        self.num_keys = [
            key._1,
            key._2,
            key._3,
            key._4,
            key._5,
            key._6,
            key._7,
            key._8,
            key._9,
        ]
        self.last_space_press = 0

        # Instance of the model that handles the world.
        self.world = World(self)

        self.player = PlayerEntity(self.world, Vec3(0, 100, 0), Vec3(0, 0, 0))

        # The label that is displayed in the top left of the canvas.
        self.label = pyglet.text.Label(
            "",
            font_name="Arial",
            font_size=18,
            x=10,
            y=self.height - 10,
            anchor_x="left",
            anchor_y="top",
            color=(0, 0, 0, 255),
        )

        self.inventory_scale = 2

        # This call schedules the `update()` method to be called
        # TICKS_PER_SEC. This is the main game event loop.
        self.last_tick = time.time()
        pyglet.clock.schedule_interval(self.update, 1.0 / TICKS_PER_SEC)

    def set_exclusive_mouse(self, exclusive: bool):
        """If `exclusive` is True, the game will capture the mouse, if False
        the game will ignore the mouse.

        """
        super(Window, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive
        self.player.strafe = [0, 0]
        self.player.key_dy = 0

    def update(self, dt: float):
        """This method is scheduled to be called repeatedly by the pyglet
        clock.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        self.world.process_queue()
        sector = sectorize(self.player.position)
        if sector != self.sector:
            self.player.change_chunks(self.sector, sector)

            if self.sector is None:
                self.world.process_entire_queue()

            self.sector = sector
        m = 20
        dt = min(dt, 0.2)
        for _ in range(m):
            self._update(dt / m)

        delta = time.time() - self.last_tick
        self.last_tick = time.time()
        self.player.update_breaking_block_state(dt)

        for _ in range(int(delta * 20)):
            self.world.tick()

    def _update(self, dt: float):
        self.player.tick(dt)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """Called when a mouse button is pressed. See pyglet docs for button
        amd modifier mappings.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        button : int
            Number representing mouse button that was clicked. 1 = left button,
            4 = right button.
        modifiers : int
            Number representing any modifying keys that were pressed when the
            mouse button was clicked.

        """
        if self.exclusive:
            stack = self.player.inventory.get_selected_itemstack()

            vector = self.player.get_sight_vector()
            block, previous, block_raw, previous_real = self.player.hit_test(
                self.player.position, vector
            )
            block_chunk = (
                self.world.get_or_create_chunk_by_position(block) if block else None
            )
            previous_chunk = (
                self.world.get_or_create_chunk_by_position(previous)
                if previous
                else None
            )

            if (
                block_chunk
                and block in block_chunk.blocks
                and block_chunk.blocks[block].on_block_interaction(
                    stack, button, modifiers
                )
            ):
                return

            if (
                block_chunk
                and not stack.is_empty()
                and stack.item.on_block_interaction(
                    stack, block_chunk.blocks.get(block, None), button, modifiers
                )
            ):
                return

            if (button == mouse.RIGHT) or (
                (button == mouse.LEFT) and (modifiers & key.MOD_CTRL)
            ):
                # ON OSX, control + left click = right click.
                if previous and not stack.is_empty():
                    old_block = previous_chunk.blocks.get(previous)

                    if old_block:
                        state2 = old_block.on_block_merging(stack, block_raw)
                        if state2 is True:
                            pass  # todo: reduce stack amount
                    elif b := stack.item.create_block_to_be_placed(stack):
                        self.world.add_block(previous, b)

                        if b.on_block_placed(stack, block, block_raw) is False:
                            self.world.remove_block(b)
                        else:
                            b.update_render_state()

            elif button == pyglet.window.mouse.LEFT and block and block_chunk:
                self.player.update_breaking_block()

            elif button == pyglet.window.mouse.MIDDLE and block and block_chunk:
                instance = block_chunk.blocks[block]

                slot = self.player.inventory.find_item(instance.NAME)

                if slot is None:
                    itemstack = self.player.inventory.get_selected_itemstack()
                    self.player.inventory.get_selected_slot().set_stack(
                        ItemStack(instance.NAME)
                    )
                    if not itemstack.is_empty():
                        self.player.inventory.insert(itemstack)

                elif slot not in self.player.inventory.slots[:9]:
                    itemstack = self.player.inventory.get_selected_itemstack()
                    self.player.inventory.get_selected_slot().set_stack(slot.itemstack)
                    slot.set_stack(itemstack)

                else:
                    self.player.inventory.selected_slot = (
                        self.player.inventory.slots.index(slot)
                    )
                    if self.player.breaking_block is not None:
                        self.player.update_breaking_block(force_reset=True)

            return

        for container in CONTAINER_STACK:
            if container.on_mouse_press(
                *container.window_to_relative_world(
                    (x, y), self.get_size(), self.inventory_scale
                ),
                button,
                modifiers,
            ):
                return

    def on_mouse_release(self, x, y, button, modifiers):
        self.player.breaking_block = None

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.on_any_mouse_motion(x, y, dx, dy, 0, 0)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.on_any_mouse_motion(x, y, dx, dy, buttons, modifiers)

    def on_any_mouse_motion(self, x, y, dx, dy, buttons, modifiers):
        """Called when the player moves the mouse.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        dx, dy : float
            The movement of the mouse.

        """
        if self.exclusive:
            m = 0.15

            x, y = self.player.rotation
            x, y = x + dx * m, y + dy * m

            # y = max(-90.0, min(90.0, y))
            y = max(-89.9, min(89.9, y))

            self.player.rotation = (x, y)

        self.mouse_position = x, y

        for container in CONTAINER_STACK:
            container.on_mouse_motion(
                *container.window_to_relative_world(
                    (x, y), self.get_size(), self.inventory_scale
                ),
                dx / self.inventory_scale,
                dy / self.inventory_scale,
                buttons,
                modifiers,
            )

    def on_key_press(self, symbol: int, modifiers: int):
        """Called when the player presses a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """

        for container in CONTAINER_STACK:
            if container.on_key_press(symbol, modifiers):
                return

        if self.exclusive:
            if symbol == key.W:
                self.player.strafe[0] -= 1

            elif symbol == key.S:
                self.player.strafe[0] += 1

            elif symbol == key.A:
                self.player.strafe[1] -= 1

            elif symbol == key.D:
                self.player.strafe[1] += 1

            elif symbol == key.SPACE:
                if self.player.flying:
                    self.player.key_dy = 1
                elif self.player.dy == 0:
                    self.player.dy = JUMP_SPEED

                if self.player.gamemode == 1:
                    if time.time() - self.last_space_press <= 0.3:
                        self.player.flying = not self.player.flying

                        if self.player.flying:
                            self.player.key_dy = 1

                        self.last_space_press = 0
                    else:
                        self.last_space_press = time.time()

            elif symbol == key.T:
                self.player.chat.show_container()
                self.player.chat.ignore_next_t = True
                self.set_exclusive_mouse(False)
                return pyglet.event.EVENT_HANDLED

            elif symbol in (key.LSHIFT, key.RSHIFT):
                self.player.key_dy = -1

        if symbol == key.ESCAPE:
            for container in CONTAINER_STACK:
                container.on_close_with_escape()

            self.set_exclusive_mouse(not self.exclusive)

        elif symbol == key.E:
            if self.player.chat.open:
                pass
            elif self.player.inventory.open:
                self.set_exclusive_mouse(True)
                self.player.inventory.hide_container()
            else:
                self.set_exclusive_mouse(False)
                self.player.inventory.show_container()

        elif symbol in self.num_keys and self.exclusive:
            index = symbol - self.num_keys[0]
            self.player.inventory.selected_slot = index
            if self.player.breaking_block is not None:
                self.player.update_breaking_block(force_reset=True)

    def on_text(self, text):
        for container in CONTAINER_STACK:
            if container.on_text(text):
                return pyglet.event.EVENT_HANDLED

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self.exclusive:
            self.player.inventory.selected_slot = int(
                (self.player.inventory.selected_slot - scroll_y) % 9
            )
            if self.player.breaking_block is not None:
                self.player.update_breaking_block(force_reset=True)

    def on_key_release(self, symbol: int, modifiers: int):
        """Called when the player releases a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """
        if self.exclusive:
            if symbol == key.W:
                self.player.strafe[0] = 0
            elif symbol == key.S:
                self.player.strafe[0] = 0
            elif symbol == key.A:
                self.player.strafe[1] = 0
            elif symbol == key.D:
                self.player.strafe[1] = 0
            elif symbol in (key.SPACE, key.LSHIFT, key.RSHIFT):
                self.player.key_dy = 0

    def on_resize(self, width: int, height: int):
        """Called when the window is resized to a new `width` and `height`."""
        super().on_resize(width, height)
        # label
        self.label.y = height - 10
        # reticle
        x, y = self.width // 2, self.height // 2
        n = 10

        self.reticle = (
            pyglet.shapes.Line(x - n, y, x + n, y, color=(0, 0, 0, 255), width=2),
            pyglet.shapes.Line(x, y - n, x, y + n, color=(0, 0, 0, 255), width=2),
        )

        for container in CONTAINER_STACK:
            container.on_resize(width, height)

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

    def on_draw(self):
        """Called by pyglet to draw the canvas."""
        self.clear()
        self.set_3d()
        self.world.batch.draw()

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)
        glDisable(GL_CULL_FACE)
        self.world.alpha_batch.draw()

        if self.player.breaking_block:
            if self.player.breaking_block_provider is None:
                from mcpython.rendering.Models import BreakingTextureProvider

                self.player.breaking_block_provider = BreakingTextureProvider()
            self.set_3d(offset=Vec3(*self.player.breaking_block.position))
            self.player.breaking_block_provider.update(
                1
                - self.player.breaking_block_timer
                / self.player.breaking_block_total_timer
                if self.player.breaking_block_timer
                else 0
            )
            self.player.breaking_block_provider.draw()

        glDisable(GL_BLEND)

        self.draw_focused_block()
        self.set_2d()
        self.draw_label()
        self.draw_reticle()

        self.draw_inventories()
        self.player.chat.draw_chat_output(self)

    def draw_inventories(self):
        glClear(GL_DEPTH_BUFFER_BIT)

        for container in CONTAINER_STACK:
            self.set_2d_centered_for_inventory(container)
            container.draw(self)

        if any(container.SHOULD_DRAW_MOVING_SLOT for container in CONTAINER_STACK):
            self.set_2d_centered_for_inventory(self.player.inventory)

            self.player.moving_player_slot.update_position(
                self.player.inventory.window_to_relative_world(
                    (self.mouse_position[0] - 8, self.mouse_position[1] - 7),
                    self.get_size(),
                    self.inventory_scale,
                )
            )

            self.player.moving_player_slot.draw(self)

        self.player.slot_hover_info.draw(self)

    def invalidate_focused_block(self):
        if self.focused_block:
            self.focused_block = None
            self.focused_box_vertex.delete()
            self.focused_box_vertex = None

    def draw_focused_block(self):
        """Draw black edges around the block that is currently under the
        crosshairs.

        """
        vector = self.player.get_sight_vector()
        if block := self.player.hit_test(self.player.position, vector)[0]:
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

    def draw_label(self):
        """Draw the label in the top left of the screen."""
        x, y, z = self.player.position
        self.label.text = "%02d (%.2f, %.2f, %.2f) %d (%d)" % (
            pyglet.clock.get_frequency(),
            x,
            y,
            z,
            len(self.world.chunks),
            len(
                self.world.get_or_create_chunk_by_position(self.player.position).blocks
            ),
        )
        self.label.draw()

    def draw_reticle(self):
        """Draw the crosshairs in the center of the screen."""
        self.reticle[0].draw()
        self.reticle[1].draw()
