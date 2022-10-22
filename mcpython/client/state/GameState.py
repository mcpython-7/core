import math

import pyglet
from pyglet.window import key
from pyglet.window import mouse

from mcpython.client.state.AbstractState import AbstractState
from mcpython.client.rendering.Window import WINDOW
from mcpython.world.block.BlockManagement import BLOCK_REGISTRY
from mcpython.world.block.BlockState import BlockState
from mcpython.world.RayCastingUtil import cast_into_world
from mcpython.world.World import WORLD


class WorldRenderingContainer:
    def __init__(self):
        self.normal_3d_batch = pyglet.graphics.Batch()

        self.overlay_batch = pyglet.graphics.Batch()


RENDERING_CONTAINER: WorldRenderingContainer = None


class GameState(AbstractState):
    NAME = "minecraft:game"

    def __init__(self):
        super().__init__()

        global RENDERING_CONTAINER
        self._rendering_container = RENDERING_CONTAINER = WorldRenderingContainer()

        self.position_label = pyglet.text.Label(color=(0, 0, 0, 255))

    async def setup(self):
        self.window_handler.subscribe("on_draw", self.on_draw)
        self.window_handler.subscribe("on_tick", self.on_tick)
        self.window_handler.subscribe("on_mouse_press", self.on_mouse_press)

        dimension = await WORLD.get_dimension("minecraft:overworld")

        blocks = list(sorted(BLOCK_REGISTRY._entries.values(), key=lambda e: e.NAME, reverse=True))
        block_with_states = sum(
            [
                [
                    BlockState(block).with_state(
                        state
                        if isinstance(state, dict)
                        else {
                            e.split("=")[0]: e.split("=")[1] for e in state.split(",")
                        }
                    )
                    for state in block.get_all_valid_block_states()
                ]
                for block in blocks
            ],
            [],
        )

        grid_size = math.ceil(math.sqrt(len(block_with_states)))

        for dx in range(grid_size):
            for dz in range(grid_size):
                if not block_with_states:
                    break

                await dimension.set_block(dx * 3, 0, dz * 3, block_with_states.pop())
            else:
                continue
            break

    async def on_draw(self, dt: float):
        WINDOW.set_3d_world_view()

        pyglet.gl.glEnable(pyglet.gl.GL_DEPTH_TEST)
        pyglet.gl.glEnable(pyglet.gl.GL_CULL_FACE)

        self._rendering_container.normal_3d_batch.draw()

        pyglet.gl.glClear(pyglet.gl.GL_DEPTH_BUFFER_BIT)

        WINDOW.set_2d()
        pyglet.gl.glDisable(pyglet.gl.GL_DEPTH_TEST)
        pyglet.gl.glDisable(pyglet.gl.GL_CULL_FACE)

        self._rendering_container.overlay_batch.draw()
        self.position_label.draw()

        pyglet.gl.glClear(pyglet.gl.GL_DEPTH_BUFFER_BIT)

    async def on_tick(self, dt: float):
        speed = 0.5 if not WINDOW.key_handler[key.LCTRL] else 2

        rotation = WORLD.current_render_rotation

        dx, dz = math.cos(rotation[0]), math.sin(rotation[0])

        self.position_label.text = "{} {} {} / {} {} / {} {}".format(
            *[
                round(e * 100) / 100
                for e in WORLD.current_render_position
                + WORLD.current_render_rotation
                + [dx, dz]
            ]
        )

        if WINDOW.key_handler[key.D]:
            WORLD.current_render_position[0] -= dx * dt * speed
            WORLD.current_render_position[2] -= dz * dt * speed
        elif WINDOW.key_handler[key.A]:
            WORLD.current_render_position[0] += dx * dt * speed
            WORLD.current_render_position[2] += dz * dt * speed

        if WINDOW.key_handler[key.W]:
            dx, dz = math.cos(rotation[0] + math.pi / 2), math.sin(
                rotation[0] + math.pi / 2
            )
            WORLD.current_render_position[0] -= dx * dt * speed
            WORLD.current_render_position[2] -= dz * dt * speed
        elif WINDOW.key_handler[key.S]:
            dx, dz = math.cos(rotation[0] - math.pi / 2), math.sin(
                rotation[0] - math.pi / 2
            )
            WORLD.current_render_position[0] -= dx * dt * speed
            WORLD.current_render_position[2] -= dz * dt * speed

        if WINDOW.key_handler[key.SPACE]:
            WORLD.current_render_position[1] += dt
        elif WINDOW.key_handler[key.LSHIFT]:
            WORLD.current_render_position[1] -= dt

        if WINDOW.key_handler[key.LEFT]:
            WORLD.current_render_rotation[0] += dt
        elif WINDOW.key_handler[key.RIGHT]:
            WORLD.current_render_rotation[0] -= dt

        if WINDOW.key_handler[key.UP]:
            WORLD.current_render_rotation[1] += dt
        elif WINDOW.key_handler[key.DOWN]:
            WORLD.current_render_rotation[1] -= dt

        WORLD.current_render_rotation[0] %= math.pi * 2
        WORLD.current_render_rotation[1] = max(
            min(WORLD.current_render_rotation[1], math.pi * 3 / 2), math.pi / 2
        )

    async def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        vector = WINDOW.get_sight_vector()
        dimension = await WORLD.get_dimension(
            "minecraft:overworld"
        )  # todo: make based on current player dim

        if button == mouse.RIGHT:
            # todo: add player as source
            result = await cast_into_world(
                dimension, WORLD.current_render_position, vector
            )

            if result is None:
                print("no target!")
                return

            blockstate, previous = result

            # todo: fill with data
            if not blockstate.on_player_interaction(
                None, None, button, modifiers, None
            ):
                await dimension.set_block(*previous, "minecraft:stone")
            else:
                print("handled!")
