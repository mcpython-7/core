from __future__ import annotations

import abc
import copy
import functools
import math
import random
import typing

import pyglet.graphics
from pyglet.gl import GL_TRIANGLES
from pyglet.math import Vec3, Vec2, Mat4, Vec4

from mcpython.resources.ResourceManager import ResourceManager
from mcpython.rendering.TextureAtlas import TextureAtlas, AtlasReference


_TEXTURE_ATLAS = TextureAtlas()


def _parse_stringfieid_blockstate(string: str) -> dict[str, str]:
    return (
        {item.split("=")[0]: item.split("=")[1] for item in string.split(",")}
        if string
        else {}
    )


def _try_resolve_texture(model: Model, element: dict, face: str) -> str | None:
    if face not in element["faces"]:
        return
    return model.resolve_texture_name(element["faces"][face]["texture"])


def _textured_cube(
    tex: AtlasReference, top: AtlasReference = None, bottom: AtlasReference = None
) -> list[float]:
    result = []
    base = tex.tex_coord()
    result.extend(top.tex_coord() if top else base)
    result.extend(bottom.tex_coord() if bottom else base)
    result.extend(base * 4)
    return result


FACE_ORDER = ["up", "down", "north", "east", "south", "west"]
FACE_ORDER_UV = ["up", "down", "east", "west", "north", "south"]


