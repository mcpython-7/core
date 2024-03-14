from __future__ import annotations

import io
import typing
from abc import ABC
import struct


_INT8 = struct.Struct("!b")
_UINT8 = struct.Struct("!c")
_INT16 = struct.Struct("!h")
_UINT16 = struct.Struct("!H")
_INT32 = struct.Struct("!i")
_UINT32 = struct.Struct("!I")
_INT64 = struct.Struct("!l")
_UINT64 = struct.Struct("!L")
_F16 = struct.Struct("!e")
_F32 = struct.Struct("!f")
_F64 = struct.Struct("!d")


class ReadBuffer:
    def __init__(self, source: bytes | io.BytesIO):
        self.source = source if isinstance(source, io.BytesIO) else io.BytesIO(source)

    def read_singleton_struct(self, entry: struct.Struct) -> typing.Any:
        return entry.unpack(self.source.read(entry.size))[0]

    def read_int8(self) -> int:
        pack = _INT8
        data = self.source.read(pack.size)
        return pack.unpack(data)[0]

    def read_uint8(self) -> int:
        pack = _UINT8
        data = self.source.read(pack.size)
        return pack.unpack(data)[0]

    def read_int16(self) -> int:
        pack = _INT16
        data = self.source.read(pack.size)
        return pack.unpack(data)[0]

    def read_uint16(self) -> int:
        pack = _UINT16
        data = self.source.read(pack.size)
        return pack.unpack(data)[0]

    def read_int32(self) -> int:
        pack = _INT32
        data = self.source.read(pack.size)
        return pack.unpack(data)[0]

    def read_uint32(self) -> int:
        pack = _UINT32
        data = self.source.read(pack.size)
        return pack.unpack(data)[0]

    def read_int64(self) -> int:
        pack = _INT64
        data = self.source.read(pack.size)
        return pack.unpack(data)[0]

    def read_uint64(self) -> int:
        pack = _UINT64
        data = self.source.read(pack.size)
        return pack.unpack(data)[0]

    def read_f16(self) -> float:
        pack = _F16
        data = self.source.read(pack.size)
        return pack.unpack(data)[0]

    def read_f32(self) -> float:
        pack = _F32
        data = self.source.read(pack.size)
        return pack.unpack(data)[0]

    def read_f64(self) -> float:
        pack = _F64
        data = self.source.read(pack.size)
        return pack.unpack(data)[0]

    def read_string(self, size_item: struct.Struct = _UINT16, encoding="utf-8") -> str:
        size = size_item.unpack(self.source.read(size_item.size))[0]
        return self.source.read(size).decode(encoding)


class WriteBuffer:
    def __init__(self, target: io.BytesIO = None):
        self.target = target or io.BytesIO()

    def write_singleton_struct(self, entry: struct.Struct, value):
        self.target.write(entry.pack(value))
        return self

    def write_int8(self, value: int) -> typing.Self:
        self.target.write(_INT8.pack(value))
        return self

    def write_uint8(self, value: int) -> typing.Self:
        self.target.write(_UINT8.pack(value))
        return self

    def write_int16(self, value: int) -> typing.Self:
        self.target.write(_INT16.pack(value))
        return self

    def write_uint16(self, value: int) -> typing.Self:
        self.target.write(_UINT16.pack(value))
        return self

    def write_int32(self, value: int) -> typing.Self:
        self.target.write(_INT32.pack(value))
        return self

    def write_uint32(self, value: int) -> typing.Self:
        self.target.write(_UINT32.pack(value))
        return self

    def write_int64(self, value: int) -> typing.Self:
        self.target.write(_INT64.pack(value))
        return self

    def write_uint64(self, value: int) -> typing.Self:
        self.target.write(_UINT64.pack(value))
        return self

    def write_f16(self, value: float) -> typing.Self:
        self.target.write(_F16.pack(value))
        return self

    def write_f32(self, value: float) -> typing.Self:
        self.target.write(_F32.pack(value))
        return self

    def write_f64(self, value: float) -> typing.Self:
        self.target.write(_F64.pack(value))
        return self

    def write_string(
        self, string: str, size_item: struct.Struct = _UINT32, encoding="utf8"
    ) -> typing.Self:
        d = string.encode(encoding)
        self.target.write(size_item.pack(len(d)))
        self.target.write(d)
        return self

    def get_data(self):
        return self.target.read()


class WriteReadBuffer(ReadBuffer, WriteBuffer):
    """
    A special buffer for direct write/read in the same buffer instance
    """

    def __init__(self):
        buffer = io.BytesIO()
        super(ReadBuffer, self).__init__(buffer)
        super(WriteBuffer, self).__init__(buffer)


# Internal array for storing what classes can be serialized in what way
_BUFFER_SERIALIZABLE_ARRAY: list[type[IBufferSerializable]] = []


class AbstractDataFixer(ABC):
    def apply(
        self, read_buffer: ReadBuffer, write_buffer: WriteBuffer, context=None
    ) -> int:
        """
        Applies this datafixer on the read_buffer and writes into the write_buffer instance.
        'context' is the optional context object the data belongs to

        Must return the new 'version' of the data
        """
        raise NotImplementedError


class IBufferSerializable(ABC):
    @classmethod
    def __init_subclass__(cls) -> None:
        if cls.decode != IBufferSerializable.decode:
            _BUFFER_SERIALIZABLE_ARRAY.append(cls)

    @classmethod
    def decode(cls, buffer: ReadBuffer):
        raise NotImplementedError

    def encode(self, buffer: WriteBuffer):
        raise NotImplementedError


class IBufferSerializableWithVersion(IBufferSerializable, ABC):
    VERSION = 0
    _VERSION_SIZE = _UINT16
    DATA_FIXERS: dict[int, AbstractDataFixer] = {}

    @classmethod
    def decode_datafixable(cls, read_buffer: ReadBuffer, context=None) -> ReadBuffer:
        version = read_buffer.read_singleton_struct(cls._VERSION_SIZE)

        while version < cls.VERSION:
            fixer = cls.DATA_FIXERS.get(version)
            if fixer is None:
                raise RuntimeError(
                    f"Cannot fix stream from {cls} in version {version} to the current version, {cls.VERSION},"
                    f" as no datafixer exists!"
                )
            target = WriteReadBuffer()
            version = fixer.apply(read_buffer, target, context=context)
            read_buffer = target
        
        return read_buffer
    
    def encode_datafixable(self, write_buffer: WriteBuffer):
        write_buffer.write_singleton_struct(self._VERSION_SIZE, self.VERSION)
