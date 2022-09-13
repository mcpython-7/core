import io
import json
import os.path
import typing
from abc import ABC
import aiofiles
import aiofiles.os
from zipfile import ZipFile

import PIL.Image
import pyglet.image


class ResourceNotFoundException(Exception):
    pass


class AbstractResourcePath(ABC):
    async def setup(self):
        pass

    async def read_bytes(self, file: str) -> bytes:
        raise NotImplementedError

    async def walk(self, folder: str) -> typing.AsyncIterator[str]:
        raise NotImplementedError


class FolderResourcePath(AbstractResourcePath):
    def __init__(self, root: str):
        if not os.path.isdir(root):
            raise IOError(f"root folder {root} does not exist!")

        self.root = root

    async def read_bytes(self, file: str) -> bytes:
        full_file_path = os.path.join(self.root, file)

        if not os.path.isfile(full_file_path):
            raise ResourceNotFoundException(file)

        async with aiofiles.open(full_file_path, mode="rb") as f:
            return await f.read()

    async def walk(self, folder: str) -> typing.AsyncIterator[str]:
        for root, folders, files in os.walk(os.path.join(self.root, folder)):
            for file in files:
                yield os.path.join(root, file).removeprefix(self.root + "/")


class ArchiveResourcePath(AbstractResourcePath):
    def __init__(self, archive: str):
        self.path = archive
        self.archive = None

    async def setup(self):
        self.archive = ZipFile(self.path)

    async def read_bytes(self, file: str) -> bytes:
        return self.archive.read(file)

    async def walk(self, folder: str) -> typing.AsyncIterator[str]:
        for file in self.archive.namelist():
            if not file.endswith("/"):
                yield file


class ResourceManager:
    def __init__(self):
        self._paths: typing.List[ArchiveResourcePath] = []

    def register_path(self, path: ArchiveResourcePath):
        self._paths.append(path)

    async def setup(self):
        for path in self._paths:
            await path.setup()

    async def read_bytes(self, file: str) -> bytes:
        for path in self._paths:
            try:
                return await path.read_bytes(file)
            except ResourceNotFoundException:
                continue

        raise ResourceNotFoundException(file)

    async def read_json(self, file: str):
        return json.loads((await self.read_bytes(file)).decode("utf-8"))

    async def read_pillow_image(self, file: str) -> PIL.Image.Image:
        try:
            return PIL.Image.open(io.BytesIO(await self.read_bytes(file)))
        except:
            raise ValueError(file)

    async def read_pyglet_image(self, file: str) -> pyglet.image.AbstractImage:
        return pyglet.image.load(file, io.BytesIO(await self.read_bytes(file)))

    async def read_nbt(self, file: str):
        raise NotImplementedError


MANAGER = ResourceManager()
