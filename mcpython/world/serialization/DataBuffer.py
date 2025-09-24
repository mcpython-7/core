from __future__ import annotations

import io
import typing
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
        data = self.source.read(entry.size)
        if len(data) < entry.size:
            raise IOError(
                f"Stream ended when no end was expected: read {len(data)} byte(s), expected {entry.size} byte(s)"
            )
        return entry.unpack(data)[0]

    def read_int8(self) -> int:
        pack = _INT8
        data = self.source.read(pack.size)
        return pack.unpack(data)[0]

    def read_uint8(self) -> int:
        return self.source.read(1)[0]

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

    def read_remaining(self):
        return self.source.read()


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
        self.target.write(bytes((value,)))
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
        return self.target.getvalue()

    def start_read(self):
        return ReadBuffer(self.get_data())
