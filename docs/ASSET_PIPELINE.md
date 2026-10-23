# Asset pipeline and preservation

All 107 original assets/ files (106 PNGs and one layered PSP source) and 18 quarantined authored PNGs are protected at their original paths. Corel working copies, unused variants and zombie_02 files retain source value regardless of linkage. No cleanup rewrites image encoding, metadata, pixels, filenames or palette. The machine .lnk stays local and is never dereferenced. [Provenance](ASSET_PROVENANCE.md) owns authorship/notices, not generation policy.

CMakeLists.txt enumerates current inputs and invokes tools/generate_*.ps 1. Output goes beneath the selected build's generated/ directory, then SDCC compiles the listed generated modules into the link. Validators compare dimensions, palette/alpha, generated payload/layout and actual composites to current source artwork. Do not hand-edit generated tables or substitute archived art.

| Input group | Generation/use |
| --- | --- |
| Concrete, blood-concrete, door, red door and four switch frames | Packed reference textures, wall palette and exact native wall schedules/palette columns |
| zombie_01 standing/walking/hit/shot-dead/corpse 8 x 8 | Actor presentation and distant LOD derivation |
| Six zombie_01 standing/walking 01/walking 02/shot 01/shot-dead/corps 16 x 16 | Authored middle presentation |
| Seven zombie_01 walking 01/walking 02/standing-attack/attack 01/attack 02/shot 01/corps 32 x 32 | Authored near/melee payloads and near-ID mapping |
| gun_12x 12, gun_shoot_12x 12 | Held pistol and native HUD masks |
| shotgun_held, shotgun_held_shoot |20x16 held shotgun,2 x screen-space display and masks |
| shotgun.png, pistol.png | Pause weapon icons; shotgun.png is the 16 x 16 pause source |
| pick_up_shotgun.png | Independent world pickup and derived LOD/projection data |
| health_hud, health_hud_1 | Health icon/bar tiles |
| sega_logo, game_over | Separate cold presentation data/palette |

Sprite alpha 15 is no-overwrite. The foreground row cache supports 8/16/32 sources and retains current clamping, strict wall-depth ties and source-step rules. Near art has a distinct page lifetime. Weapon pause/held/pickup art are separate roles; do not interchange them. Generators and validators assert actual input dimensions rather than inferring them from filenames.

The exact active source list expanded from CMakeLists.txt appears below. All other original files remain preserved, including every zombie_02 file; no second-zombie runtime type or selection was implemented.

- `assets/logos/game_over.png`
- `assets/logos/sega_logo.png`
- `assets/sprites/enemies/zombie/zombie_01_attack_01_32x32.png`
- `assets/sprites/enemies/zombie/zombie_01_attack_02_32x32.png`
- `assets/sprites/enemies/zombie/zombie_01_corps.png`
- `assets/sprites/enemies/zombie/zombie_01_corps_16x16.png`
- `assets/sprites/enemies/zombie/zombie_01_corps_32x32.png`
- `assets/sprites/enemies/zombie/zombie_01_shot_01.png`
- `assets/sprites/enemies/zombie/zombie_01_shot_01_16x16.png`
- `assets/sprites/enemies/zombie/zombie_01_shot_01_32x32.png`
- `assets/sprites/enemies/zombie/zombie_01_shot_02.png`
- `assets/sprites/enemies/zombie/zombie_01_shot_dead.png`
- `assets/sprites/enemies/zombie/zombie_01_shot_dead_16x16.png`
- `assets/sprites/enemies/zombie/zombie_01_standing.png`
- `assets/sprites/enemies/zombie/zombie_01_standing_16x16.png`
- `assets/sprites/enemies/zombie/zombie_01_standing_attack_32x32.png`
- `assets/sprites/enemies/zombie/zombie_01_walking_01.png`
- `assets/sprites/enemies/zombie/zombie_01_walking_01_16x16.png`
- `assets/sprites/enemies/zombie/zombie_01_walking_01_32x32.png`
- `assets/sprites/enemies/zombie/zombie_01_walking_02.png`
- `assets/sprites/enemies/zombie/zombie_01_walking_02_16x16.png`
- `assets/sprites/enemies/zombie/zombie_01_walking_02_32x32.png`
- `assets/sprites/weapons/gun_12x12.png`
- `assets/sprites/weapons/gun_shoot_12x12.png`
- `assets/sprites/weapons/pick_up_shotgun.png`
- `assets/sprites/weapons/pistol.png`
- `assets/sprites/weapons/shotgun.png`
- `assets/sprites/weapons/shotgun_held.png`
- `assets/sprites/weapons/shotgun_held_shoot.png`
- `assets/textures/walls/switch_off_01.png`
- `assets/textures/walls/switch_off_02.png`
- `assets/textures/walls/switch_on_01.png`
- `assets/textures/walls/switch_on_02.png`
- `assets/textures/walls/wall_concrete.png`
- `assets/textures/walls/wall_concrete_blood.png`
- `assets/textures/walls/wall_door.png`
- `assets/textures/walls/wall_door_red.png`
- `assets/ui/health_hud.png`
- `assets/ui/health_hud_1.png`
