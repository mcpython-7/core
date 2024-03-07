from __future__ import annotations

import math
import random
import time
import typing

from collections import deque

import pyglet.graphics.shader
from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.math import Mat4, Vec3
from pyglet.window import key, mouse
import pyglet.model.codecs.obj

from mcpython.world.blocks.AbstractBlock import (
    AbstractBlock,
    GrassBlock,
    Sand,
    Bricks,
    Stone,
)

pyglet.image.Texture.default_min_filter = GL_NEAREST
pyglet.image.Texture.default_mag_filter = GL_NEAREST

pyglet.resource.path.append("../cache/assets.zip")

TICKS_PER_SEC = 60

# Size of sectors used to ease block loading.
SECTOR_SIZE = 16

WALKING_SPEED = 5
FLYING_SPEED = 15

GRAVITY = 20.0
MAX_JUMP_HEIGHT = 1.0  # About the height of a block.
# To derive the formula for calculating jump speed, first solve
#    v_t = v_0 + a * t
# for the time at which you achieve maximum height, where a is the acceleration
# due to gravity and v_t = 0. This gives:
#    t = - v_0 / a
# Use t and the desired MAX_JUMP_HEIGHT to solve for v_0 (jump speed) in
#    s = s_0 + v_0 * t + (a * t^2) / 2
JUMP_SPEED = math.sqrt(2 * GRAVITY * MAX_JUMP_HEIGHT)
TERMINAL_VELOCITY = 50

PLAYER_HEIGHT = 2

default_vert_src = """#version 330 core
in vec3 position;
in vec2 tex_coords;

out vec2 texture_coords;
out vec3 vertex_position;

uniform WindowBlock
{
    mat4 projection;
    mat4 view;
} window;

uniform mat4 model;

void main()
{
    vec4 pos = window.view * model * vec4(position, 1.0);
    gl_Position = window.projection * pos;

    vertex_position = pos.xyz;
    texture_coords = tex_coords;
}
"""
default_frag_src = """#version 330 core
in vec2 texture_coords;
in vec3 vertex_position;
out vec4 final_colors;

uniform sampler2D our_texture;

void main()
{
    final_colors = (texture(our_texture, texture_coords));
}
"""
shader = pyglet.gl.current_context.create_program(
    (default_vert_src, "vertex"), (default_frag_src, "fragment")
)

matgroup = pyglet.model.TexturedMaterialGroup(
    pyglet.model.Material(
        "XY",
        [1.0, 1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0, 1.0],
        [0.0, 0.0, 0.0, 1.0],
        100,
        "texture.png",
    ),
    shader,
    pyglet.resource.texture("texture.png"),
)
matgroup_black_line = pyglet.graphics.ShaderGroup(pyglet.graphics.get_default_shader())


def cube_vertices(x: float, y: float, z: float, n: float) -> list[float]:
    """Return the vertices of the cube at position x, y, z with size 2*n."""
    # fmt: off
    return [
        # Top
        x-n, y+n, z-n, x-n, y+n, z+n, x+n, y+n, z+n,  # Triangle 1
        x-n, y+n, z-n, x+n, y+n, z+n, x+n, y+n, z-n,  # Triangle 2

        # Bottom
        x-n, y-n, z-n, x+n, y-n, z-n, x+n, y-n, z+n,  # Triangle 1
        x-n, y-n, z-n, x+n, y-n, z+n, x-n, y-n, z+n,  # Triangle 2

        # Left
        x-n, y-n, z-n, x-n, y-n, z+n, x-n, y+n, z+n,  # Triangle 1
        x-n, y-n, z-n, x-n, y+n, z+n, x-n, y+n, z-n,  # Triangle 2

        # Right
        x+n, y-n, z+n, x+n, y-n, z-n, x+n, y+n, z-n,  # Triangle 1
        x+n, y-n, z+n, x+n, y+n, z-n, x+n, y+n, z+n,  # Triangle 2

        # Front
        x-n, y-n, z+n, x+n, y-n, z+n, x+n, y+n, z+n,  # Triangle 1
        x-n, y-n, z+n, x+n, y+n, z+n, x-n, y+n, z+n,  # Triangle 2

        # Back
        x+n, y-n, z-n, x-n, y-n, z-n, x-n, y+n, z-n,  # Triangle 1
        x+n, y-n, z-n, x-n, y+n, z-n, x+n, y+n, z-n   # Triangle 2
    ]
    # fmt: on


