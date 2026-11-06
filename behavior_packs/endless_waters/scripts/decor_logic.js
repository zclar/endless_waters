export function interactDecor(block, player, options) {
    if (!block?.isValid) return;
    let permutation=block.permutation;
    if (player?.isSneaking && options.colors) {
        permutation=permutation.withState('endless:color',
            (Number(permutation.getState('endless:color'))+1)%options.colors);
    } else if (options.styles && (!options.light || player?.isSneaking)) {
        permutation=permutation.withState('endless:style',
            (Number(permutation.getState('endless:style'))+1)%options.styles);
    } else if (options.light) {
        permutation=permutation.withState('endless:lit',!permutation.getState('endless:lit'));
    } else if (options.colors) {
        permutation=permutation.withState('endless:color',
            (Number(permutation.getState('endless:color'))+1)%options.colors);
    }
    block.setPermutation(permutation);
}

