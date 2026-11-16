# ZV-01 Luna implementation and qualification return

Date: 2026-11-16  
Execution owner: Luna  
Return recipient: Sol, by manual owner transfer only  
Disposition: integrated candidate and broad technical qualification complete; Sol engineering review/repair/integration and owner-only acceptance remain open. This report does not claim Astra acceptance or publication readiness.

## Result

Security and scientist zombie art now has an explicit deterministic generation and production-link path. All specified authored tiers are wired: hot base and middle sprites in Bank 1, sixteen 32x32 near frames in Bank 4, per-type distant LODs, and current held-shotgun idle/fire composites. Asset selection is explicit; the pipeline does not glob editor copies. The only added palette conversions are `#4D4D4D -> 2`, `#797878 -> 3`, and `#FFFFFF -> 12`. There is no `#03000F` alias.

Candidate ROM: [GearRay.gg](../../../../build/zv01-luna/canonical-source/rom/GearRay.gg)  
Bytes: 131,072 (128 KiB)  
SHA-256: `B5F9DA2B5461574C6C09BC06387EEAA08AE304CAEEFC96F4FFCE1B7C2C58349B`  
Source: main `e6d1e2346e3752c2fce9332c3fe59f6c2e31190e` plus the owner-authored artwork/planning and the uncommitted ZV-01 work. Production dirs (`game`, `engine`, `platform`, `assets`, `CMakeLists.txt`, generators) in the isolated canonical workflow copy match the root source by SHA with zero differences.

The named clean CMake/Ninja Release build and isolated canonical `cmd.exe /d /c build.bat` Release workflow both produced this exact ROM SHA. The frozen October ROM remains 65,536 bytes with SHA-256 `3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340`; it was not overwritten. No commit, push, tag, publication or automatic inter-role handoff was made.

## Engineering and resource findings

- Generator fingerprints include content and correctly invalidate when selected zombie or held-shotgun PNG content changes while byte length and timestamp are preserved. Both isolated mutation cases restored the exact original input and reproduced the candidate SHA.
- Authored source preservation audit: all 122 recorded input files match their pre-campaign SHA-256; 0 mismatches. No authored PNG bytes were changed during this work.
- ROM packager header byte `0x7F`; makesms checksum `0x40FE`. Of 58,184 emitted IHX addresses, 58,182 linked payload bytes match physical ROM offsets (the other two are the checksum pair). Bank 4 holds 8,192 bytes of near frames plus a 32-byte table at virtual `0x48000` / CPU `0x8000`; pointer and payload checks pass.
- ROM occupancy: Bank 0 12,889 used / 3,495 free; Bank 1 16,324 / **44 free**; Bank 2 8,139 / 8,245; Bank 3 extent 12,756 / 3,628; Bank 4 8,224 / 8,160. Bank 1 has little placement headroom and merits attention during Sol's integration review.
- Persistent RAM is 1,538 bytes, unchanged from baseline; eight nine-byte actors occupy 72 bytes. No persistent renderer cache growth. Conservative call-chain stack maximum is 586 bytes plus the inherited 32-byte IRQ allowance = 618 of the 1,024-byte reservation. Pinned Emulicious observed a 387-byte high-water over 51,700 measured interrupts. This does not independently prove physical-device/NMI lifetime assumptions.
- Toolchain: CMake 4.4.0-rc2, Ninja 1.13.2, SDCC 4.6.0 #16555 and Python 3.12.10. Emulator binary identity and profiler observer metadata are retained in evidence.

## Acceptance and qualification matrix

