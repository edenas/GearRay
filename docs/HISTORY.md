# History and retained evidence

Current topic owners are in the [documentation hub](README.md). Dated reports retain their original bytes, dates, paths, encodings, failures and decisions. The final optimization decision is B - APPROVED WITH MINOR NOTES; cooperative/fixed-rate architectures remain experimental/rejected for production. Earlier hardware-tested milestones do not qualify the current optimized ROM.

## Retrieval and link classification

The [2026-10-23 catalog](history/2026-10-23/catalog.json) maps every retained original path to size/SHA-256, provenance, dependency set and immutable archive/member/hash. Original27 ZIPs remain at their original paths. New content-addressed project evidence is in history/2026-10-23/objects.zip. Python binaries/CFR/decompiled emulator research are retained only in ignored artifacts/local-history/2026-10-23; optional local research is not reproducible from a clone alone.

```powershell
py -3.12 tools/maintenance/restore_history.py --list --entry build-astra-final-control
py -3.12 tools/maintenance/restore_history.py --entry build-astra-final-control --dest build/history-restore/control
py -3.12 tools/maintenance/restore_history.py --entry docs/performance/2026-10-19/post-implementation-followup/astra-final-review/evidence/selected-replay/frame-samples.csv --dest build/history-restore/accepted-replay
```

Add --project-only to skip cataloged local-only runtime/research objects, or use tools/maintenance/restore_oracle_inputs.py for the public compiled-reference sets. Use --catalog with the execution-journal-catalog.json named in the cleanup report when retrieving this run's compacted raw journals.

Retrieval rejects traversal, absolute members, conflicting duplicates, symlink/junction components, outside-project outputs and differing existing files. Destinations are case directories beneath build/history-restore/. Restore symbol/link/source sets with their ROM for compiled oracles, not only an image. Restored link files keep original absolute paths as provenance; the maintained resolver follows listed object order using same-name restored local objects. Runtime algorithms/assertions are unchanged by path adapters.

Live links point to present reports/scripts/small summaries. Links in historical reports to compacted raw CSV/trace/large JSON payloads are **archived; restore required**, not live filesystem links. Adjacent ARCHIVED_DATA.md notices list those payloads. The catalog is the exact resolver. Pre-reconstruction current-document paths identify their earlier retained version; current paths now point to their single topic owner. The [full previous Bible](history/2026-10-23/pre-cleanup/GearRay_Developer_Bible.md) retains old relative paths as historical context.

The [maintenance plan](maintenance/2026-10-23/README.md) is immutable planning evidence. The [implementation report](maintenance/2026-10-23/implementation/IMPLEMENTATION_REPORT.md) records actual removal/retention/restore tests and measured disk usage. Do not run old source-mutating setup/finalization writers against current source or overwrite historical evidence.

## Original100-document index

Every original Markdown document is listed below. Current references were reconstructed only after freezing their previous bytes; historical reports remain at their original paths. This index does not promote every historical proposal.

