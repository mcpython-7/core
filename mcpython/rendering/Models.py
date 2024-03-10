from __future__ import annotations

import abc
import copy
import functools
import random
import typing

import pyglet.graphics
from pyglet.gl import GL_TRIANGLES
from pyglet.math import Vec3, Vec2

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


class Model:
    _MODEL_CACHE: dict[str, Model] = {}

    @classmethod
    def by_name(cls, name: str) -> Model:
        if name in cls._MODEL_CACHE:
            return cls._MODEL_CACHE[name]

        if ":" not in name:
            name = f"minecraft:{name}"

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
            model.elements = copy.deepcopy(model.parent.elements.copy())
            model.texture_table.update(model.parent.texture_table)

        if "textures" in data:
            model.texture_table.update(data["textures"])

        for _, __, faces in model.elements:
            faces[:] = [
                (
                    (
                        _TEXTURE_ATLAS.add_image_from_path(
                            model.resolve_texture_name(face)
                        )
                        if ":" in model.resolve_texture_name(face)
                        else model.resolve_texture_name(face)
                    )
                    if isinstance(face, str)
                    else face
                )
                for face in faces
            ]

        if "elements" in data:
            for element in data["elements"]:
                from_coord = Vec3(*element["from"]) / 16
                to_coord = Vec3(*element["to"]) / 16

                faces = [
                    _try_resolve_texture(model, element, "up"),
                    _try_resolve_texture(model, element, "down"),
                    _try_resolve_texture(model, element, "north"),
                    _try_resolve_texture(model, element, "east"),
                    _try_resolve_texture(model, element, "south"),
                    _try_resolve_texture(model, element, "west"),
                ]
                faces = [
                    (
                        _TEXTURE_ATLAS.add_image_from_path(face)
                        if face and ":" in face
                        else face
                    )
                    for face in faces
                ]

                model.elements.append(
                    (
                        (from_coord + to_coord) / 2 - Vec3(0.5, 0.5, 0.5),
                        (to_coord - from_coord),
                        faces,
                    )
                )

        return model

    def __init__(self, name: str):
        self.parent_name: str | None = None
        self.parent: Model | None = None
        self.texture_table: dict[str, str] = {}

        self.elements: list[
            tuple[
                Vec3, Vec3, list[float | None] | tuple[AtlasReference | str | None, ...]
            ]
        ] = []
        self.name = name
        self.texture_coordinates = None
        self.was_baked = False

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

        for _, __, textures in self.elements:
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

    def get_rendering_data(
        self, position: tuple[int, int, int]
    ) -> tuple[int, list[float], list[float]]:
        v = Vec3(*position)
        count = 0
        vertex = []
        texture = []

        from mcpython.rendering.util import cube_vertices

        for center, size, textures in self.elements:
            count += 36
            vertex += cube_vertices(v + center, size / 2)
            texture.extend(textures)

        return count, vertex, texture

    def create_vertex_list(
        self,
        batch: pyglet.graphics.Batch,
        position: tuple[int, int, int],
        offset: Vec2 = Vec2(0, 0),
    ):
        from mcpython.rendering.util import (
            DEFAULT_BLOCK_SHADER,
            DEFAULT_BLOCK_GROUP,
        )

        count, vertex_data, texture_data = self.get_rendering_data(position)

        return DEFAULT_BLOCK_SHADER.vertex_list(
            count,
            GL_TRIANGLES,
            batch,
            DEFAULT_BLOCK_GROUP,
            position=("f", vertex_data),
            tex_coords=("f", texture_data),
            render_offset=("f", tuple(offset) * count),
        )


class BlockState:
    @classmethod
    def by_data(cls, data: dict | list) -> BlockState:
        data = data if isinstance(data, list) else [data]
        models = [
            (
                typing.cast(str, entry["model"]),
                None,
                entry.get("x", 0),
                entry.get("y", 0),
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


class AbstractBlockStateCondition(abc.ABC):
    @classmethod
    def by_data(cls, data: dict) -> AbstractBlockStateCondition:
        raise NotImplementedError

    def applies(self, state: dict[str, str]) -> bool:
        raise NotImplementedError


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
                instance.multipart = (
                    (
                        AbstractBlockStateCondition.by_data(entry["when"])
                        if "when" in entry
                        else None
                    ),
                    BlockState.by_data(entry["apply"]),
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

    def get_models(
        self, position: tuple[int, int, int], state: dict[str, str]
    ) -> typing.Iterator[tuple[str, Model | None, int, int, int, bool, int]]:
        if self.variants:
            for case, variant in self.variants:
                if all(state.get(key) == value for key, value in case.items()):
                    yield variant.get_model(position)
                    return
            raise KeyError(f"block state: {self.name}, state: {state}")

        for case, variant in self.multipart:
            if case.applies(state):
                yield variant.get_model(position)

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
        for _, model, x, y, z, uvlock, __ in self.get_models(position, state):
            c, v, t = model.get_rendering_data(position)
            count += c
            vertex_data += v
            texture_data += t

        return DEFAULT_BLOCK_SHADER.vertex_list(
            count,
            GL_TRIANGLES,
            batch,
            DEFAULT_BLOCK_GROUP,
            position=("f", vertex_data),
            tex_coords=("f", texture_data),
        )