class Model:
    _MODEL_CACHE: dict[str, Model] = {"minecraft:builtin/generated": None}

    @classmethod
    def by_name(cls, name: str) -> Model:
        if name in cls._MODEL_CACHE:
            return cls._MODEL_CACHE[name]

        if ":" not in name:
            name = f"minecraft:{name}"

        if name in cls._MODEL_CACHE:
            return cls._MODEL_CACHE[name]

        file = "assets/{}/models/{}.json".format(*name.split(":"))
        data = ResourceManager.load_json(file)
        model = cls.by_data(name, data)
        cls._MODEL_CACHE[name] = model
        return model

    @classmethod
    def by_data(cls, name: str, data: dict) -> Model:
        model = cls(name)

        if "parent" in data:
            model.parent = cls.by_name(data["parent"])
            if model.parent is not None:
                model.elements = copy.deepcopy(model.parent.elements.copy())
                # this is a 'basic' copy to share the cache entries
                model.vertex_data_cache = model.parent.vertex_data_cache.copy()
                model.texture_table.update(model.parent.texture_table)

        if "textures" in data:
            model.texture_table.update(data["textures"])

        while f"layer{model.item_layer_count}" in model.texture_table:
            tex = model.resolve_texture_name(f"layer{model.item_layer_count}")
            if tex and ":" in tex:
                _TEXTURE_ATLAS.add_image_from_path(tex)
            model.item_layer_count += 1

        for _, __, faces, ___ in model.elements:
            faces[:] = [
                (
                    (
                        (
                            _TEXTURE_ATLAS.add_image_from_path(
                                model.resolve_texture_name(face[0])
                            )
                            if not face[1]
                            else (
                                _TEXTURE_ATLAS.add_image_from_path(
                                    model.resolve_texture_name(face[0])
                                ).uv_section(face[1])
                                if ":" in model.resolve_texture_name(face[0])
                                else model.resolve_texture_name(face[0])
                            )
                        )
                        if ":" in model.resolve_texture_name(face[0])
                        else (model.resolve_texture_name(face[0]), face[1])
                    )
                    if isinstance(face, tuple)
                    else face
                )
                for face in faces
            ]

        if "elements" in data:
            for element in data["elements"]:
                from_coord = Vec3(*element["from"]) / 16
                to_coord = Vec3(*element["to"]) / 16

                _faces = [
                    _try_resolve_texture(model, element, face) for face in FACE_ORDER
                ]
                uvs = [
                    tuple(
                        e / 16
                        for e in element["faces"]
                        .get(FACE_ORDER_UV[i], {})
                        .get("uv", [])
                    )
                    for i in range(6)
                ]

                faces = [
                    (
                        (
                            _TEXTURE_ATLAS.add_image_from_path(face)
                            if not uv
                            else _TEXTURE_ATLAS.add_image_from_path(face).uv_section(uv)
                        )
                        if face and ":" in face
                        else (face, uv)
                    )
                    for face, uv in zip(_faces, uvs)
                    if face is not None
                ]

                model.elements.append(
                    (
                        (from_coord + to_coord) / 2 - Vec3(0.5, 0.5, 0.5),
                        (to_coord - from_coord),
                        faces,
                        tuple(face is not None for face in _faces),
                    )
                )
                model.vertex_data_cache.append({})

        return model

    def __init__(self, name: str):
        self.parent_name: str | None = None
        self.parent: Model | None = None
        self.texture_table: dict[str, str] = {}

        self.elements: list[
            tuple[
                Vec3,
                Vec3,
                list[float | None] | list[AtlasReference | str | None],
                tuple[bool, ...],
            ]
        ] = []
        self.name = name
        self.texture_coordinates = None
        self.was_baked = False
        self.vertex_data_cache: list[dict[tuple[float, float, float], list[Vec3]]] = []
        self.item_layer_count = 0
        self.item_layers: list[pyglet.image.AbstractImage] = []

    def __repr__(self):
        return f"Model({self.name})"

    def resolve_texture_name(self, name: str | None) -> str | None:
        if not name:
            return name

        while True:
            if name[0] == "#":
                name = name[1:]

            if name not in self.texture_table:
                return name

            name = self.texture_table[name]

    def bake(self):
        if self.was_baked:
            return
        self.was_baked = True

        if self.parent:
            self.parent.bake()

        for _, __, textures, ___ in self.elements:
            if None in textures:
                continue

            tex = [
                (
                    reference.tex_coord()
                    if isinstance(reference, AtlasReference)
                    else (reference,)
                )
                for reference in textures
            ]
            textures.clear()
            textures.extend(sum(tex, ()))

        for i in range(self.item_layer_count):
            texture = _TEXTURE_ATLAS.add_image_from_path(
                self.resolve_texture_name(f"layer{i}")
            )
            self.item_layers.append(texture.get_texture())

    def get_rendering_data(
        self,
        extra: list[pyglet.graphics.vertexdomain.VertexList],
        position: tuple[int, int, int],
        rotation: tuple[float, float, float] = (0, 0, 0),
        flat_batch=None,
    ) -> tuple[int, list[float], list[float]]:
        v = Vec3(*position)
        count = 0
        vertex = []
        texture = []

        from mcpython.rendering.util import cube_vertices

        for i, (center, size, textures, enabled) in enumerate(self.elements):
            vertex_cache = self.vertex_data_cache[i]

            if rotation not in vertex_cache:
                rotation_matrix = Mat4.from_rotation(rotation[0], Vec3(1, 0, 0))
                rotation_matrix @= Mat4.from_rotation(rotation[1], Vec3(0, 1, 0))
                rotation_matrix @= Mat4.from_rotation(rotation[2], Vec3(0, 0, 1))

                vertex_data = cube_vertices(center, size / 2)
                vertex_data = sum(
                    (
                        [
                            Vec3(
                                (e := rotation_matrix @ Vec4(*element))[0],
                                e[1],
                                e[2],
                            )
                            for element in x
                        ]
                        for i, x in enumerate(vertex_data)
                        if enabled[i]
                    ),
                    [],
                )
                vertex_cache[rotation] = vertex_data
            else:
                vertex_data = vertex_cache[rotation]

            count += 6 * enabled.count(True)
            vertex_data = [vertex + v for vertex in vertex_data]
            vertex += sum(map(tuple, vertex_data), ())
            texture.extend(textures)

        if flat_batch and self.item_layer_count:
            for i in range(self.item_layer_count):
                # todo: creating sprites each time here seems a bit overkill, can we do better?
                sprite = pyglet.sprite.Sprite(self.item_layers[i], batch=flat_batch)
                extra.append(sprite)

        return count, vertex, texture

    def create_vertex_list(
        self,
        batch: pyglet.graphics.Batch,
        position: tuple[int, int, int],
        flat_batch=None,
    ):
        from mcpython.rendering.util import (
            DEFAULT_BLOCK_SHADER,
            DEFAULT_BLOCK_GROUP,
        )

        if not self.was_baked:
            self.bake()

        extra = []
        count, vertex_data, texture_data = self.get_rendering_data(
            extra, position, flat_batch=flat_batch
        )

        return [
            DEFAULT_BLOCK_SHADER.vertex_list(
                count,
                GL_TRIANGLES,
                batch,
                DEFAULT_BLOCK_GROUP,
                position=("f", vertex_data),
                tex_coords=("f", texture_data),
            )
        ] + extra


