"""Audit decoration sources without running their code or changing release packs."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    existing = {}
    for kind in ['blocks', 'items']:
        for path in (ROOT / 'behavior_packs/endless_waters' / kind).rglob('*.json'):
            data = json.loads(path.read_text())
            body = data.get('minecraft:block', data.get('minecraft:item'))
            if body:
                ident = body['description']['identifier']
                assert ident not in existing, ident
                existing[ident] = str(path.relative_to(ROOT))
    furniture = []
    for path in sorted((ROOT / 'third_party/furnideco/BP/blocks').rglob('*.json')):
        body = json.loads(path.read_text())['minecraft:block']
        source_id = body['description']['identifier']
        target_id = 'endless:decor_' + source_id.split(':')[1].replace('.', '_')
        assert target_id not in existing or "/blocks/decor/" in existing[target_id], target_id
        furniture.append({'source_id': source_id, 'target_id': target_id,
                          'source': str(path.relative_to(ROOT)),
                          'legacy_components_to_port': sorted(k for k in body['components'] if k.startswith('furnideco:'))})
    assert len({d['target_id'] for d in furniture}) == len(furniture)
    aliases = {
        'oceanoverhaul:driftwood_plank': 'endless:driftwood_plank',
        'oceanoverhaul:sea_glass': 'endless:sea_glass',
        'oceanoverhaul:polished_prismarine_bricks': 'endless:polished_prismarine_bricks',
        'oceanoverhaul:pearl_lantern': 'endless:pearl_lantern',
        'oceanoverhaul:deep_sea_helmet': 'endless:deep_sea_helmet',
        'oceanoverhaul:oxygen_tank': 'endless:oxygen_tank',
        'oceanoverhaul:flippers': 'endless:flippers',
    }
    assert set(aliases.values()) <= existing.keys()
    report = {'status': 'identifier audit; runtime results are recorded in ship_review/validation.json',
              'existing_identifiers': existing, 'reuse_existing': aliases,
              'furniture': furniture, 'furniture_count': len(furniture),
              'furniture_identifier_conflicts': [],
              'release_sha256': hashlib.sha256((ROOT/'dist/Endless_Waters.mcaddon').read_bytes()).hexdigest()}
    out = ROOT/'experiments/decor/inventory.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2)+'\n')
    print(f'Audited {len(furniture)} furniture definitions; no target identifier collisions.')


if __name__ == '__main__':
    main()
