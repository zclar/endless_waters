import json
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[1]
pack = root / 'behavior_packs/endless_waters'
manifest = json.loads((pack / 'manifest.json').read_text())
assert manifest['header']['min_engine_version'] == [1, 26, 50]
features = {p.stem for p in (pack / 'features').glob('*.json')}
for path in pack.rglob('*.json'): json.loads(path.read_text())
for path in (pack / 'features').glob('column_*.json'):
    data = json.loads(path.read_text())['minecraft:structure_template_feature']
    name = data['structure_name'].split(':')[1]
    assert (pack / f'structures/endless/{name}.mcstructure').is_file()
assert 'depth_selector' in features
rule = json.loads((pack / 'feature_rules/endless_water.json').read_text())['minecraft:feature_rules']
assert rule['description']['places_feature'] == 'endless:depth_selector'
archive = root / 'dist/Endless_Waters.mcpack'
with zipfile.ZipFile(archive) as z: assert z.testzip() is None
print(f'Validated {len(features)} feature definitions and {archive.stat().st_size:,} byte package.')
