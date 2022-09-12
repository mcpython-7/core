import io
import struct
import typing
from collections import namedtuple


class INBTSerializeAble:
    pass


class IObjectNBTSerializer:
    @classmethod
    def check_if_top(cls, stream: io.BytesIO, serialize: "NBTSerializer") -> bool:
        raise NotImplementedError

    @classmethod
    def decode_from_top(cls, stream: io.BytesIO, serialize: "NBTSerializer") -> object:
        raise NotImplementedError

    @classmethod
    def encode_data(cls, obj: object, serialize: "NBTSerializer") -> bytes:
        raise NotImplementedError

    @classmethod
    def create(
        cls,
        check: typing.Callable[[io.BytesIO, "NBTSerializer"], bool],
        decode: typing.Callable[[io.BytesIO, "NBTSerializer"], object],
        encode: typing.Callable[[object, "NBTSerializer"], bytes],
    ):
        class Serializer(IObjectNBTSerializer):
            check_if_top = check
            decode_from_top = decode
            encode_data = encode

        return Serializer


class NBTSerializer:
    def __init__(self):
        self.serializers: typing.List[typing.Type[IObjectNBTSerializer]] = []
        self.type2serializer: typing.Dict[
            typing.Type, typing.Type[IObjectNBTSerializer]
        ] = {}

    def register_type_serializer(
        self, data_type: typing.Type, serializer: typing.Type[IObjectNBTSerializer]
    ):
        self.serializers.append(serializer)
        self.type2serializer[data_type] = serializer

    def decode_stream(self, stream: io.BytesIO):
        for serializer in self.serializers:
            if serializer.check_if_top(stream, self):
                return serializer.decode_from_top(stream, self)

        raise ValueError(stream.tell())

    def encode_into_stream(self, obj: object) -> bytes:
        obj_types = [type(obj)]
        visited = {object}

        while obj_types:
            obj_type = obj_types.pop()

            if obj_type in visited:
                continue

            if obj_type in self.type2serializer:
                serializer = self.type2serializer[obj_type]
                break

            visited.add(obj_type)
            obj_types += obj_type.__bases__
        else:
            raise ValueError(obj)

        return serializer.encode_data(obj, self)


SERIALIZER = NBTSerializer()

# Byte
_BYTE = struct.Struct(">b")
NBT_BYTE = namedtuple("NBT_BYTE", "value")
SERIALIZER.register_type_serializer(
    NBT_BYTE,
    IObjectNBTSerializer.create(
        lambda stream, serializer: stream.tell() == 1,
        lambda stream, serializer: NBT_BYTE(_BYTE.unpack(stream.read(2)[1:])),
        lambda obj, serializer: b"\x01" + _BYTE.pack(obj.value),
    ),
)

# Short
_SHORT = struct.Struct(">h")
_USHORT = struct.Struct(">H")
NBT_SHORT = namedtuple("NBT_SHORT", "value")
SERIALIZER.register_type_serializer(
    NBT_SHORT,
    IObjectNBTSerializer.create(
        lambda stream, serializer: stream.tell() == 2,
        lambda stream, serializer: NBT_SHORT(_SHORT.unpack(stream.read(3)[1:])),
        lambda obj, serializer: b"\x02" + _SHORT.pack(obj.value),
    ),
)

# Int
_INT = struct.Struct(">i")
NBT_INT = namedtuple("NBT_INT", "value")
SERIALIZER.register_type_serializer(
    NBT_INT,
    IObjectNBTSerializer.create(
        lambda stream, serializer: stream.tell() == 3,
        lambda stream, serializer: NBT_INT(_INT.unpack(stream.read(5)[1:])),
        lambda obj, serializer: b"\x03" + _INT.pack(obj.value),
    ),
)

# Long
_LONG = struct.Struct(">l")
NBT_LONG = namedtuple("NBT_LONG", "value")
SERIALIZER.register_type_serializer(
    NBT_LONG,
    IObjectNBTSerializer.create(
        lambda stream, serializer: stream.tell() == 4,
        lambda stream, serializer: NBT_LONG(_LONG.unpack(stream.read(9)[1:])),
        lambda obj, serializer: b"\x04" + _LONG.pack(obj.value),
    ),
)

# Float
_FLOAT = struct.Struct(">f")
NBT_FLOAT = namedtuple("NBT_FLOAT", "value")
SERIALIZER.register_type_serializer(
    NBT_FLOAT,
    IObjectNBTSerializer.create(
        lambda stream, serializer: stream.tell() == 5,
        lambda stream, serializer: NBT_FLOAT(_FLOAT.unpack(stream.read(5)[1:])),
        lambda obj, serializer: b"\05" + _FLOAT.pack(obj.value),
    ),
)

# Double
_DOUBLE = struct.Struct(">d")
NBT_DOUBLE = namedtuple("NBT_DOUBLE", "value")
SERIALIZER.register_type_serializer(
    NBT_DOUBLE,
    IObjectNBTSerializer.create(
        lambda stream, serializer: stream.tell() == 6,
        lambda stream, serializer: NBT_DOUBLE(_DOUBLE.unpack(stream.read(9)[1:])),
        lambda obj, serializer: b"\06" + _DOUBLE.pack(obj.value),
    ),
)

# Byte Array
NBT_BYTE_ARRAY = namedtuple("NBT_BYTE_ARRAY", "value")
SERIALIZER.register_type_serializer(
    NBT_BYTE_ARRAY,
    IObjectNBTSerializer.create(
        lambda stream, serializer: stream.tell() == 7,
        lambda stream, serializer: NBT_BYTE_ARRAY(
            stream.read(_INT.unpack(stream.read(5)[1:]))
        ),
        lambda obj, serializer: b"\07" + _INT.pack(len(obj.value)) + obj.value,
    ),
)

# String
NBT_STRING = namedtuple("NBT_STRING", "value")
SERIALIZER.register_type_serializer(
    NBT_BYTE_ARRAY,
    IObjectNBTSerializer.create(
        lambda stream, serializer: stream.tell() == 7,
        lambda stream, serializer: NBT_BYTE_ARRAY(
            stream.read(_USHORT.unpack(stream.read(5)[1:])).decode("utf-8")
        ),
        lambda obj, serializer: b"\07"
        + _USHORT.pack(len(obj.value))
        + obj.value.encode("utf-8"),
    ),
)

# List