class BlockState:
    @classmethod
    def by_data(cls, data: dict | list) -> BlockState:
        data = data if isinstance(data, list) else [data]
        models = [
            (
                typing.cast(str, entry["model"]),
                None,
                entry.get("x", 0) / 180 * math.pi,
                entry.get("y", 0) / 180 * math.pi,
                0,
                entry.get("uvlock", False),
                entry.get("weight", 1),
            )
            for entry in data
        ]
        return cls(models)

    def __init__(
        self, models: list[tuple[str, Model | None, int, int, int, bool, int]]
    ):
        self.models = models

        if len(models) == 1:
            self.get_model = lambda _: self.models[0]
        else:
            weights = [m[-1] for m in self.models]
            self.get_model = lambda _: random.choices(self.models, weights, k=1)[0]

    def get_required_models(self) -> list[str]:
        return list(map(lambda e: e[0], self.models))

    def get_model(
        self, position: tuple[int, int, int]
    ) -> tuple[str, Model | None, int, int, int, bool, int]:
        raise RuntimeError

    def bake(self):
        self.models = [
            (name, model or Model.by_name(name), x, y, z, uvlock, weight)
            for name, model, x, y, z, uvlock, weight in self.models
        ]
        for _, model, *__ in self.models:
            model.bake()

    def get_rendering_data(
        self,
        extra: list[pyglet.graphics.vertexdomain.VertexList],
        position: tuple[int, int, int],
    ) -> tuple[int, list[float], list[float]]:
        name, model, x, y, z, uvlock, _ = self.get_model(position)
        return model.get_rendering_data(extra, position, (x, y, z))


class AbstractBlockStateCondition(abc.ABC):
    @classmethod
    def by_data(cls, data: dict) -> AbstractBlockStateCondition:
        return BlockStateConditionStateMatch(data)

    def applies(self, state: dict[str, str]) -> bool:
        raise NotImplementedError


class BlockStateConditionStateMatch(AbstractBlockStateCondition):
    def __init__(self, state: dict):
        self.state = state

    def applies(self, state: dict[str, str]) -> bool:
        return all(state[key] == value for key, value in self.state.items())


class BlockStateFile:
    _INSTANCES: list[BlockStateFile] = []

    @classmethod
    def bake_all(cls):
        from mcpython.rendering.util import update_texture_atlas_references

        for file in cls._INSTANCES:
            file.bake()

        update_texture_atlas_references()

    @classmethod
    def by_name(cls, name: str) -> BlockStateFile:
        """
        Returns the BlockStateFile instance for a certain 'name'
        of the form "<namespace>:<name>" loaded from the block state file
        "assets/<namespace>/blockstates/<name>.json"
        """

        file = "assets/{}/blockstates/{}.json".format(*name.split(":"))
        data = ResourceManager.load_json(file)
        return cls.by_data(name, data)

    @classmethod
    def by_data(cls, name: str, data: dict) -> BlockStateFile:
        instance = BlockStateFile(name)

        if "variants" in data:
            if "multipart" in data:
                raise ValueError(
                    f"cannot have both 'variants' and 'multipart' in block state file {name}"
                )

            for key, variant in data["variants"].items():
                instance.variants.append(
                    (_parse_stringfieid_blockstate(key), BlockState.by_data(variant))
                )

        elif "multipart" in data:
            for entry in data["multipart"]:
                instance.multipart.append(
                    (
                        (
                            AbstractBlockStateCondition.by_data(entry["when"])
                            if "when" in entry
                            else None
                        ),
                        BlockState.by_data(entry["apply"]),
                    )
                )

        return instance

    def __init__(self, name: str):
        self._INSTANCES.append(self)
        self.name = name

        self.variants: list[tuple[dict[str, str], BlockState]] = []
        self.multipart: list[tuple[AbstractBlockStateCondition, BlockState]] = []

    def bake(self):
        for _, state in self.variants:
            state.bake()

        for _, state in self.multipart:
            state.bake()

    def get_blockstates(self, state: dict[str, str]) -> typing.Iterator[BlockState]:
        if self.variants:
            for case, variant in self.variants:
                if all(state.get(key) == value for key, value in case.items()):
                    yield variant
                    return

            raise KeyError(
                f"block state: {self.name}, state: {state} (possible: {', '.join(map(lambda e: str(e[0]), self.variants))})"
            )

        for case, variant in self.multipart:
            if case is None or case.applies(state):
                yield variant

    def create_vertex_list(
        self,
        batch: pyglet.graphics.Batch,
        position: tuple[int, int, int],
        state: dict[str, str],
    ):
        from mcpython.rendering.util import (
            DEFAULT_BLOCK_SHADER,
            DEFAULT_BLOCK_GROUP,
        )

        count = 0
        vertex_data = []
        texture_data = []
        extra = []

        for blockstate in self.get_blockstates(state):
            c, v, t = blockstate.get_rendering_data(extra, position)
            count += c
            vertex_data += v
            texture_data += t

        return [
            DEFAULT_BLOCK_SHADER.vertex_list(
                count,
                GL_TRIANGLES,
                batch,
                DEFAULT_BLOCK_GROUP,
                position=("f", vertex_data),
                tex_coords=("f", texture_data),
            )
        ] + extra
