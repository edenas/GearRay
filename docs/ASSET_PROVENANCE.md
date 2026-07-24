# GearRay Asset Provenance

## Purpose

This document records the source, ownership, license, and release status of
GearRay's non-code assets. It must be updated before adding or distributing new
art, audio, fonts, maps, screenshots, or other media.

No entry marked **confirmation required** should be presented as confirmed
original or cleared for public redistribution until the maintainer has
completed that entry. Git commit authorship alone does not prove ownership of
an asset's underlying content.

Unless a row explicitly says otherwise, its ownership and license status
remains to be confirmed.

## Runtime Texture Sources

| Category | Files or directory | Purpose | Creator/source | Intended license | Status |
| --- | --- | --- | --- | --- | --- |
| Active wall texture | `assets/textures/walls/wall_concrete.png` | Current wall-texture generator input | **Confirmation required** | **Confirmation required** | Used by the build; ownership and license must be confirmed |
| Active door texture | `assets/textures/walls/wall_door.png` | Current door-texture generator input | **Confirmation required** | **Confirmation required** | Used by the current working build; ownership and license must be confirmed |
| Directional brick textures | `wall_brick_x.png`, `wall_brick_y.png` | Historical or planned wall material | **Confirmation required** | **Confirmation required** | Not currently selected by CMake |
| Directional metal textures | `wall_metal_x.png`, `wall_metal_y.png` | Historical or planned wall material | **Confirmation required** | **Confirmation required** | Not currently selected by CMake |
| Directional technology textures | `wall_tech_x.png`, `wall_tech_y.png` | Historical or planned wall material | **Confirmation required** | **Confirmation required** | Not currently selected by CMake |
| Legacy directional concrete/door textures | `wall_concrete_x.png`, `wall_concrete_y.png`, `wall_door_x.png`, `wall_door_y.png` | Earlier texture pipeline inputs | **Confirmation required** | **Confirmation required** | Deleted in the current working tree; confirm archival or removal decision |

The PowerShell generator converts active texture inputs into generated C data
inside the build directory. Generated texture tables are derived from their
input images and therefore inherit any relevant licensing obligations of those
images.

## Floor and Ceiling Textures

| Category | Files or directory | Purpose | Creator/source | Intended license | Status |
| --- | --- | --- | --- | --- | --- |
| Ceiling texture | `assets/textures/ceilings/ceiling_industrial.png.png` | Planned or reference ceiling art | **Confirmation required** | **Confirmation required** | Not used by the current build; duplicated extension should be reviewed |
| Floor texture | `assets/textures/floors/floor_industrial.png` | Planned or reference floor art | **Confirmation required** | **Confirmation required** | Not used by the current build |

## Texture Library and References

| Category | Files or directory | Purpose | Creator/source | Intended license | Status |
| --- | --- | --- | --- | --- | --- |
| Ceiling reference | `assets/textures/library/ceiling_tiles.png` | Design/reference material | **Confirmation required** | **Confirmation required** | Do not assume redistribution clearance |
| Floor reference | `assets/textures/library/floor_tiles.png` | Design/reference material | **Confirmation required** | **Confirmation required** | Do not assume redistribution clearance |
| Wall reference | `assets/textures/library/wall_reference.png` | Design/reference material | **Confirmation required** | **Confirmation required** | Do not assume redistribution clearance |

Reference material should be removed from the public release if it is not
needed and cannot be documented with a redistribution-compatible license.

## Corel Auto-Preserve Files

Directory: `assets/textures/walls/Corel Auto-Preserve/`

Current or pending files include:

- `wall_concrete.png`
- `wall_concrete_x.png`
- `wall_concrete_y.png.png`
- `wall_door.png`

These appear to be editor-generated preservation or working files. Their exact
creation history, relationship to the active textures, creator, ownership, and
license are **confirmation required**. The directory should not be included in
a public release merely as an editor backup. Retain it only if it provides
documented source value and all content is cleared for redistribution.

## Renderer Captures

Directory: `artifacts/`

| Category | Files or directory | Purpose | Creator/source | Intended license | Status |
| --- | --- | --- | --- | --- | --- |
| Task 101 captures | `artifacts/task101/*.png` | Early renderer orientation evidence | Emulator/capture details **confirmation required** | **Confirmation required** | Historical engineering evidence |
| Tasks 102–107 captures | `artifacts/task102/` through `artifacts/task107/` | Renderer milestone and optimization evidence | Emulator/capture details **confirmation required** | **Confirmation required** | Historical engineering evidence |

`artifacts/task102/native-4bpp-walls.png` and
`artifacts/task103/solid-wall-fast-path.png` are byte-for-byte identical. They
may represent separate milestones, but that reason should be recorded if both
are retained.

Before using a capture as the public README screenshot, record:

- who captured it;
- the emulator or hardware used;
- the GearRay commit/tag and ROM build;
- confirmation that all visible art is cleared for release.

## Maps and Code-Embedded Visual Data

The workshop map in `game/workshop_map.c`, palette values generated from texture
inputs, and native tile patterns embedded in platform source are distributed as
code rather than standalone media. Their design/source ownership is
**confirmation required** for this provenance record even though the files are
covered by the repository's source license.

## Audio, Fonts, Sprites, and Additional Media

No standalone audio, font, or sprite asset collection is currently present.
Before adding one, record:

- exact filename and category;
- creator and source URL or source project;
- whether the work is original, commissioned, or derived;
- license and attribution text;
- modification history;
- redistribution and commercial-use permission.

## Maintainer Confirmation Checklist

Before the first public asset-bearing release:

- [ ] Confirm Edenas Pocius's ownership or redistribution rights for each
      active runtime texture.
- [ ] Decide whether the MIT License covers confirmed original GearRay assets
      or whether a separate asset license will be used.
- [ ] Confirm or remove all texture-library references.
- [ ] Review and remove unnecessary Corel Auto-Preserve files.
- [ ] Resolve duplicated filename extensions.
- [ ] Record the provenance of historical captures.
- [ ] Select and document a cleared public README screenshot.
- [ ] Update `THIRD_PARTY_NOTICES.md` for any third-party media retained.
