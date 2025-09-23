from __future__ import annotations

import io
import os
import typing
import zipfile
import pathlib
import json
import PIL.Image
import pyglet

from mcpython.config import TMP


class AbstractResourceSource:
    def exists(self, file: str) -> bool:
        raise NotImplementedError()

    def load_raw(self, file: str) -> bytes:
        raise NotImplementedError()

    def list_directory(self, directory: str) -> typing.Iterator[str]:
        raise NotImplementedError


class DirectoryResourceSource(AbstractResourceSource):
    def __init__(self, directory: str | pathlib.Path):
        self.directory = pathlib.Path(directory)

        if not self.directory.exists():
            self.directory.mkdir()

    def exists(self, file: str) -> bool:
        return self.directory.joinpath(file).exists()

    def load_raw(self, file: str) -> bytes:
        return self.directory.joinpath(file).read_bytes()

    def list_directory(
        self, directory: str, no_duplicates=True
    ) -> typing.Iterator[str]:
        if not self.directory.joinpath(directory).exists():
            return

        yield from (
            f"{directory}/{file}"
            for file in os.listdir(self.directory.joinpath(directory))
        )


class ArchiveResourceSource(AbstractResourceSource):
    def __init__(self, path: str | pathlib.Path):
        self.path = path
        self.file = zipfile.ZipFile(path)
        self.exist = set(self.file.namelist())

    def exists(self, file: str) -> bool:
        return file in self.exist

    def load_raw(self, file: str) -> bytes:
        return self.file.read(file)

    def list_directory(
        self, directory: str, no_duplicates=True
    ) -> typing.Iterator[str]:
        for file in self.file.namelist():
            if file.startswith(f"{directory}/"):
                yield file


class _ResourceManager:
    def __init__(self):
        self.dynamic_source_list: list[AbstractResourceSource] = []
        self.static_source_list: list[AbstractResourceSource] = []

    def exists(self, file: str) -> bool:
        if ".." in file:
            raise IOError
        return any(source.exists(file) for source in self.dynamic_source_list) or any(
            source.exists(file) for source in self.static_source_list
        )

    def load_raw(self, file: str) -> bytes:
        if ".." in file:
            raise IOError

        for source in self.dynamic_source_list:
            if source.exists(file):
                return source.load_raw(file)

        for source in self.static_source_list:
            if source.exists(file):
                return source.load_raw(file)

        raise FileNotFoundError(file)

    def load_text(self, file: str, encoding="utf-8") -> str:
        return self.load_raw(file).decode(encoding)

    def load_json(
        self, file: str, encoding="utf-8"
    ) -> dict | list | float | int | str | None:
        return json.loads(self.load_raw(file).decode(encoding))

    def load_pillow_image(self, file: str) -> PIL.Image.Image:
        stream = io.BytesIO(self.load_raw(file))
        return PIL.Image.open(stream)

    def load_pyglet_image(self, file: str) -> pyglet.image.AbstractImage:
        stream = io.BytesIO(self.load_raw(file))
        return pyglet.image.load(file, stream)

    def load_image(self, file: str) -> ImageWrapper:
        data = self.load_raw(file)
        return ImageWrapper(file, data)

    def list_directory(
        self, directory: str, no_duplicates=True
    ) -> typing.Iterator[str]:
        if ".." in directory:
            raise ValueError(f"invalid directory: {repr(directory)}")

        if no_duplicates:
            yielded = set()

            for source in self.dynamic_source_list + self.static_source_list:
                generator = source.list_directory(directory)

                for entry in generator:
                    if entry in yielded:
                        continue
                    yielded.add(entry)
                    yield entry
        else:
            for source in self.dynamic_source_list + self.static_source_list:
                yield from source.list_directory(directory)


class ImageWrapper:
    def __init__(
        self,
        file: str,
        data: bytes = None,
        pyglet_image: pyglet.image.AbstractImage = None,
        pillow_image: PIL.Image.Image = None,
    ):
        self._pillow_image = pillow_image
        self._pyglet_image = pyglet_image
        self.file = file
        self._data = data

    def get_region(self, start: tuple[int, int], end: tuple[int, int]) -> ImageWrapper:
        image = self.to_pillow().crop(start + end)
        image.save(f"{TMP}/tmp.png")
        return ImageWrapper(self.file, pillow_image=image)

    def get_data(self) -> bytes:
        if not self._data:
            buffer = io.BytesIO()
            buffer.name = self.file
            if self._pyglet_image:
                self._pyglet_image.save(self.file, buffer)
            else:
                self._pillow_image.save(buffer)
            self._data = buffer.getvalue()
        return self._data

    def to_pyglet(self) -> pyglet.image.AbstractImage:
        if not self._pyglet_image:
            self._pyglet_image = pyglet.image.load(
                self.file, io.BytesIO(self.get_data())
            )

        return self._pyglet_image

    def to_pillow(self) -> PIL.Image.Image:
        if not self._pillow_image:
            self._pillow_image = PIL.Image.open(io.BytesIO(self.get_data()))

        return self._pillow_image


ResourceManager = _ResourceManager()
ResourceManager.static_source_list.append(
    ArchiveResourceSource(
        pathlib.Path(__file__).parent.parent.parent.joinpath("cache/assets.zip")
    )
)
ResourceManager.static_source_list.append(
    DirectoryResourceSource(
        pathlib.Path(__file__).parent.parent.parent.joinpath("cache/temp")
    )
)
ResourceManager.static_source_list.append(
    DirectoryResourceSource(pathlib.Path(__file__).parent.parent.parent)
)
