# Ocean structure candidates — researched 2026-11-02

Research only: no structures or third-party executable code have been added.
All candidates below are Java content and need asset inspection, conversion to
Bedrock, block/state and loot translation, and tests with our generator.

## First candidate: Trek

- Project: https://modrinth.com/datapack/trek
- Author repository: https://github.com/hotsu0p/Trek
- License: https://github.com/hotsu0p/Trek/blob/main/license (MIT text).
- Author lists ships, ancient buildings, ruins and water islands among 150+
  structures. Select only ships/ruins compatible with the all-ocean design.
- GitHub holds issue tracking/docs; inspect the downloaded datapack and its
  included license for the selected assets before copying them. No assets have
  yet been inspected or validated for Bedrock.

## Legacy Boat Ruins

- https://modrinth.com/mod/legacy-boat-ruins
- https://github.com/425913490bb-gif/boat_ruins_mod
- Author lists three wreck templates and five loot-table categories, using
  vanilla items. A small set could provide wood and supplies during exploration.
- Repository/project label says MIT, while README says CC0. Inspect the actual
  LICENSE and templates before importing; preserve the applicable notice.

## Later candidate: YUNG's Better Ocean Monuments

- https://github.com/YUNG-GANG/YUNGs-Better-Ocean-Monuments
- Repository declares LGPL-3.0. Check asset-specific notices and retain the
  applicable license/source/attribution with any adaptation.
- Larger monuments are a later project: size, multi-piece layout, guardians and
  water placement need more work than a small wreck. Not a drop-in Bedrock pack.

## Rejected or deferred

- TONI's Better Shipwrecks: description/search excerpts mention MIT but the
  actual CurseForge project currently labels All Rights Reserved. Defer pending
  a clear license for the actual builds.
- Hopo and Moog intake assets were already excluded after license review.

## Placement requirements

Our final generation pass removes above-water blocks. Surface vessels must be
placed after terrain cleanup, with tests showing they survive generation and
reload. Seabed structures must fit actual floor depth without flattening caves
or leaving air bubbles. Use vanilla supplies with restrained loot, several
rotations/variants, and enough spacing for meaningful exploration. Verify a
small set in-engine before expanding it.
