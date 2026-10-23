# Documentation reconstruction plan

Reconstruct current references from current source and fresh output. Do not repair a 54-KiB architecture chapter and 80-KiB Bible by appending another disclaimer. Preserve their exact pre-edit versions as historical documents, then replace their maintained roles deliberately. Do not rewrite dated reports/raw measurements.

## One owner per topic

| Document | Maintained role and required action |
| --- | --- |
| README.md | Concise overview, current controls/features, accepted synchronous status, canonical build/ROM, navigation and hardware caveat. Remove pistol-only/START-reserved/current-hardware-qualified claims. |
| docs/README.md (new) | Navigation hub with “current” versus “history” separation; authority order: source/build/test evidence, topic reference, dated history. |
| docs/BUILDING.md | Pinned observed tools/hashes versus unknown upstream revisions, supported Windows setup, build/release/dev/profile output policy, exact clean workflow and dependency overrides. |
| docs/CURRENT_BEHAVIOR.md | Gameplay only: movement/rotation/strafe/interaction, pause, weapons/pickup, AI/damage/death/corpses, doors/switch, restart; explicitly eight zombies, WorldSprite 9 bytes, zombie_02 art only. Link architecture/performance instead of copying their tables. |
| docs/ENGINE_ARCHITECTURE.md | Current module ownership, exact loop sequence, cache inputs, renderer stages, mapper ownership boundaries and synchronous timing. Move historical narrative out of the maintained account. |
| docs/ROM_BANKING.md | Current logical/physical mapping, page lifetimes, link contract, fresh occupancy/RAM/stack/VRAM, and growth constraints; remove first-migration instructions presented as next actions. |
| docs/ASSET_PIPELINE.md (new) | Protected source art→generators→build-generated tables→linked assets. Exact active CMake inputs, alpha and LOD contracts, unused zombie_02 status, no source-PNG modification. |
| docs/ASSET_PROVENANCE.md | Authorship/provenance only. Record user-declared original artwork without inventing rights for unrelated references. Remove obsolete deletion advice and incorrect “all *_16x16 active” assumptions; preservation instruction controls cleanup. |
| docs/TESTING.md (new) | One explicit Release validation entry point, all 24 tests, compiled oracles/bench dependencies, pending interactive/hardware checklist, restore procedure for historical evidence. Distinguish source/host, compiled and human results. |
| docs/PERFORMANCE_BASELINE.md (new) | Selected SHA, measurement date/config, 2,880 paired records, current combined means/tails/resources, cold restart caveat, small regressions and update-rate limitations. Link evidence; no new optimization roadmap. |
| docs/DEVELOPMENT_GUIDE.md (new) | Content-change workflow, module/cache/asset/bank contracts, preserved capacity, test triggers; preparation only for a future second zombie. |
| GearRay_Developer_Bible.md | Short compatibility/navigation page linking current topic owners and the immutable historical full Bible. Stop calling it the competing “single consolidated current reference.” |
| docs/PROJECT_BIBLE.md | Short redirect to the documentation hub/history role; retain existing entry links. |
| docs/HISTORY.md (new) | Date/topic/status index of all dated studies and experiments, retention/restore links, final acceptance as current decision. No mass moves of old reports just to rearrange headings. |
| CHANGELOG.md | Add accurate Unreleased notes for already implemented pause/shotgun/performance follow-up and repository maintenance. Preserve dated release history; no invented release version/tag. |
| CONTRIBUTING.md | Current build/test commands, link topic owners and explain temporary experiments under build/experiments. |
| ACKNOWLEDGEMENTS, LICENSE, SECURITY, THIRD_PARTY_NOTICES | Preserve authorship/notices/policy; change only demonstrably stale project workflow/tool evidence. Do not add a new licensing exercise or unverified claims. |

## Concrete contradictions to fix

