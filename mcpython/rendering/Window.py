from __future__ import annotations

import math

import pyglet
from pyglet.gl import (
    GL_LINES,
    glDisable,
    GL_DEPTH_TEST,
    glEnable,
    glClear,
    GL_DEPTH_BUFFER_BIT,
)
from pyglet.math import Vec3, Mat4
from pyglet.window import key, mouse

from mcpython.commands.Chat import Chat
from mcpython.config import (
    TICKS_PER_SEC,
    FLYING_SPEED,
    WALKING_SPEED,
    GRAVITY,
    TERMINAL_VELOCITY,
    PLAYER_HEIGHT,
    JUMP_SPEED,
)
from mcpython.containers.AbstractContainer import (
    CONTAINER_STACK,
    Slot,
    Container,
    ItemInformationScreen,
)
from mcpython.containers.ItemStack import ItemStack
from mcpython.containers.PlayerInventoryContainer import (
    PlayerInventoryContainer,
    HotbarContainer,
)
from mcpython.rendering.util import (
    COLORED_LINE_GROUP,
    cube_line_vertices,
    FACES,
    off_axis_projection_matrix,
)
from mcpython.world.World import World
from mcpython.world.util import sectorize, normalize


class Window(pyglet.window.Window):
    INSTANCE: Window = None

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        Window.INSTANCE = self

        self.mouse_position = 0, 0

        # Whether or not the window exclusively captures the mouse.
        self.exclusive = False

        # When flying gravity has no effect and speed is increased.
        self.flying = False

        # Strafing is moving lateral to the direction you are facing,
        # e.g. moving to the left or right while continuing to face forward.
        #
        # First element is -1 when moving forward, 1 when moving back, and 0
        # otherwise. The second element is -1 when moving left, 1 when moving
        # right, and 0 otherwise.
        self.strafe = [0, 0]

        # Current (x, y, z) position in the world, specified with floats. Note
        # that, perhaps unlike in math class, the y-axis is the vertical axis.
        self.position = Vec3(0, 0, 0)

        # First element is rotation of the player in the x-z plane (ground
        # plane) measured from the z-axis down. The second is the rotation
        # angle from the ground plane up. Rotation is in degrees.
        #
        # The vertical plane rotation ranges from -90 (looking straight down) to
        # 90 (looking straight up). The horizontal rotation range is unbounded.
        self.rotation: tuple[float, float] = (0, 0)

        # Which sector the player is currently in.
        self.sector = None

        # The crosshairs at the center of the screen.
        self.reticle: tuple[pyglet.shapes.Line, pyglet.shapes.Line] | None = None
        self.focused_block_batch = pyglet.graphics.Batch()
        self.focused_block = pyglet.graphics.get_default_shader().vertex_list(
            24,
            GL_LINES,
            self.focused_block_batch,
            COLORED_LINE_GROUP,
            position=("f", cube_line_vertices(0, 0, 0, 0.51)),
            colors=("f", (0, 0, 0, 255) * 24),
        )

        # Velocity in the y (upward) direction.
        self.dy = 0

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

        # Instance of the model that handles the world.
        self.world = World()

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

        # This call schedules the `update()` method to be called
        # TICKS_PER_SEC. This is the main game event loop.
        pyglet.clock.schedule_interval(self.update, 1.0 / TICKS_PER_SEC)

        self.inventory_scale = 2

        self.slot_hover_info = ItemInformationScreen()

        self.player_inventory = PlayerInventoryContainer()
        self.hotbar = HotbarContainer(self.player_inventory)
        self.hotbar.show_container()
        self.player_chat = Chat()

        self.moving_player_slot = Slot(
            self.player_inventory, (0, 0), on_update=self._update_moving_slot
        )

    def _update_moving_slot(self, slot, old_stack):
        if not slot.itemstack.is_empty():
            self.slot_hover_info.bind_to_slot(slot)
        else:
            self.slot_hover_info.bind_to_slot(None)

    def set_exclusive_mouse(self, exclusive: bool):
        """If `exclusive` is True, the game will capture the mouse, if False
        the game will ignore the mouse.

        """
        super(Window, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive
        self.strafe = [0, 0]

    def get_sight_vector(self) -> Vec3:
        """Returns the current line of sight vector indicating the direction
        the player is looking.

        """
        x, y = self.rotation
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return Vec3(dx, dy, dz)

    def get_motion_vector(self) -> tuple[float, float, float]:
        """Returns the current motion vector indicating the velocity of the
        player.

        Returns
        -------
        vector : tuple of len 3
            Tuple containing the velocity in x, y, and z respectively.

        """
        if any(self.strafe):
            x, y = self.rotation
            strafe = math.degrees(math.atan2(*self.strafe))
            y_angle = math.radians(y)
            x_angle = math.radians(x + strafe)
            if self.flying:
                m = math.cos(y_angle)
                dy = math.sin(y_angle)
                if self.strafe[1]:
                    # Moving left or right.
                    dy = 0.0
                    m = 1
                if self.strafe[0] > 0:
                    # Moving backwards.
                    dy *= -1
                # When you are flying up or down, you have less left and right
                # motion.
                dx = math.cos(x_angle) * m
                dz = math.sin(x_angle) * m
            else:
                dy = 0.0
                dx = math.cos(x_angle)
                dz = math.sin(x_angle)
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return dx, dy, dz

    def update(self, dt: float):
        """This method is scheduled to be called repeatedly by the pyglet
        clock.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        self.world.process_queue()
        sector = sectorize(self.position)
        if sector != self.sector:
            self.world.change_chunks(self.sector, sector)

            if self.sector is None:
                self.world.process_entire_queue()

            self.sector = sector
        m = 8
        dt = min(dt, 0.2)
        for _ in range(m):
            self._update(dt / m)

    def _update(self, dt: float):
        """Private implementation of the `update()` method. This is where most
        of the motion logic lives, along with gravity and collision detection.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        # walking
        speed = FLYING_SPEED if self.flying else WALKING_SPEED
        d = dt * speed  # distance covered this tick.
        dx, dy, dz = self.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d
        # gravity
        if not self.flying:
            # Update your vertical speed: if you are falling, speed up until you
            # hit terminal velocity; if you are jumping, slow down until you
            # start falling.
            self.dy -= dt * GRAVITY
            self.dy = max(self.dy, -TERMINAL_VELOCITY)
            dy += self.dy * dt

        # collisions
        x, y, z = self.position
        x, y, z = self.collide((x + dx, y + dy, z + dz), PLAYER_HEIGHT)
        self.position = Vec3(x, y, z)

    def collide(self, position: tuple[float, float, float], height: int):
        """Checks to see if the player at the given `position` and `height`
        is colliding with any blocks in the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check for collisions at.
        height : int or float
            The height of the player.

        Returns
        -------
        position : tuple of len 3
            The new position of the player taking into account collisions.

        """
        # How much overlap with a dimension of a surrounding block you need to
        # have to count as a collision. If 0, touching terrain at all counts as
        # a collision. If .49, you sink into the ground, as if walking through
        # tall grass. If >= .5, you'll fall through the ground.
        pad = 0.25
        p = list(position)
        np = normalize(position)
        for face in FACES:  # check all surrounding blocks
            for i in range(3):  # check each dimension independently
                if not face[i]:
                    continue
                # How much overlap you have with this dimension.
                d = (p[i] - np[i]) * face[i]
                if d < pad:
                    continue
                for dy in range(height):  # check each height
                    op = list(np)
                    op[1] -= dy
                    op[i] += face[i]
                    if tuple(op) not in self.world.get_or_create_chunk(op).blocks:
                        continue
                    p[i] -= (d - pad) * face[i]
                    if face == (0, -1, 0) or face == (0, 1, 0):
                        # You are colliding with the ground or ceiling, so stop
                        # falling / rising.
                        self.dy = 0
                    break

        return tuple(p)

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
            stack = self.player_inventory.get_selected_itemstack()

            vector = self.get_sight_vector()
            block, previous, block_raw = self.world.hit_test(self.position, vector)
            block_chunk = self.world.get_or_create_chunk(block) if block else None
            previous_chunk = (
                self.world.get_or_create_chunk(previous) if previous else None
            )

            if (
                block_chunk
                and block in block_chunk.blocks
                and block_chunk.blocks[block].on_block_interaction(
                    stack, button, modifiers
                )
            ):
                return

            if not stack.is_empty() and stack.item.on_block_interaction(
                stack, block_chunk.blocks.get(block, None), button, modifiers
            ):
                return

            if (button == mouse.RIGHT) or (
                (button == mouse.LEFT) and (modifiers & key.MOD_CTRL)
            ):
                # ON OSX, control + left click = right click.
                if previous and not stack.is_empty():
                    if b := stack.item.create_block_to_be_placed(stack):
                        self.world.add_block(
                            previous, b, block_added_parms=(block_raw,)
                        )
                        b.on_block_placed(stack, block)

            elif button == pyglet.window.mouse.LEFT and block:
                instance = block_chunk.blocks[block]

                if instance.BREAKABLE:
                    self.world.remove_block(block)

            elif button == pyglet.window.mouse.MIDDLE and block:
                instance = block_chunk.blocks[block]

                slot = self.player_inventory.find_item(instance.NAME)

                if slot is None:
                    itemstack = self.player_inventory.get_selected_itemstack()
                    self.player_inventory.get_selected_slot().set_stack(
                        ItemStack(instance.NAME)
                    )
                    if not itemstack.is_empty():
                        self.player_inventory.insert(itemstack)

                elif slot not in self.player_inventory.slots[:9]:
                    itemstack = self.player_inventory.get_selected_itemstack()
                    self.player_inventory.get_selected_slot().set_stack(slot.itemstack)
                    slot.set_stack(itemstack)

                else:
                    self.player_inventory.selected_slot = (
                        self.player_inventory.slots.index(slot)
                    )

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

            x, y = self.rotation
            x, y = x + dx * m, y + dy * m

            # y = max(-90.0, min(90.0, y))
            y = max(-89.9, min(89.9, y))

            self.rotation = (x, y)

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
                self.strafe[0] -= 1

            elif symbol == key.S:
                self.strafe[0] += 1

            elif symbol == key.A:
                self.strafe[1] -= 1

            elif symbol == key.D:
                self.strafe[1] += 1

            elif symbol == key.SPACE:
                if self.dy == 0:
                    self.dy = JUMP_SPEED

            elif symbol == key.T:
                self.player_chat.show_container()
                self.player_chat.ignore_next_t = True
                self.set_exclusive_mouse(False)
                return pyglet.event.EVENT_HANDLED

        if symbol == key.ESCAPE:
            for container in CONTAINER_STACK:
                container.on_close_with_escape()

            self.set_exclusive_mouse(not self.exclusive)

        elif symbol == key.E:
            if self.player_chat.open:
                pass
            elif self.player_inventory.open:
                self.set_exclusive_mouse(True)
                self.player_inventory.hide_container()
            else:
                self.set_exclusive_mouse(False)
                self.player_inventory.show_container()

        elif symbol == key.TAB:
            self.flying = not self.flying

        elif symbol in self.num_keys and self.exclusive:
            index = symbol - self.num_keys[0]
            self.player_inventory.selected_slot = index

    def on_text(self, text):
        for container in CONTAINER_STACK:
            if container.on_text(text):
                return pyglet.event.EVENT_HANDLED

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self.exclusive:
            self.player_inventory.selected_slot = int(
                (self.player_inventory.selected_slot - scroll_y) % 9
            )

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
                self.strafe[0] += 1
            elif symbol == key.S:
                self.strafe[0] -= 1
            elif symbol == key.A:
                self.strafe[1] += 1
            elif symbol == key.D:
                self.strafe[1] -= 1

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

    def set_3d(self):
        """Configure OpenGL to draw in 3d.3"""
        self.projection = Mat4.perspective_projection(
            self.aspect_ratio, z_near=0.1, z_far=100, fov=45
        )
        position = self.position
        vector = self.get_sight_vector()
        self.view = Mat4.look_at(position, position + vector, Vec3(0, 1, 0))
        glEnable(GL_DEPTH_TEST)

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
        self.draw_focused_block()
        self.set_2d()
        self.draw_label()
        self.draw_reticle()

        self.draw_inventories()
        self.player_chat.draw_chat_output(self)

    def draw_inventories(self):
        glClear(GL_DEPTH_BUFFER_BIT)

        for container in CONTAINER_STACK:
            self.set_2d_centered_for_inventory(container)
            container.draw(self)

        if any(container.SHOULD_DRAW_MOVING_SLOT for container in CONTAINER_STACK):
            self.set_2d_centered_for_inventory(self.player_inventory)

            self.moving_player_slot.update_position(
                self.player_inventory.window_to_relative_world(
                    (self.mouse_position[0] - 8, self.mouse_position[1] - 7),
                    self.get_size(),
                    self.inventory_scale,
                )
            )

            self.moving_player_slot.draw(self)

        self.slot_hover_info.draw(self)

    def draw_focused_block(self):
        """Draw black edges around the block that is currently under the
        crosshairs.

        """
        vector = self.get_sight_vector()

        if block := self.world.hit_test(self.position, vector)[0]:
            x, y, z = block
            vertex_data = cube_line_vertices(x, y, z, 0.51)
            self.focused_block.set_attribute_data("position", vertex_data)
            self.focused_block_batch.draw()

    def draw_label(self):
        """Draw the label in the top left of the screen."""
        x, y, z = self.position
        self.label.text = "%02d (%.2f, %.2f, %.2f) %d (%d)" % (
            pyglet.clock.get_frequency(),
            x,
            y,
            z,
            len(self.world.chunks),
            len(self.world.get_or_create_chunk(self.position).blocks),
        )
        self.label.draw()

    def draw_reticle(self):
        """Draw the crosshairs in the center of the screen."""
        self.reticle[0].draw()
        self.reticle[1].draw()