| Assignment criterion | Result | Evidence / boundary |
| --- | --- | --- |
| Authored two-type asset path, palette, tiers, shotgun and Bank 1/4 integration | PASS | Asset, near/middle/weapon validators; generated payloads and pointers checked; `#03000F` absent. |
| Content-based dependencies and preserved-mtime rebuilds | PASS | Two isolated same-size/same-mtime content mutations changed fingerprints and refreshed outputs; restored build returned candidate SHA. |
| Clean and canonical Release candidate; header, IHX, placement and identity | PASS | Candidate identity, canonical build log and clean subtree identity; both builds produce the same SHA. |
| Broad actor/map/renderer/cache/occlusion/native-bank/combat qualification | PASS for scripted candidate checks | Retained applicable core evidence plus current-candidate runs below. Physical hardware and full human gameplay are separate. |
| Full validator suite and production-dispatch mutations | PASS | 24/24 validators exit 0; all five mutation cases verified, including expected rejection cases. Assertions were adapted to current contracts and retained. |
| Compiled math and renderer regression against actual candidate | PASS | 202,068 scenarios; 0 mismatches: wall 168,960; wrapper 20,480; ray 11,616; camera 484; material 242; prep 226; transitions 24; occlusion 36. |
| Native wall correctness | PASS | 41,943,040 cases across height/offset/side/material/screen-row, all 256 native color pairs; linked slot-2 worker without VDP/IRQ ownership. |
| RAM/VRAM/stack/ROM accounting | PASS with placement risk | Resource values above; VRAM layout unchanged. Bank 1 has 44 bytes free. |
| Final-candidate performance campaign | PASS with cold-tail caveat | 11 Emulicious routes, each 32 warmup + 256 measured samples; no unclosed spans; max observed stack 387; 51,700 measured interrupts. Seeded zombie/LOD/mixed routes can die and restart; cold maxima up to 25.76M cycles (about 431 display periods) are retained, with active median/p95 shown separately. |
| Exact candidate emulator mixed-actor/weapon/pause/death/restart playthrough | PARTIAL / OWNER-DEPENDENT | Candidate launched and displayed initial gameplay in Emulicious, but the short UI attempt did not maintain a reliable picture. Do not infer full visual/gameplay acceptance. Grouped owner checklist is below. |
| Physical Game Gear acceptance | UNRUN / OWNER-DEPENDENT | Not claimed; assess separately if required. |

Performance evidence reports per-route mean, median, p95, max and counters. Profiled routes: static, rotation, forward, geometry, zombies, offscreen, pistol, shotgun, LOD, mixed and authored. The long zombie/offscreen/LOD/mixed maxima are cold death/restart intervals, not silently discarded; review the retained route metadata and raw data before drawing tail conclusions.

## Preserved evidence and reproducibility

Start at [evidence index](evidence/README.md). Machine-readable summaries include candidate and tool/source identity, asset preservation, validator results, dispatch mutations, compiled regression totals, preserved-mtime cases, emulator metadata, profiler self-test, ABI metadata and performance summary. Individual validator logs and compiled-oracle outputs are retained beneath `evidence/`. The campaign used the existing full audit runner; legacy fixture expectations were repaired to the authoritative map, actor ABI, Bank 4 and current generated symbols without removing assertions or mutation cases.

Reproduce the clean candidate build from the project root:

```powershell
cmake -S . -B build/zv01-luna -G Ninja -DCMAKE_BUILD_TYPE=Release -DGEARRAY_PROFILE_RENDERER=OFF -DGEAR_RAY_ROM_FILENAME=GearRay.gg -DGEAR_RAY_ROM_DIR=D:/mano_projektai/GearRay/build/zv01-luna/rom
cmake --build build/zv01-luna --target rom/GearRay.gg
```

Canonical workflow was separately executed with `cmd.exe /d /c build.bat` from `build/zv01-luna/canonical-source`. See [copy-ready Sol continuation](CONTINUE_PROMPT_FOR_SOL.md) for the requested review and grouped human checks.

Campaign entry commands from the project root:

```powershell
tools/full_z80_audit.ps1 -BuildDirectory build/zv01-luna -RunValidators -RomPath build/zv01-luna/rom/GearRay.gg
tools/validate_native_wall.ps1 -BuildDirectory build/zv01-luna -RequireMapPlacement -RequireAssembly
py -3.12 tools/performance/build_driver.py --java-tools build/zv01-luna/java-tools
py -3.12 tools/performance/test_profiler.py --java-tools build/zv01-luna/java-tools --output build/zv01-luna/profiler-self-test.json
py -3.12 tools/performance/benchmark.py 256 --actor-layout visual-type-animation-v1 --warmup 32 --route-length 16 --logical-input --build build/zv01-luna --java-tools build/zv01-luna/java-tools --only A_static,B_rotation,C_forward,F_geometry,G_zombies,H_offscreen,I_pistol,I_shotgun,J_lod,L_mixed,M_authored --output build/zv01-luna/replay-final
```

The compiled regression artifacts are retained as JSON and the preserved-mtime runner at `qualification/test_preserved_mtime_fingerprints.py` records its isolated mutation procedure. Logs, outputs and metadata live in the evidence tree; rebuild first if starting from a clean checkout.

## Next action

The owner manually transfers the CONTINUE prompt and candidate to Sol. Sol owns engineering review, any in-scope repairs, affected regression reruns and the consolidated implementation report before any later acceptance review. The human Emulicious checklist names the exact ROM and covers both species/map regions/poses/corpses, shotgun idle/fire, unchanged pickup/pause icons, movement/fire feel, pause and restart. Physical hardware review is distinct. Luna stops here; no dispatch was sent.
