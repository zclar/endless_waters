import struct

def integer(v): return (3, v)
def string(v): return (8, v)
def listing(kind, values): return (9, (kind, values))
def compound(v): return (10, v)

def text(value):
    data = value.encode('utf-8')
    return struct.pack('<H', len(data)) + data

def payload(kind, value):
    if kind == 3: return struct.pack('<i', value)
    if kind == 8: return text(value)
    if kind == 9:
        subtype, values = value
        return struct.pack('<bi', subtype, len(values)) + b''.join(payload(subtype, v) for v in values)
    if kind == 10:
        encoded = []
        for key, typed in value.items():
            if isinstance(typed, tuple) and len(typed) == 2 and isinstance(typed[0], int):
                tag, item = typed
            elif isinstance(typed, dict):
                tag, item = 10, typed
            elif isinstance(typed, int):
                tag, item = 3, typed
            else:
                raise ValueError(f'Unencoded NBT field: {key}')
            encoded.append(bytes([tag]) + text(key) + payload(tag, item))
        return b''.join(encoded) + b'\0'
    raise ValueError(kind)

def dumps(value): return b'\x0a\0\0' + payload(10, value)

def structure(size, blocks):
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
