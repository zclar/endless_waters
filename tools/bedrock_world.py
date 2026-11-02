"""Typed little-endian NBT for editing native Bedrock world metadata."""
from io import BytesIO
from pathlib import Path
import struct

FORMATS = {1: 'b', 2: 'h', 3: 'i', 4: 'q', 5: 'f', 6: 'd'}


def loads(data):
    stream = BytesIO(data)
    def number(fmt):
        return struct.unpack('<' + fmt, stream.read(struct.calcsize('<' + fmt)))[0]
    def string():
        return stream.read(number('H')).decode('utf8')
    def value(tag):
        if tag in FORMATS:
            return number(FORMATS[tag])
        if tag == 7:
            return stream.read(number('i'))
        if tag == 8:
            return string()
        if tag == 9:
            subtype, count = number('B'), number('i')
            return subtype, [value(subtype) for _ in range(count)]
        if tag == 10:
            result = {}
            while (kind := number('B')):
                name = string()
                result[name] = (kind, value(kind))
            return result
        if tag in [11, 12]:
            return [number('i' if tag == 11 else 'q') for _ in range(number('i'))]
        raise ValueError(tag)
    assert number('B') == 10
    name = string()
    root = value(10)
    assert not stream.read(), 'Trailing NBT data'
    return name, root


def dumps(root, name=''):
    def string(value):
        data = value.encode('utf8')
        return struct.pack('<H', len(data)) + data
    def value(tag, item):
        if tag in FORMATS:
            return struct.pack('<' + FORMATS[tag], item)
        if tag == 7:
            return struct.pack('<i', len(item)) + item
        if tag == 8:
            return string(item)
        if tag == 9:
            subtype, items = item
            return bytes([subtype]) + struct.pack('<i', len(items)) + b''.join(value(subtype, v) for v in items)
        if tag == 10:
            return b''.join(bytes([kind]) + string(key) + value(kind, v) for key, (kind, v) in item.items()) + b'\0'
        if tag in [11, 12]:
            return struct.pack('<i', len(item)) + b''.join(struct.pack('<i' if tag == 11 else '<q', v) for v in item)
        raise ValueError(tag)
    return b'\x0a' + string(name) + value(10, root)


def read_level(path):
    data = Path(path).read_bytes()
    version, length = struct.unpack('<ii', data[:8])
    assert len(data) == length + 8
    name, root = loads(data[8:])
    return version, name, root


def write_level(path, version, name, root):
    data = dumps(root, name)
    Path(path).write_bytes(struct.pack('<ii', version, len(data)) + data)
