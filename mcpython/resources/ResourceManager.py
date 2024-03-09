import io
import zipfile
import pathlib
import json
import PIL.Image
import pyglet


class AbstractResourceSource:
    def exists(self, file: str) -> bool:
        raise NotImplementedError()

    def load_raw(self, file: str) -> bytes:
        raise NotImplementedError()


class DirectoryResourceSource(AbstractResourceSource):
    def __init__(self, directory: str | pathlib.Path):
        self.directory = pathlib.Path(directory)

        if not self.directory.exists():
            self.directory.mkdir()

    def exists(self, file: str) -> bool:
        return self.directory.joinpath(file).exists()

    def load_raw(self, file: str) -> bytes:
        return self.directory.joinpath(file).read_bytes()


class ArchiveResourceSource(AbstractResourceSource):
    def __init__(self, path: str | pathlib.Path):
        self.path = path
        self.file = zipfile.ZipFile(path)
        self.exist = set(self.file.namelist())

    def exists(self, file: str) -> bool:
        return file in self.exist

    def load_raw(self, file: str) -> bytes:
        return self.file.read(file)


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