def cube_line_vertices(x: float, y: float, z: float, n: float) -> list[float]:
    """Return the vertices of the cube at position x, y, z with size 2*n."""
    # fmt: off
    return [
        # Top
        x-n, y+n, z-n, x-n, y+n, z+n,  # Line 1
        x-n, y+n, z+n, x+n, y+n, z+n,  # Line 2
        x+n, y+n, z+n, x+n, y+n, z-n,  # Line 3
        x+n, y+n, z-n, x-n, y+n, z-n,  # Line 4

        # Bottom
        x-n, y-n, z-n, x-n, y-n, z+n,  # Line 1
        x-n, y-n, z+n, x+n, y-n, z+n,  # Line 2
        x+n, y-n, z+n, x+n, y-n, z-n,  # Line 3
        x+n, y-n, z-n, x-n, y-n, z-n,  # Line 4

        # Vertical lines connecting top and bottom
        x-n, y+n, z-n, x-n, y-n, z-n,  # Line 1
        x-n, y+n, z+n, x-n, y-n, z+n,  # Line 2
        x+n, y+n, z+n, x+n, y-n, z+n,  # Line 3
        x+n, y+n, z-n, x+n, y-n, z-n   # Line 4
    ]
    # fmt: on


TEXTURE_PATH = "texture.png"


FACES = [
    (0, 1, 0),
    (0, -1, 0),
    (-1, 0, 0),
    (1, 0, 0),
    (0, 0, 1),
    (0, 0, -1),
]


def normalize(position: tuple[float, float, float]) -> tuple[int, int, int]:
    """Accepts `position` of arbitrary precision and returns the block
    containing that position.

    Parameters
    ----------
    position : tuple of len 3

    Returns
    -------
    block_position : tuple of ints of len 3

    """
    x, y, z = position
    x, y, z = (int(round(x)), int(round(y)), int(round(z)))
    return x, y, z


def sectorize(position: tuple[float, float, float]) -> tuple[int, int]:
    """Returns a tuple representing the sector for the given `position`.

    Parameters
    ----------
    position : tuple of len 3

    Returns
    -------
    sector : tuple of len 3

    """
    x, y, z = normalize(position)
    x, y, z = x // SECTOR_SIZE, y // SECTOR_SIZE, z // SECTOR_SIZE
    return x, z


