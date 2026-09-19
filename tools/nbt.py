"""Small, dependency-free little-endian NBT writer for our own structures."""
import struct

def byte(v): return (1, v)
def integer(v): return (3, v)
def long(v): return (4, v)
def string(v): return (8, v)
def listing(kind, values): return (9, (kind, values))
def compound(v): return (10, v)

def text(value):
    data = value.encode('utf-8')
    return struct.pack('<H', len(data)) + data

def payload(kind, value):
    if kind == 1: return struct.pack('<b', value)
    if kind == 3: return struct.pack('<i', value)
    if kind == 4: return struct.pack('<q', value)
    if kind == 8: return text(value)
    if kind == 9:
        subtype, values = value
        return struct.pack('<bi', subtype, len(values)) + b''.join(payload(subtype, v) for v in values)
    if kind == 10:
        return b''.join(bytes([t]) + text(k) + payload(t, v) for k, (t, v) in value.items()) + b'\0'
    raise ValueError(kind)

def dumps(value): return b'\x0a\0\0' + payload(10, value)

def structure(size, blocks):
    """blocks are palette names in X/Y/Z order; format 1 remains supported in 26.50."""
    palette = list(dict.fromkeys(blocks))
    indices = {b: i for i, b in enumerate(palette)}
    return dumps({
        'format_version': integer(1),
        'size': listing(3, list(size)),
        'structure_world_origin': listing(3, [0, 0, 0]),
        'structure': compound({
            'block_indices': listing(9, [(3, [indices[b] for b in blocks]), (3, [-1] * len(blocks))]),
            'entities': listing(10, []),
            'palette': compound({'default': compound({
                'block_palette': listing(10, [
                    {'name': string('minecraft:' + b), 'states': compound({}), 'version': integer(18168865)}
                    for b in palette
                ]),
                'block_position_data': compound({})
            })})
        })
    })