| Original path | Role/status | Original title |
| --- | --- | --- |
| [ACKNOWLEDGEMENTS.md](../ACKNOWLEDGEMENTS.md) | Current project policy / notices; prior bytes retained where reconstructed | Acknowledgements |
| [CHANGELOG.md](../CHANGELOG.md) | Current project policy / notices; prior bytes retained where reconstructed | Changelog |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | Current topic/navigation; prior bytes retained in catalog | Contributing to GearRay |
| [GearRay_Developer_Bible.md](../GearRay_Developer_Bible.md) | Current topic/navigation; prior bytes retained in catalog | GearRay Developer Bible |
| [README.md](../README.md) | Current topic/navigation; prior bytes retained in catalog | GearRay |
| [SECURITY.md](../SECURITY.md) | Current project policy / notices; prior bytes retained where reconstructed | Security Policy |
| [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) | Current project policy / notices; prior bytes retained where reconstructed | Third-Party Notices |
| [docs/ASSET_PROVENANCE.md](ASSET_PROVENANCE.md) | Current topic/navigation; prior bytes retained in catalog | GearRay Asset Provenance |
| [docs/BUILDING.md](BUILDING.md) | Current topic/navigation; prior bytes retained in catalog | Building GearRay |
| [docs/CURRENT_BEHAVIOR.md](CURRENT_BEHAVIOR.md) | Current topic/navigation; prior bytes retained in catalog | GearRay current behavior and architecture |
| [docs/ENGINE_ARCHITECTURE.md](ENGINE_ARCHITECTURE.md) | Current topic/navigation; prior bytes retained in catalog | GearRay Engine Architecture |
| [docs/ENGINE_FOUNDATION_V1.0.0.md](ENGINE_FOUNDATION_V1.0.0.md) | Historical evidence / dated project policy | GearRay Engine Foundation v1.0.0 |
| [docs/full_z80_simplification_audit.md](full_z80_simplification_audit.md) | Historical evidence / dated project policy | Full Z80 simplification and residency audit |
| [docs/held_shotgun_20x16.md](held_shotgun_20x16.md) | Historical evidence / dated project policy | Held shotgun: authored 20×16 canvas |
| [docs/pause_freeze_audit.md](pause_freeze_audit.md) | Historical evidence / dated project policy | Final pause freeze / Z80 audit — 2026-09-16 |
| [docs/pause_map.md](pause_map.md) | Historical evidence / dated project policy | GearRay final pause map and gameplay freeze |
| [docs/pause_padding_pattern_checkpoint.md](pause_padding_pattern_checkpoint.md) | Historical evidence / dated project policy | Pause 20x20 padding: required pattern-allocation checkpoint |
| [docs/pause_pistol_icon.md](pause_pistol_icon.md) | Historical evidence / dated project policy | Static pause pistol icon |
| [docs/pause_weapon_focus_borders.md](pause_weapon_focus_borders.md) | Historical evidence / dated project policy | Pause defaults to WEAPONS; white center and gray side borders |
| [docs/pause_weapon_padding_active_focus.md](pause_weapon_padding_active_focus.md) | Historical evidence / dated project policy | Pause weapon padding and active focus |
| [docs/POST_AUDIT_HARDENING.md](POST_AUDIT_HARDENING.md) | Historical evidence / dated project policy | Post-audit Z80 hardening record |
| [docs/PROJECT_BIBLE.md](PROJECT_BIBLE.md) | Current topic/navigation; prior bytes retained in catalog | GearRay Project Bible |
| [docs/ROM_BANKING.md](ROM_BANKING.md) | Current topic/navigation; prior bytes retained in catalog | GearRay ROM Banking Architecture |
| [docs/rom_bank_architecture_checkpoint.md](rom_bank_architecture_checkpoint.md) | Historical evidence / dated project policy | GearRay ROM bank architecture checkpoint |
| [docs/shotgun_aim_samples.md](shotgun_aim_samples.md) | Historical evidence / dated project policy | Shotgun aim sample correction |
| [docs/shotgun_combat_bank_checkpoint.md](shotgun_combat_bank_checkpoint.md) | Historical evidence / dated project policy | Shotgun combat checkpoint and completed pickup expansion |
| [docs/shotgun_combat_final.md](shotgun_combat_final.md) | Historical evidence / dated project policy | Shotgun combat identity and Bank 3 Game Over relocation |
| [docs/shotgun_pickup_cap_auto_equip.md](shotgun_pickup_cap_auto_equip.md) | Historical evidence / dated project policy | Shotgun close-range cap and first-time auto-equip |
| [docs/shotgun_pickup_perspective.md](shotgun_pickup_perspective.md) | Historical evidence / dated project policy | Shotgun world pickup perspective / source LOD correction |
| [docs/shotgun_pickup_perspective_correction.md](shotgun_pickup_perspective_correction.md) | Historical evidence / dated project policy | World shotgun perspective correction |
| [docs/shotgun_pickup_scale.md](shotgun_pickup_scale.md) | Historical evidence / dated project policy | Shotgun pickup scale correction |
| [docs/shotgun_pickup_touch_far.md](shotgun_pickup_touch_far.md) | Historical evidence / dated project policy | Shotgun pickup touch region and dark FAR silhouette |
| [docs/SPRINT_11_TASK_107_RENDERER_PROFILE.md](SPRINT_11_TASK_107_RENDERER_PROFILE.md) | Historical evidence / dated project policy | Sprint 11 Task 107: renderer profiling report |
| [docs/SPRINT_11_TASK_108_OPTIMIZATION_PASS_1.md](SPRINT_11_TASK_108_OPTIMIZATION_PASS_1.md) | Historical evidence / dated project policy | Sprint 11 Task 108: optimization pass 1 |
| [docs/SPRINT_17_DISTANT_WALL_LOD.md](SPRINT_17_DISTANT_WALL_LOD.md) | Historical evidence / dated project policy | Sprint 17: distant-wall LOD |
| [docs/SPRINT_21_ENGINE_PERFORMANCE_AUDIT.md](SPRINT_21_ENGINE_PERFORMANCE_AUDIT.md) | Historical evidence / dated project policy | Sprint 21: Engine Performance Audit |
| [docs/SPRINT_22_FINAL_DISTANT_WALL_LOD.md](SPRINT_22_FINAL_DISTANT_WALL_LOD.md) | Historical evidence / dated project policy | Sprint 22: final distant-wall LOD |
| [docs/SPRINT_23_SENIOR_CODE_CLEANUP_AUDIT.md](SPRINT_23_SENIOR_CODE_CLEANUP_AUDIT.md) | Historical evidence / dated project policy | Sprint 23: senior code cleanup and architecture audit |
| [docs/SPRINT_24_PLAYER_MOVEMENT_AND_CONTROL_FEEL.md](SPRINT_24_PLAYER_MOVEMENT_AND_CONTROL_FEEL.md) | Historical evidence / dated project policy | Sprint 24: player movement and control feel |
| [docs/SPRINT_25_EXPERIMENTAL_8X8_WALL_TEXTURE.md](SPRINT_25_EXPERIMENTAL_8X8_WALL_TEXTURE.md) | Historical evidence / dated project policy | Sprint 25 — Experimental Native 8×8 Wall Texture |
| [docs/SPRINT_26_EXPERIMENTAL_FAR_WALL_DITHER.md](SPRINT_26_EXPERIMENTAL_FAR_WALL_DITHER.md) | Historical evidence / dated project policy | Sprint 26 — Experimental Far-Wall Ordered Dither |
| [docs/SPRINT_27_EXPERIMENTAL_BLACK_FOG_LOD.md](SPRINT_27_EXPERIMENTAL_BLACK_FOG_LOD.md) | Historical evidence / dated project policy | Sprint 27 — Experimental Black Fog LOD |
| [docs/SPRINT_28_EXPERIMENTAL_DISTANCE_ATTENUATION.md](SPRINT_28_EXPERIMENTAL_DISTANCE_ATTENUATION.md) | Historical evidence / dated project policy | Sprint 28 — Experimental Distance Attenuation |
| [docs/SPRINT_29_HYBRID_DISTANCE_FOG.md](SPRINT_29_HYBRID_DISTANCE_FOG.md) | Historical evidence / dated project policy | Sprint 29 — Hybrid Distance Fog |
| [docs/SPRINT_30_POST_8X8_RENDERER_PERFORMANCE_AUDIT.md](SPRINT_30_POST_8X8_RENDERER_PERFORMANCE_AUDIT.md) | Historical evidence / dated project policy | Sprint 30 — Post-8×8 Renderer Performance Audit |
| [docs/SPRINT_31_FINAL_GAME_GEAR_CONTROLS.md](SPRINT_31_FINAL_GAME_GEAR_CONTROLS.md) | Historical evidence / dated project policy | Sprint 31: final Game Gear controls |
| [docs/SPRINT_31_SENIOR_ENGINE_ARCHITECTURE_AUDIT.md](SPRINT_31_SENIOR_ENGINE_ARCHITECTURE_AUDIT.md) | Historical evidence / dated project policy | Sprint 31: senior engine architecture audit |
| [docs/two_weapon_bank_pressure.md](two_weapon_bank_pressure.md) | Historical evidence / dated project policy | Two-weapon milestone: bank-placement approval checkpoint |
| [docs/two_weapon_milestone.md](two_weapon_milestone.md) | Historical evidence / dated project policy | Two-weapon milestone — final production report |
| [docs/two_weapon_pre_edit.md](two_weapon_pre_edit.md) | Historical evidence / dated project policy | Two-weapon milestone: pre-edit findings |
| [docs/validator_hygiene.md](validator_hygiene.md) | Historical evidence / dated project policy | Normal build validator hygiene |
| [docs/world_shotgun_pickup_asset.md](world_shotgun_pickup_asset.md) | Historical evidence / dated project policy | Dedicated world shotgun pickup artwork |
| [docs/ZOMBIE_PRESENTATION_PIPELINE.md](ZOMBIE_PRESENTATION_PIPELINE.md) | Historical evidence / dated project policy | Zombie Presentation and Renderer Audit |
| [docs/ZOMBIE_SYSTEM_ARCHITECTURE_AUDIT.md](ZOMBIE_SYSTEM_ARCHITECTURE_AUDIT.md) | Historical evidence / dated project policy | Zombie System Architecture and Melee-Spacing Audit |
| [docs/performance/2026-10-19/ARCHITECTURE_RECONSTRUCTION.md](performance/2026-10-19/ARCHITECTURE_RECONSTRUCTION.md) | Historical evidence / dated project policy | Architecture reconstruction |
| [docs/performance/2026-10-19/ASTRA_IMPLEMENTATION_ARCHITECTURE.md](performance/2026-10-19/ASTRA_IMPLEMENTATION_ARCHITECTURE.md) | Historical evidence / dated project policy | Recommended implementation architecture |
| [docs/performance/2026-10-19/ASTRA_INDEPENDENT_REVIEW.md](performance/2026-10-19/ASTRA_INDEPENDENT_REVIEW.md) | Historical evidence / dated project policy | GearRay independent performance review |
| [docs/performance/2026-10-19/ASTRA_OPTIMIZATION_DECISION_MATRIX.md](performance/2026-10-19/ASTRA_OPTIMIZATION_DECISION_MATRIX.md) | Historical evidence / dated project policy | Optimization decision matrix |
| [docs/performance/2026-10-19/ASTRA_TECHNICAL_SOURCES.md](performance/2026-10-19/ASTRA_TECHNICAL_SOURCES.md) | Historical evidence / dated project policy | Independent technical sources — 2026-10-19 |
| [docs/performance/2026-10-19/ASTRA_VALIDATION_PLAN.md](performance/2026-10-19/ASTRA_VALIDATION_PLAN.md) | Historical evidence / dated project policy | Validation and rollback specification |
| [docs/performance/2026-10-19/BANKING_AND_MEMORY_AUDIT.md](performance/2026-10-19/BANKING_AND_MEMORY_AUDIT.md) | Historical evidence / dated project policy | Banking, RAM, stack and VRAM audit |
| [docs/performance/2026-10-19/COMPILED_MICROBENCHMARKS.md](performance/2026-10-19/COMPILED_MICROBENCHMARKS.md) | Historical evidence / dated project policy | Compiled routine microbenchmarks |
| [docs/performance/2026-10-19/EXPERIMENTS_AND_ALTERNATIVES.md](performance/2026-10-19/EXPERIMENTS_AND_ALTERNATIVES.md) | Historical evidence / dated project policy | Controlled experiments and architectural alternatives |
| [docs/performance/2026-10-19/EXTERNAL_REFERENCE_NOTES.md](performance/2026-10-19/EXTERNAL_REFERENCE_NOTES.md) | Historical evidence / dated project policy | External reference boundaries |
| [docs/performance/2026-10-19/FRAME_PIPELINE_AND_INPUT_LATENCY.md](performance/2026-10-19/FRAME_PIPELINE_AND_INPUT_LATENCY.md) | Historical evidence / dated project policy | Frame pipeline, input latency and control cadence |
| [docs/performance/2026-10-19/GENERATED_Z80_ANALYSIS.md](performance/2026-10-19/GENERATED_Z80_ANALYSIS.md) | Historical evidence / dated project policy | Generated SDCC Z80 analysis |
| [docs/performance/2026-10-19/GIT_VERIFICATION.md](performance/2026-10-19/GIT_VERIFICATION.md) | Historical evidence / dated project policy | Git packaging verification - 2026-10-19 |
| [docs/performance/2026-10-19/HANDOFF_TO_ASTRA.md](performance/2026-10-19/HANDOFF_TO_ASTRA.md) | Historical evidence / dated project policy | Independent review handoff — stage2 |
| [docs/performance/2026-10-19/IMPLEMENTATION_MASTER_PROMPT.md](performance/2026-10-19/IMPLEMENTATION_MASTER_PROMPT.md) | Historical evidence / dated project policy | GearRay implementation master prompt — Codex 6.1 Solo High |
| [docs/performance/2026-10-19/IMPLEMENTATION_RECORD.md](performance/2026-10-19/IMPLEMENTATION_RECORD.md) | Historical evidence / dated project policy | Performance implementation engineering record |
| [docs/performance/2026-10-19/IMPLEMENTATION_REPORT.md](performance/2026-10-19/IMPLEMENTATION_REPORT.md) | Historical evidence / dated project policy | GearRay performance implementation - 2026-10-19 |
| [docs/performance/2026-10-19/OPTIMIZATION_OPPORTUNITIES.md](performance/2026-10-19/OPTIMIZATION_OPPORTUNITIES.md) | Historical evidence / dated project policy | Optimization opportunities and dependencies |
| [docs/performance/2026-10-19/PERFORMANCE_BENCHMARKS.md](performance/2026-10-19/PERFORMANCE_BENCHMARKS.md) | Historical evidence / dated project policy | Performance measurements and reproduction |
| [docs/performance/2026-10-19/PERFORMANCE_FINDINGS.md](performance/2026-10-19/PERFORMANCE_FINDINGS.md) | Historical evidence / dated project policy | Ranked findings and evidence registry |
| [docs/performance/2026-10-19/PROJECT_DOCUMENT_INDEX.md](performance/2026-10-19/PROJECT_DOCUMENT_INDEX.md) | Historical evidence / dated project policy | Project document and historical decision index |
| [docs/performance/2026-10-19/RAYCASTER_DEEP_AUDIT.md](performance/2026-10-19/RAYCASTER_DEEP_AUDIT.md) | Historical evidence / dated project policy | Raycaster deep audit |
| [docs/performance/2026-10-19/README.md](performance/2026-10-19/README.md) | Historical evidence / dated project policy | GearRay performance investigation — 2026-10-19 |
| [docs/performance/2026-10-19/REGRESSION_AND_CORRECTNESS_RISKS.md](performance/2026-10-19/REGRESSION_AND_CORRECTNESS_RISKS.md) | Historical evidence / dated project policy | Regression and correctness requirements |
| [docs/performance/2026-10-19/RENDERER_AND_VRAM_DEEP_AUDIT.md](performance/2026-10-19/RENDERER_AND_VRAM_DEEP_AUDIT.md) | Historical evidence / dated project policy | Renderer, compositor and VRAM deep audit |
| [docs/performance/2026-10-19/SPRITES_AI_AND_GAMEPLAY_AUDIT.md](performance/2026-10-19/SPRITES_AI_AND_GAMEPLAY_AUDIT.md) | Historical evidence / dated project policy | Sprites, AI and gameplay audit |
| [docs/performance/2026-10-19/UNRESOLVED_QUESTIONS.md](performance/2026-10-19/UNRESOLVED_QUESTIONS.md) | Historical evidence / dated project policy | Unresolved questions and missing measurements |
| [docs/performance/2026-10-19/post-implementation-followup/IMPLEMENTATION_RECORD.md](performance/2026-10-19/post-implementation-followup/IMPLEMENTATION_RECORD.md) | Historical evidence / dated project policy | Astra follow-up engineering record |
| [docs/performance/2026-10-19/post-implementation-followup/IMPLEMENTATION_REPORT.md](performance/2026-10-19/post-implementation-followup/IMPLEMENTATION_REPORT.md) | Historical evidence / dated project policy | Astra follow-up implementation report |
| [docs/performance/2026-10-19/post-implementation-followup/astra-final-review/FINAL_ACCEPTANCE_REVIEW.md](performance/2026-10-19/post-implementation-followup/astra-final-review/FINAL_ACCEPTANCE_REVIEW.md) | Historical evidence / dated project policy | Final acceptance review |
| [docs/performance/2026-10-19/post-implementation-followup/astra-final-review/INDEPENDENT_VALIDATION_RESULTS.md](performance/2026-10-19/post-implementation-followup/astra-final-review/INDEPENDENT_VALIDATION_RESULTS.md) | Historical evidence / dated project policy | Independent validation results |
| [docs/performance/2026-10-19/post-implementation-followup/astra-final-review/PERFORMANCE_AND_RESOURCE_COMPARISON.md](performance/2026-10-19/post-implementation-followup/astra-final-review/PERFORMANCE_AND_RESOURCE_COMPARISON.md) | Historical evidence / dated project policy | Performance and resources |
| [docs/performance/2026-10-19/post-implementation-followup/astra-final-review/README.md](performance/2026-10-19/post-implementation-followup/astra-final-review/README.md) | Historical evidence / dated project policy | GearRay final independent acceptance review |
| [docs/performance/2026-10-19/post-implementation-followup/astra-final-review/REMAINING_RISKS_AND_OPPORTUNITIES.md](performance/2026-10-19/post-implementation-followup/astra-final-review/REMAINING_RISKS_AND_OPPORTUNITIES.md) | Historical evidence / dated project policy | Remaining risks and opportunities |
| [docs/performance/2026-10-19/post-implementation-followup/astra-final-review/SECOND_ZOMBIE_READINESS_NOTES.md](performance/2026-10-19/post-implementation-followup/astra-final-review/SECOND_ZOMBIE_READINESS_NOTES.md) | Historical evidence / dated project policy | Preparation for a second zombie |
| [docs/performance/2026-10-19/post-implementation-review/ARCHITECTURAL_ALTERNATIVES.md](performance/2026-10-19/post-implementation-review/ARCHITECTURAL_ALTERNATIVES.md) | Historical evidence / dated project policy | Architectural alternatives and isolated experiments |
| [docs/performance/2026-10-19/post-implementation-review/ENGINE_CORRECTNESS_REVIEW.md](performance/2026-10-19/post-implementation-review/ENGINE_CORRECTNESS_REVIEW.md) | Historical evidence / dated project policy | Engine correctness review |
| [docs/performance/2026-10-19/post-implementation-review/FINAL_FINDINGS_AND_RECOMMENDATIONS.md](performance/2026-10-19/post-implementation-review/FINAL_FINDINGS_AND_RECOMMENDATIONS.md) | Historical evidence / dated project policy | Final findings and recommendations |
| [docs/performance/2026-10-19/post-implementation-review/IMPLEMENTATION_VERIFICATION.md](performance/2026-10-19/post-implementation-review/IMPLEMENTATION_VERIFICATION.md) | Historical evidence / dated project policy | Implementation verification |
| [docs/performance/2026-10-19/post-implementation-review/PERFORMANCE_REBENCHMARK.md](performance/2026-10-19/post-implementation-review/PERFORMANCE_REBENCHMARK.md) | Historical evidence / dated project policy | Independent performance rebenchmark |
| [docs/performance/2026-10-19/post-implementation-review/README.md](performance/2026-10-19/post-implementation-review/README.md) | Historical evidence / dated project policy | GearRay independent post-implementation review — 2026-10-22 |
| [docs/performance/2026-10-19/post-implementation-review/REMAINING_BOTTLENECKS.md](performance/2026-10-19/post-implementation-review/REMAINING_BOTTLENECKS.md) | Historical evidence / dated project policy | Remaining bottlenecks |
| [docs/performance/2026-10-19/post-implementation-review/SOLO_FOLLOWUP_IMPLEMENTATION_PROMPT.md](performance/2026-10-19/post-implementation-review/SOLO_FOLLOWUP_IMPLEMENTATION_PROMPT.md) | Historical evidence / dated project policy | Codex 6.1 Solo High — exact compositor follow-up |
| [docs/performance/2026-10-19/post-implementation-review/VALIDATION_GAPS.md](performance/2026-10-19/post-implementation-review/VALIDATION_GAPS.md) | Historical evidence / dated project policy | Validation coverage and gaps |
| [docs/performance/2026-10-19/post-implementation-review/Z80_BANKING_AND_MEMORY_REVIEW.md](performance/2026-10-19/post-implementation-review/Z80_BANKING_AND_MEMORY_REVIEW.md) | Historical evidence / dated project policy | Z80, banking and memory review |
| [tools/performance/README.md](../tools/performance/README.md) | Historical evidence / dated project policy | Z80 performance measurement |