class World:

    def __init__(self):

        # A Batch is a collection of vertex lists for batched rendering.
        self.batch = pyglet.graphics.Batch()

        # A TextureGroup manages an OpenGL texture.
        self.group = TextureGroup(image.load(TEXTURE_PATH).get_texture())

        # A mapping from position to the texture of the block at that position.
        # This defines all the blocks that are currently in the world.
        self.world: dict[tuple[int, int, int], AbstractBlock] = {}

        # Mapping from sector to a list of positions inside that sector.
        self.sectors: dict[tuple[int, int], list[tuple[int, int, int]]] = {}

        # Simple function queue implementation. The queue is populated with
        # _show_block() and _hide_block() calls
        self.queue = deque()

        self._initialize()

    def _initialize(self):
        """Initialize the world by placing all the blocks."""
        n = 100  # 1/2 width and height of world
        s = 1  # step size
        y = 0  # initial y height
        for x in range(-n, n + 1, s):
            for z in range(-n, n + 1, s):
                # create a layer stone a grass everywhere.
                self.add_block((x, y - 2, z), GrassBlock, immediate=False)
                self.add_block((x, y - 3, z), Stone, immediate=False)
                if x in (-n, n) or z in (-n, n):
                    # create outer walls.
                    for dy in range(-2, 3):
                        self.add_block((x, y + dy, z), Stone, immediate=False)

        # generate the hills randomly
        o = n - 10
        for _ in range(120):
            a = random.randint(-o, o)  # x position of the hill
            b = random.randint(-o, o)  # z position of the hill
            c = -1  # base of the hill
            h = random.randint(1, 6)  # height of the hill
            s = random.randint(4, 8)  # 2 * s is the side length of the hill
            d = 1  # how quickly to taper off the hills
            t = random.choice([GrassBlock, Sand, Bricks])
            for y in range(c, c + h):
                for x in range(a - s, a + s + 1):
                    for z in range(b - s, b + s + 1):
                        if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
                            continue
                        if (x - 0) ** 2 + (z - 0) ** 2 < 5**2:
                            continue
                        self.add_block((x, y, z), t, immediate=False)
                s -= d  # decrement side length so hills taper off

    def hit_test(
        self,
        position: tuple[int, int, int],
        vector: tuple[float, float, float],
        max_distance=8,
    ) -> tuple[tuple[int, int, int], tuple[int, int, int]] | tuple[None, None]:
        """Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return None, None.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check visibility from.
        vector : tuple of len 3
            The line of sight vector.
        max_distance : int
            How many blocks away to search for a hit.

        """
        m = 8
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in range(max_distance * m):
            key = normalize((x, y, z))
            if key != previous and key in self.world:
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None

    def exposed(self, position: tuple[int, int, int]) -> bool:
        """Returns False is given `position` is surrounded on all 6 sides by
        blocks, True otherwise.

        """
        x, y, z = position
        for dx, dy, dz in FACES:
            if (x + dx, y + dy, z + dz) not in self.world:
                return True
        return False

    def add_block(
        self,
        position: tuple[int, int, int],
        block_type: type[AbstractBlock],
        immediate=True,
    ):
        """Add a block with the given `texture` and `position` to the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to add.
        block_type :
            The block type to use
        immediate : bool
            Whether or not to draw the block immediately.

        """
        if position in self.world:
            self.remove_block(position, immediate)

        instance = block_type(position)
        self.world[position] = instance
        self.sectors.setdefault(sectorize(position), []).append(position)
        if immediate:
            if self.exposed(position):
                self.show_block(instance)
            self.check_neighbors(position)

    def remove_block(self, position: tuple[int, int, int], immediate=True):
        """Remove the block at the given `position`.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to remove.
        immediate : bool
            Whether or not to immediately remove block from canvas.

        """
        instance = self.world[position]
        del self.world[position]
        self.sectors[sectorize(position)].remove(position)
        if immediate:
            if instance.shown:
                self.hide_block(instance)
            self.check_neighbors(position)

    def check_neighbors(self, position: tuple[int, int, int]):
        """Check all blocks surrounding `position` and ensure their visual
        state is current. This means hiding blocks that are not exposed and
        ensuring that all exposed blocks are shown. Usually used after a block
        is added or removed.

        """
        x, y, z = position
        for dx, dy, dz in FACES:
            key = (x + dx, y + dy, z + dz)
            if key not in self.world:
                continue
            instance = self.world[key]
            if self.exposed(key):
                if not instance.shown:
                    self.show_block(instance)
            else:
                if instance.shown:
                    self.hide_block(instance)

    def show_block(self, instance: AbstractBlock, immediate=True):
        """Show the block at the given `position`. This method assumes the
        block has already been added with add_block()

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        immediate : bool
            Whether or not to show the block immediately.

        """
        instance.shown = True
        if immediate:
            self._show_block(instance)
        else:
            self._enqueue(self._show_block, instance)

    def _show_block(self, instance: AbstractBlock):
        """Private implementation of the `show_block()` method.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        instance:
            The block instance

        """
        x, y, z = instance.position
        vertex_data = cube_vertices(x, y, z, 0.5)
        texture_data = list(instance.TEXTURE_COORDINATES)
        vertex = shader.vertex_list(
            36,
            GL_TRIANGLES,
            self.batch,
            matgroup,
            position=("f", vertex_data),
            tex_coords=("f", texture_data),
        )
        instance.vertex_data = vertex

    def hide_block(self, instance: AbstractBlock, immediate=True):
        """Hide the block at the given `position`. Hiding does not remove the
        block from the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to hide.
        immediate : bool
            Whether or not to immediately remove the block from the canvas.

        """
        instance.shown = False
        if immediate:
            self._hide_block(instance)
        else:
            self._enqueue(self._hide_block, instance)

    def _hide_block(self, instance: AbstractBlock):
        """Private implementation of the 'hide_block()` method."""
        instance.vertex_data.delete()
        instance.vertex_data = None

    def show_sector(self, sector: tuple[int, int]):
        """Ensure all blocks in the given sector that should be shown are
        drawn to the canvas.

        """
        for position in self.sectors.get(sector, []):
            instance = self.world[position]
            if not instance.shown and self.exposed(position):
                self.show_block(instance, False)

    def hide_sector(self, sector: tuple[int, int]):
        """Ensure all blocks in the given sector that should be hidden are
        removed from the canvas.

        """
        for position in self.sectors.get(sector, []):
            instance = self.world[position]
            if instance.shown:
                self.hide_block(instance, False)

    def change_sectors(self, before: tuple[int, int], after: tuple[int, int]):
        """Move from sector `before` to sector `after`. A sector is a
        contiguous x, y sub-region of world. Sectors are used to speed up
        world rendering.

        """
        before_set: set[tuple[int, int]] = set()
        after_set: set[tuple[int, int]] = set()
        pad = 4
        for dx in range(-pad, pad + 1):
            for dy in [0]:  # range(-pad, pad + 1):
                for dz in range(-pad, pad + 1):
                    if dx**2 + dy**2 + dz**2 > (pad + 1) ** 2:
                        continue
                    if before:
                        x, z = before
                        before_set.add((x + dx, z + dz))
                    if after:
                        x, z = after
                        after_set.add((x + dx, z + dz))

        show = after_set - before_set
        hide = before_set - after_set
        for sector in show:
            self.show_sector(sector)
        for sector in hide:
            self.hide_sector(sector)

    def _enqueue(self, func: typing.Callable, *args):
        """Add `func` to the internal queue."""
        self.queue.append((func, args))

    def _dequeue(self):
        """Pop the top function from the internal queue and call it."""
        func, args = self.queue.popleft()
        func(*args)

    def process_queue(self):
        """Process the entire queue while taking periodic breaks. This allows
        the game loop to run smoothly. The queue contains calls to
        _show_block() and _hide_block() so this method should be called if
        add_block() or remove_block() was called with immediate=False

        """
        start = time.perf_counter()
        while self.queue and time.perf_counter() - start < 1.0 / TICKS_PER_SEC:
            self._dequeue()

    def process_entire_queue(self):
        """Process the entire queue with no breaks."""
        while self.queue:
            self._dequeue()