| Existing location | Current problem | Authoritative replacement |
| --- | --- | --- |
| README controls and following paragraph | START “reserved”; pistol only, no switching/additional weapons | input_pause_requested in input.c; main pause branch; pause_map.c; weapons.h defines pistol/shotgun; HUD/pickup acquisition path |
| README current status and architecture “current project status” | Broad hardware-tested wording covers newer untested optimization | Prior hardware milestones remain historical; accepted combined ROM is emulator-verified, complete interactive A/B and physical qualification pending |
| ENGINE_ARCHITECTURE Input/API sections; Bible Appendix A | No START request API | input.c exports input_pause_requested and main consumes it |
| ENGINE_ARCHITECTURE Camera, fixed-point details; Bible rotation | Runtime normalization/integer square root described as active | camera.c follows generated 242-state/484-edge exact legacy graph, explicitly maps page 2 |
| ENGINE_ARCHITECTURE exact loop list | HUD order misplaced, pause omitted, raycasting always all 28 | Read game/main.c order; complete ray reuse/material refresh are active; pause restores and continues without gameplay tick |
| ENGINE_ARCHITECTURE wall sampling/per-pixel text | Old scalar wall/HUD algorithms remain mixed with native descriptions | native_wall.c generated schedules/palette columns; generated HUD keep/plane masks; scalar implementations are regression evidence |
| ENGINE_ARCHITECTURE future weapons/game logic | Switching, additional weapon and health listed as future | Two weapons, acquisition/auto-equip/selection and health already exist; ammo/audio/progression remain separate future work |
| ROM_BANKING opening, policies and “next migration” | First Bank 1 migration/data banking “when introduced” mixed with four-bank engine | Current Bank 2 code+art and disjoint hot/cold Bank 3 scopes; no speculative relocation task |
| BUILDING validation examples | Partial older suite / build root defaults / old placement wording | Single current 24-validator runner with explicit build/release and ROM; profile tested separately |
| Bible authority paragraphs | Both “historical” and “single consolidated current reference” | Preserve full original as dated history; replace root entry with current-doc navigation |
| ASSET_PROVENANCE | Missing shotgun/pause sources, broad zombie glob, editor files proposed for removal | Current CMake membership plus manifest; all authored files protected, unused zombie_02 not implemented |
| Old POST_AUDIT_HARDENING and validator_hygiene | Old rejected caches, 20/21-validator counts, old resources/pickup behavior | Keep byte-identical historical reports; index them as superseded by later implementation and final acceptance |

## Required technical account

Derive the exact loop from game/main.c: optional profiling start; input; pause/restore/continue; sprite timers; sample fire and rotate; move/copy camera; HUD update and pickup acquisition; all-actor AI every fourth update; lethal exit; interaction; switch animation; ray update; resolve previous pending shot against current state; latch current fire; VBlank; shake; draw. Initialization prepares a complete first frame; Game Over/logo hold/restart are separate cold paths. Do not claim a fixed simulation rate or one game update per display refresh.

Describe full ray geometry keys (six pose values and three door states), terminal material refresh, exact camera transition graph, native wall preparation/8-row worker and page restoration, stable sprite ordering/budget, completed preparation keys (all actor bytes/count, pose, pickup cells/state, wall depths), foreground-only repeated-row reuse with sentinel 255, sprite-guarded wall offset comparison, HUD mask generation and transparency. Explain all offscreen AI remains active and pending-shot order is preserved. No cooperative scheduler or framebuffer is linked.

Document input B1 rising-edge fire, B2+left/right strafe and non-strafe B2 release interaction, START pause. First shotgun acquisition auto-equips; duplicate ownership preserves selection. Include pistol and shotgun combat, strict wall-depth ties, doors/crushing/player safety, persistent corpses, pause freeze/restore and restart input rules from their modules and validators. Do not infer behavior from an earlier screenshot or milestone title.

Fresh resources should reproduce: 64 KiB; banks 12,865/14,217/11,737/12,756 used; RAM 1,538; WorldSprite 9 bytes ×8; conservative stack 590+32=622 versus 1,024 reserve; observed maximum 383 (corpus bound, not proof); VRAM delta zero. Native wall virtual 0x39200/CPU 0x9200 maps physical 0xD200; cold Bank 3 ends at 0xD1FC. Label physical absolute offsets versus offsets within Bank 3. Use measured final maps rather than copying this table if source changed.

Acceptance: source-to-section review, no contradicted current claims, every topic has one owner, maintained relative links resolve, history is indexed without rewriting bytes, commands work from a clean build, final resource/hash assertions match executed evidence. Store a documentation change matrix with section, source/test reference and result. Do not manufacture a current screenshot or hardware test.
