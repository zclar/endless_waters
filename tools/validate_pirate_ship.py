"""Review-asset checks; these do not replace Bedrock runtime tests."""
from collections import deque
from io import BytesIO
import hashlib
import json
import struct
import subprocess
from pirate_ship import OUT, ROOT, SIZE, VARIANTS, AIR, build_ship


def decode(data):
    stream = BytesIO(data)
    def number(fmt):
        return struct.unpack('<' + fmt, stream.read(struct.calcsize('<' + fmt)))[0]
    def string():
        return stream.read(number('H')).decode('utf8')
    def value(tag):
        if tag in [1, 3, 4]:
            return number({1:'b',3:'i',4:'q'}[tag])
        if tag == 8:
            return string()
        if tag == 9:
            subtype, count = number('B'), number('i')
            return [value(subtype) for _ in range(count)]
        if tag == 10:
            result = {}
            while (kind := number('B')):
                name = string()
                result[name] = value(kind)
            return result
        raise ValueError(tag)
    assert number('B') == 10
    string()
    result = value(10)
    assert not stream.read()
    return result


def dry_hull(ship):
    # Flood exterior empty voxels below the water surface. No explicit interior
    # air cell may be reached through the hull. Lower hull uses full cubes.
    queue = deque([(0, 0, 0)])
    seen = set(queue)
    while queue:
        p = queue.popleft()
        for delta in [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]:
            n = tuple(p[i] + delta[i] for i in range(3))
            if 0 <= n[0] < SIZE[0] and 0 <= n[1] < 8 and 0 <= n[2] < SIZE[2] and n not in seen and ship.blocks.get(n, AIR) == AIR:
                seen.add(n)
                queue.append(n)
    assert not any(ship.blocks.get(p) == AIR for p in seen), 'Water reaches interior'


def validate():
    catalog = json.loads((OUT / 'catalog.json').read_text())
    report = {'scope': 'static block layouts and files; not engine or multiplayer validation', 'variants': {}}
    for variant in VARIANTS:
        ship = build_ship(variant)
        info = catalog['variants'][variant]
        count = 0
        for part in info['parts']:
            raw = (OUT / part['file']).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == part['sha256']
            nbt = decode(raw)
            assert nbt['size'] == part['size'] and nbt['size'][0] <= 64 and nbt['size'][2] <= 64
            sx, sy, sz = nbt['size']
            structure = nbt['structure']
            indices, water = structure['block_indices']
            palette = structure['palette']['default']['block_palette']
            assert len(indices) == len(water) == sx * sy * sz
            assert set(water) == {-1}
            assert structure['entities'] == [], 'Preview crew are planned, not embedded'
            for index, block_id in enumerate(indices):
                x = index // (sy * sz)
                y = (index // sz) % sy
                z = index % sz + part['offset'][2]
                expected = ship.blocks.get((x, y, z))
                if expected is None:
                    assert block_id == -1
                else:
                    p = palette[block_id]
                    assert p['name'] == (expected.name if ':' in expected.name else 'minecraft:' + expected.name)
                    assert p['states'] == dict(expected.states)
                    count += expected != AIR
        assert count == info['solid_blocks'] and count > 14000
        assert len(ship.loot)>=25
        assert sum(b.name.startswith('endless:decor_') for b in ship.blocks.values())>=150
        for part in info['parts']:
            nbt=decode((OUT/part['file']).read_bytes())
            entities=nbt['structure']['palette']['default']['block_position_data']
            expected=[l for l in ship.loot if part['offset'][2]<=l['position'][2]<part['offset'][2]+part['size'][2]]
            assert len(entities)==len(expected)
            for entity in entities.values():
                data=entity['block_entity_data']
                assert data['LootTableSeed']==0 and 'Items' not in data
                assert (ROOT/'behavior_packs/endless_waters'/data['LootTable']).is_file()
        for x, y, z in ship.crew:
            assert ship.blocks.get((x, y - 1, z), AIR) != AIR
            assert ship.blocks.get((x, y, z), AIR) == AIR
            assert ship.blocks.get((x, y + 1, z), AIR) == AIR
        assert len(ship.crew) == {'new': 12, 'tattered': 8, 'abandoned': 0}[variant]
        dry_hull(ship)
        view = json.loads((OUT / (variant + '.json')).read_text())
        assert len(view['blocks']) == len(ship.blocks)
        for x, y, z, i in view['blocks']:
            palette_block = view['palette'][i]
            actual = ship.blocks[(x, y, z)]
            assert palette_block['name'] == actual.name and palette_block['states'] == dict(actual.states)
        report['variants'][variant] = {'solid_blocks': count, 'dry_hull': True,
                                        'crew_positions_clear': True, 'nbt_matches_layout': True,
                                        'furnished': True, 'random_loot_chests':len(ship.loot)}
    report['main_addon_sha256'] = hashlib.sha256((ROOT/'dist/Endless_Waters.mcaddon').read_bytes()).hexdigest()
    (OUT / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    validate()
