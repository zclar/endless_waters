"""Vibrant Visuals materials for our assets; leave external water/lighting alone."""
from sea_life import save


def build(rp):
    # Uniform MER values avoid extra mobile texture memory. Original RGBA color
    # textures (including transparency) are shared with the classic renderer.
    materials = {
        'driftwood_plank': [0, 0, 220],
        'sea_glass': [0, 0, 45],
        'polished_prismarine_bricks': [0, 0, 130],
        'pearl_lantern': [0, 150, 140],
        'deep_sea_helmet': [0, 0, 150],
        'oxygen_tank': [0, 0, 150],
        'flippers': [0, 0, 205],
        'endless_diving_1': [0, 0, 150],
    }
    for path in sorted((rp / 'textures').rglob('*.png')):
        mer = ([0, 0, 85] if path.stem.startswith('jellyfish_') else
               [0, 0, 180] if path.stem.startswith('seahorse_') else
               materials[path.stem])
        save(path.with_suffix('.texture_set.json'), {
            'format_version': '1.21.30',
            'minecraft:texture_set': {
                'color': path.stem,
                'metalness_emissive_roughness': mer,
            },
        })