class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)

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
        self.position = (0, 0, 0)

        # First element is rotation of the player in the x-z plane (ground
        # plane) measured from the z-axis down. The second is the rotation
        # angle from the ground plane up. Rotation is in degrees.
        #
        # The vertical plane rotation ranges from -90 (looking straight down) to
        # 90 (looking straight up). The horizontal rotation range is unbounded.
        self.rotation = (0, 0)

        # Which sector the player is currently in.
        self.sector = None

        # The crosshairs at the center of the screen.
        self.reticle: tuple[pyglet.shapes.Line, pyglet.shapes.Line] | None = None
        self.focused_block_batch = pyglet.graphics.Batch()
        self.focused_block = pyglet.graphics.get_default_shader().vertex_list(
            24,
            GL_LINES,
            self.focused_block_batch,
            matgroup_black_line,
            position=("f", cube_line_vertices(0, 0, 0, 0.51)),
            colors=("f", (0, 0, 0, 255) * 24),
        )

        # Velocity in the y (upward) direction.
        self.dy = 0

        # A list of blocks the player can place. Hit num keys to cycle.
        self.inventory = [Bricks, GrassBlock, Sand]

        # The current block the user can place. Hit num keys to cycle.
        self.block = self.inventory[0]

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
            key._0,
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

    def set_exclusive_mouse(self, exclusive: bool):
        """If `exclusive` is True, the game will capture the mouse, if False
        the game will ignore the mouse.

        """
        super(Window, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive

    def get_sight_vector(self) -> tuple[float, float, float]:
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
        return dx, dy, dz

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
            self.world.change_sectors(self.sector, sector)
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
        self.position = (x, y, z)

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
                    if tuple(op) not in self.world.world:
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
            vector = self.get_sight_vector()
            block, previous = self.world.hit_test(self.position, vector)

            if (button == mouse.RIGHT) or (
                (button == mouse.LEFT) and (modifiers & key.MOD_CTRL)
            ):

                # ON OSX, control + left click = right click.
                if previous:
                    self.world.add_block(previous, self.block)

            elif button == pyglet.window.mouse.LEFT and block:
                instance = self.world.world[block]

                if instance.BREAKABLE:
                    self.world.remove_block(block)

        else:
            self.set_exclusive_mouse(True)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
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
            y = max(-90, min(90, y))
            self.rotation = (x, y)

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
        elif symbol == key.ESCAPE:
            self.set_exclusive_mouse(False)
        elif symbol == key.TAB:
            self.flying = not self.flying
        elif symbol in self.num_keys:
            index = (symbol - self.num_keys[0]) % len(self.inventory)
            self.block = self.inventory[index]

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

    def set_2d(self):
        """Configure OpenGL to draw in 2d."""
        width, height = self.get_size()
        self.projection = Mat4.orthogonal_projection(0, width, 0, height, -255, 255)
        self.view = Mat4()
        glDisable(GL_DEPTH_TEST)

    def set_3d(self):
        """Configure OpenGL to draw in 3d.3"""
        self.projection = Mat4.perspective_projection(
            self.aspect_ratio, z_near=0.1, z_far=100, fov=45
        )
        position = Vec3(*self.position)
        vector = Vec3(*self.get_sight_vector())
        self.view = Mat4.look_at(position, position + vector, Vec3(0, 1, 0))
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

    def draw_focused_block(self):
        """Draw black edges around the block that is currently under the
        crosshairs.

        """
        vector = self.get_sight_vector()
        block = self.world.hit_test(self.position, vector)[0]
        if block:
            x, y, z = block
            vertex_data = cube_line_vertices(x, y, z, 0.51)
            self.focused_block.set_attribute_data("position", vertex_data)
            self.focused_block_batch.draw()

    def draw_label(self):
        """Draw the label in the top left of the screen."""
        x, y, z = self.position
        self.label.text = "%02d (%.2f, %.2f, %.2f) %d" % (
            pyglet.clock.get_frequency(),
            x,
            y,
            z,
            len(self.world.world),
        )
        self.label.draw()

    def draw_reticle(self):
        """Draw the crosshairs in the center of the screen."""
        self.reticle[0].draw()
        self.reticle[1].draw()


def setup_fog():
    """Configure the OpenGL fog properties.
    todo
    """
    # # Enable fog. Fog "blends a fog color with each rasterized pixel fragment's
    # # post-texturing color."
    # glEnable(GL_FOG)
    # # Set the fog color.
    # glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1))
    # # Say we have no preference between rendering speed and quality.
    # glHint(GL_FOG_HINT, GL_DONT_CARE)
    # # Specify the equation used to compute the blending factor.
    # glFogi(GL_FOG_MODE, GL_LINEAR)
    # # How close and far away fog starts and ends. The closer the start and end,
    # # the denser the fog in the fog range.
    # glFogf(GL_FOG_START, 20.0)
    # glFogf(GL_FOG_END, 60.0)


def setup():
    """Basic OpenGL configuration."""
    # Set the color of "clear", i.e. the sky, in rgba.
    glClearColor(0.5, 0.69, 1.0, 1)
    # Enable culling (not rendering) of back-facing facets -- facets that aren't
    # visible to you.
    glEnable(GL_CULL_FACE)
    # Set the texture minification/magnification function to GL_NEAREST (nearest
    # in Manhattan distance) to the specified texture coordinates. GL_NEAREST
    # "is generally faster than GL_LINEAR, but it can produce textured images
    # with sharper edges because the transition between texture elements is not
    # as smooth."
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    setup_fog()


def main():
    window = Window(width=800, height=600, caption="Pyglet", resizable=True)
    # Hide the mouse cursor and prevent the mouse from leaving the window.
    window.set_exclusive_mouse(True)
    setup()
    pyglet.app.run()


if __name__ == "__main__":
    main()
