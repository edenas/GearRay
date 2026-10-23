"""Apply final measured sprite experiment and temporal-scope qualifications."""
from pathlib import Path
import json,csv,statistics,hashlib
E=Path(__file__).resolve().parent;D=E.parent
R=json.loads((E/'rowcache-comparison.json').read_text())
assert R['records']==2880 and not R['mismatches']
def read(n):return (D/n).read_text(encoding='utf-8')
def write(n,s):(D/n).write_text(s,encoding='utf-8')
def table(headers,rows):return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in rows)
rowtable=table(['Route','Production mean T','Row-cache mean T','Reduction'],[(k,f"{v['baseline_mean']:,.2f}",f"{v['candidate_mean']:,.2f}",f"{v['reduction_percent']:.3f}%") for k,v in R['routes'].items()])
scope='''\n## Review snapshot and concurrent artwork\n\nThe verdict applies to committed implementation `bf89ea9c6f340a919e68e8059c0c005dff237f78` and selected ROM `E0FCFDD6FAE28794FED9B56CD256D27FCD029248A9A8DA846C12BB05DBF05566`, freshly reproduced at review start. New/modified zombie PNGs appeared during the review and were left untouched. Their end-of-review identities are in `evidence/final-preservation.json`; they are not covered by this ROM verdict. Candidate source inputs were copied from the frozen reviewed version, not those later artwork edits. Do not infer that rebuilding the latest changed working tree necessarily yields the reviewed hash.\n'''
s=read('README.md');start=s.index('**Verdict B');end=s.index('## Independently established')
s=s[:start]+'''**Verdict C — FURTHER OPTIMIZATION JUSTIFIED**, through a focused exact sprite-compositor improvement. The accepted production implementation is sound in the inspected contract and tested corpus, and its substantial improvement is reproduced. No P0 defect or architectural rework is required. The new P1 opportunity is a small measured kernel change, not a reason to replace the successful synchronous engine.

An isolated sprite-row reuse prototype improves the pistol route **11.11%**, shotgun **5.26%**, and the worst active-play interval **34.30%** (3.07→2.02 seconds). It **saves132 Bank0 bytes**, adds no persistent RAM/VRAM, and retains the38-byte local stack frame. All48,384 compiled graphics cases and2,880 full-state/ray/final-VRAM records match. This is the primary follow-up, PIR-010.

A secondary guarded wall-key candidate improves forward movement **7.66%**, costs36 ROM bytes and has small regressions (worst0.86% on shotgun). Its ungated version is rejected for80 stale VRAM bytes in a partial-occlusion fixture. Candidates were tested separately; their gains are not additive and no combined result is claimed. Neither was installed in production.

'''+s[end:]
s=s.replace('The follow-up is small and optional for continued game development, not a prerequisite to using the accepted ROM.','')
s+=scope
write('README.md',s)
s=read('IMPLEMENTATION_VERIFICATION.md')+scope+'''\n## Additional isolated sprite candidate\n\nThe final review's PIR-010 candidate retains the accepted wall/cache architecture and changes only `game_gear_overlay_sprite_tile` to reuse foreground row masks for repeated source-Y values within one tile. SHA2569F07A6282C0C9C046656C82965385C856C2A606A00CD26BBBCFD95BF7B88002A. Its complete2880-record replay and48,384 compiled cases pass. Candidate sources match initial reviewed inputs except `video.c` and a host-only definite-assignment compatibility adjustment in its copied weapon validator. Twenty-three original validators pass; the remaining original validator fails to compile translated C#, then passes with that adjustment and every pixel assertion retained. Production's24 validators pass unmodified. The guarded-wall candidate also passes24 validators against its isolated source after its configured ROM path is populated.\n'''
write('IMPLEMENTATION_VERIFICATION.md',s)
s=read('PERFORMANCE_REBENCHMARK.md')+'''\n## Important active tail: not all long intervals are cold\n\nJ update4 is an active10,982,103-T interval (~3.07s), with8,582,874 T in sprite overlay,81,273 in preparation,453,469 in rays and1,097,480 in wall rows. L update11 is active9,865,997 T, with7,010,078 in sprite overlay. These intervals execute no cold slot1 code. The corrected profile therefore identifies enlarged sprite composition as the dominant severe active tail, while walls/rays dominate ordinary changing empty views.\n\nThe exact row-cache experiment reduces those same intervals to7,214,922 and6,895,796 T respectively (34.30% and30.11%). It reduces J update10 from10,672,001 to7,138,775 T. New code preserves the source/depth span and caches only foreground keep/plane masks within one tile; every destination row still merges its own background. These are matched interval results, not a global worst-case bound. Complete candidate route statistics and resource costs are in ARCHITECTURAL_ALTERNATIVES.\n'''
write('PERFORMANCE_REBENCHMARK.md',s)
s=read('ENGINE_CORRECTNESS_REVIEW.md')+'''\n## PIR-010: exact per-tile repeated-source-row reuse\n\nFor one sprite/tile call, horizontal source indices, depth eligibility, art pointer, palette, source size and sprite identity are fixed. A repeated clamped source-Y therefore yields exactly the same transparent keep mask and four foreground planes. Cache those five values after the first decoded row and reuse them while Y is unchanged; still merge each destination row independently. Caching the already merged destination row would be incorrect when backgrounds or lower sprites differ.\n\nInitialize `last_source_y=255`, outside all valid0..31 source rows. The first visible row necessarily decodes and assigns every mask/plane. Vertical clipping can skip rows without reading uninitialized masks; a later visible row either matches a previously decoded row or triggers a decode. State is automatic and reset for every tile/sprite call; no cross-tile invalidation or global cache is added. IRQs do not mutate the frozen synchronous art/span inputs.\n\nThe isolated implementation passes the same48,384 compiled old/new cases (including large144-pixel bounds, differing destination-row patterns, transparency, clipping, depth ties,8/16/32 and actual near-ID), with the same output digest as accepted production. All2880 logical/render records match. Its host weapon validator requires only a C# definite-assignment adaptation, separately documented; the actual compiled-Z80 oracle does not need that adaptation.\n'''
write('ENGINE_CORRECTNESS_REVIEW.md',s)
s=read('Z80_BANKING_AND_MEMORY_REVIEW.md').replace('The fresh link gives these half-open regions:','The fresh link gives these sections and inclusive byte ranges:')
s+='''\n## Experimental resource delta (not production)\n\nPIR-010's linked Bank0 extent is12,829 (132 bytes smaller); other banks,1538 persistent RAM,64-KiB image and all VRAM allocations are unchanged. SDCC emits424 instruction lines for the sprite overlay versus463, with the same38-byte automatic frame and42-byte model peak. Sampled whole-route stack maximum remains383 and conservative main closure588. The reduction is a measured compiler result, not a source-line-count inference. The row cache has no new port/mapper calls or public ABI change. PIR-006 separately adds36 Bank0 bytes; do not combine the two deltas without a new link.\n'''
write('Z80_BANKING_AND_MEMORY_REVIEW.md',s)
s=read('REMAINING_BOTTLENECKS.md')
s=s.replace('## Priority','''## Severe active tail and measured remedy

At J update4, sprite composition is8,582,874 of10,982,103 T (~78%). At L update11 it is7,010,078 of9,865,997 T (~71%). These are active gameplay, not Game Over/logo waits. Near sprites enlarge the source: consecutive output rows often select the same source row, but the accepted kernel decodes all eight source pixels and four planes again. PIR-010 eliminates those repeated decodes within each tile. This changes the follow-up priority: wall/ray work dominates typical empty turns, but sprite row reuse is the demonstrated high-value remedy for the active tail.

## Priority''')
s=s.replace('- **PIR-006, P2:** Guarded offset canonicalization is the only new measured engine opportunity recommended for a narrow follow-up.', '- **PIR-010, P1:** Reuse decoded foreground row masks when source Y repeats within a sprite tile. Matched severe intervals improve30–34%; pistol/shotgun means improve11.11/5.26%; code shrinks132 bytes. Integrate this exact kernel first, with the supplied regression corpus.\n- **PIR-006, P2:** Guarded offset canonicalization is a secondary measured opportunity.')
write('REMAINING_BOTTLENECKS.md',s)
s=read('ARCHITECTURAL_ALTERNATIVES.md');intro='''## Primary new experiment: repeated sprite source rows — PIR-010

The accepted span compositor still decodes the same source row repeatedly when a sprite is enlarged. The isolated change introduces one automatic `last_source_y` sentinel per tile call. It recomputes keep/b0/b1/b2/b3 only when clamped source Y changes; each output row still merges those foreground bits with its own destination. No art, geometry, depth test, clipping, ordering, simulation or mapper change occurs. This is independent of the wall-key experiment below.

Candidate SHA256 **9F07A6282C0C9C046656C82965385C856C2A606A00CD26BBBCFD95BF7B88002A**. All **48,384** compiled sprite cases and **2,880** logical records match, including every warm-up/outlier. Emitted Bank0 shrinks **132 bytes**; local sprite frame stays38, persistent RAM/VRAM0 delta and observed stack maximum383. Twenty-three unmodified candidate validators pass. The remaining C-to-C# host validator initially rejects possibly-unassigned locals; a host-only initialization adjustment makes it pass without removing assertions or changing candidate ROM. Full details and failed log are retained.

'''+rowtable+'''

Active J update4 falls10,982,103→7,214,922 T (34.30%,3.07→2.02s); L update11 falls9,865,997→6,895,796 T (30.11%). The standard compiled corpus's candidate total drops1,223,189,428→940,973,696 T against accepted production (23.07% within that synthetic corpus, not a whole-game percentage). Sprite-free A/B/C/F and authored M whole-loop records have identical cycle counts. G's measured mean is23.77 T slower (0.0084%); its heavy warm-up improves, and the post-restart long average is not a steady eight-actor stress measure. No universal slowdown-free claim is made.

This is sufficient for **C — further optimization justified** and a P1 scoped kernel follow-up. It does not undermine the correctness or large gains of Solo's accepted implementation. It does not establish that the cooperative architecture should be promoted. Do not add its savings to the wall-key candidate; combined integration requires another measured replay.

'''
s=s.replace('## New exact dirty-key experiment — PIR-006',intro+'## Secondary exact dirty-key experiment — PIR-006')
s=s.replace('This supports **B/minor follow-up**, not a P1 optimization claim.','This remains a **P2** follow-up; the overall C verdict is driven by PIR-010, not this small wall-key change.')
write('ARCHITECTURAL_ALTERNATIVES.md',s)
s=read('VALIDATION_GAPS.md');start=s.index('The separate candidate audit initially');end=s.index('\n\nPIR-009',start)
s=s[:start]+'''The guarded-wall candidate initially failed artifact-reading validators because its build cache named a missing source/rom output. After the isolated output was placed at that configured path, all24 validators passed against its copied source. No production file or assertion changed.

The row-cache candidate passes23 validators unchanged. `validate_weapon_runtime` translates the compositor C into C#; C# cannot infer that sentinel255 forces the first valid source-Y row to assign keep/planes, and rejects their definite assignment. The isolated validator initializes **only translated host locals**, retains all geometry/pixel assertions, then passes. Its failed and corrected logs are retained. This is not an executed-Z80 mismatch; the independent48,384 actual compiled cases and2880 full records pass. A production integration must carry an equally strong host compatibility fix, rather than suppress the validator or claim it passed unchanged.''' +s[end:]
s+=scope
write('VALIDATION_GAPS.md',s)
s=read('FINAL_FINDINGS_AND_RECOMMENDATIONS.md')
s=s.replace('**B — APPROVED WITH MINOR FOLLOW-UP. Zero P0 and zero P1.** The accepted engine is sound in the inspected contract and tested corpus, and its44.99–88.89% improvement is independently reproduced. A guarded, small P2 opportunity warrants a narrow handoff. No fundamental redesign, cooperative promotion or gameplay alteration is justified.','**C — FURTHER OPTIMIZATION JUSTIFIED. Zero P0; one P1 (PIR-010).** The accepted engine is sound in the inspected contract and tested corpus, and its44.99–88.89% improvement is independently reproduced. A new exact sprite-row reuse kernel materially reduces the severe active tail and pistol/shotgun work while shrinking code. No fundamental redesign, cooperative promotion or gameplay alteration is justified.')
s=s.replace('|PIR-001|GOOD|','|PIR-010|P1|Exact sprite-row mask reuse; primary measured follow-up|\n|PIR-001|GOOD|',1)
finding='''## PIR-010 — reuse repeated foreground sprite rows

Location `platform/game_gear/video.c:89`, `game_gear_overlay_sprite_tile`, isolated `build-post-review-rowcache-source` and `rowcache-experiment.zip`; generated overlay ASM in that bundle. Reproduce `run_review.py rowcache_sprite`, the ten-route rowcache replay, and `analyze_candidate.py rowcache`. CONFIRMED48,384 compiled cases and2880 complete state/ray/VRAM records pass. The corrected profile identifies8,582,874 T in sprite overlay during J update4. MEASURED that interval falls10,982,103→7,214,922 T (34.30%); L update11 improves30.11%; pistol mean11.11%, shotgun5.26%, J2.12%, L1.70%. Sprite-free routes are cycle-identical; G measured mean worsens0.0084%, explicitly retained.

Root cause: enlarged sprites repeat clamped source Y, yet the accepted kernel re-decodes the same eight source-X pixels and plane masks each output row. PROVEN within one call: source-X/depth span/art/palette are constant, so repeated source Y has identical foreground masks. Cache keep/four planes only; re-merge each destination row. A255 sentinel ensures initialization before use. Never copy already merged destination rows or reuse across sprites/tiles.

Recommendation: integrate this focused kernel first. Expected benefit is the measured scene-dependent reduction, not60Hz or an architecture cure. MEASURED ROM **−132 Bank0 bytes**, persistent RAM0, VRAM0, same64-KiB package; local stack remains38, model peak42, whole-route max383, main closure588; no banking/public-ABI change. Compatibility risk is wrong cache lifetime/background ownership or future source heights reaching255. Require compiled clipping/alpha/depth/tie/background cases, full route equality and all validators. Host C# definite-assignment adaptation is needed; its assertions must remain. High confidence in bounded algebra, executed corpus and measured resources; hardware behavior remains the same unverified platform gate. **P1** due to34% reduction of a major active tail plus weapon-route gains with smaller code.

'''
s=s.replace('## Next action',finding+'## Next action')
s=s.replace('Continue normal GearRay development on the accepted verified ROM. If taking the small optimization, use [the bounded Solo prompt](SOLO_FOLLOWUP_IMPLEMENTATION_PROMPT.md).','The accepted verified ROM remains usable. Use [the bounded Solo prompt](SOLO_FOLLOWUP_IMPLEMENTATION_PROMPT.md) to integrate PIR-010 first; treat PIR-006 as a separate optional measured step.')
s+=scope
write('FINAL_FINDINGS_AND_RECOMMENDATIONS.md',s)
write('SOLO_FOLLOWUP_IMPLEMENTATION_PROMPT.md','''# Codex 6.1 Solo High — exact compositor follow-up

Work in `D:\\mano_projektai\\GearRay`. Read the post-implementation review README, PIR-010/PIR-006/PIR-007/PIR-009, ARCHITECTURAL_ALTERNATIVES and VALIDATION_GAPS. The verdict is **C — FURTHER OPTIMIZATION JUSTIFIED**, based on a measured small exact kernel, not a flawed production architecture. The accepted implementation is sound and its gains are reproduced.

This is a handoff specification, not evidence that integration is already performed. Confirm current source/ROM identity. New zombie artwork appeared during review; preserve it and do not replace current files with the frozen experimental source tree. Apply only the narrowly reviewed code changes to current source, then generate/test the user's current artwork. No commit/push unless separately requested.

## First: PIR-010 sprite source-row reuse

In `game_gear_overlay_sprite_tile`, horizontal source-X/depth eligibility, source pointer, palette and source size are fixed throughout one tile/sprite call. When consecutive clamped texture-Y values match, reuse the decoded foreground keep mask and four plane bytes. Continue merging every output row into its own current destination.

- Initialize an automatic last-source-Y sentinel to255, outside valid0..31.
- Compute/clamp texture Y as today. When it changes, decode that source row using the unchanged source-X span and alpha15 rules, assigning keep/b0/b1/b2/b3; then remember Y.
- On a repeat, skip only foreground decode. Keep destination-row merging, clipping, depth ties, near-ID mapping, source8/16/32, stable layering and sprite budget unchanged.
- Reset lifetime on every call. Never cache merged destination pixels, share state between sprites/tiles or add a persistent cache.

Reference: `evidence/rowcache-experiment.zip`, ROM SHA2569F07A6282C0C9C046656C82965385C856C2A606A00CD26BBBCFD95BF7B88002A. It passes48,384 actual compiled sprite cases and2880 complete records. Measured pistol/shotgun mean savings11.11/5.26%; J severe active interval10,982,103→7,214,922 T; L severe interval9,865,997→6,895,796 T. Bank0 shrinks132 bytes, local frame stays38, persistent RAM/VRAM unchanged. Sprite-free routes are cycle-identical; measured G mean is0.0084% slower. Do not advertise universal savings or60Hz.

The copied `validate_weapon_runtime` host translator initially fails C# definite assignment for keep/planes. The isolated fix initializes only translated host locals, retaining every sampling/geometry/pixel assertion. Either carry that narrow compatibility adjustment or provide an equally strong executed test; never disable the validator. The actual SDCC kernel's first visible row necessarily differs from sentinel255 and initializes its masks. Preserve the failed/corrected logs as evidence.

## Required acceptance for PIR-010

1. Fresh Release built from current source/assets; report the new hash and any intentional pixel changes caused solely by the user's new art. Compare optimization on/off using identical current assets, not old art versus new art.
2. All24 validators, with explicit ROM path and the documented host translator adjustment; all48,384 compiled sprite cases including repeat/nonrepeat Y, vertically clipped first visible row, differing background rows, alpha, both wall halves/depth ties, near-ID and8/16/32 sources.
3.32 warm-up+256 measured updates for all ten fixed16-update routes, full authoritative state/camera/rays/final-VRAM equivalence. Keep cold rows; report active tails separately. Retain substantial pistol/shotgun and severe J/L improvements; investigate materially worse sprite-free or other routes. Do not claim archived figures apply automatically to changed art.
4. Exact linked ROM/RAM/stack/VRAM/bank deltas; inspect emitted kernel and ensure no new mapper/port/public-ABI behavior. No stack or retained-state regression.
5. Interactive movement/fire/large-near-sprite/occlusion/pickup/pause/death/restart A/B. Physical hardware remains an available-hardware gate, not a fabricated pass.

## Optional second step: PIR-006 guarded wall offsets

Evaluate separately after the sprite kernel. Native wall sampling uses only upper3 hit-offset bits. Permit coarse offset comparison **only in columns with no current projected sprite**; all sprite dirty/removal, HUD, height, texture, side and validity gates remain. Preserve original signatures and actual rays. The accepted standalone guarded prototype costs36 Bank0 bytes and improves C7.660%, with small regressions up to0.863% shotgun. Combined gains are unmeasured and must not be added.

Never integrate the unrestricted shortcut: it leaves80 stale VRAM bytes when ray depth519→521 crosses actor depth520 while height31 and sampled texture column stay equal. `occlusion_guard_test.py` proves production and guarded candidate agree with a forced redraw. Extend that regression to left/right, appearance/removal and pickup. If combined benefit/trade-off is poor, retain only PIR-010.

## Measurement and document follow-up

Fix profiler return matching with explicit ABI stack-cleanup metadata; preserve physical bank bits on the world-initialization counter. Reproduce unchanged whole-loop timings and corrected child spans, and label G/J/L routes as episodes that can restart into authored state. Do not rewrite historical CSVs. Reconcile stale385-byte/no-emulator claims in maintained docs and identify the selected ROM by path/hash; the local ignored `rom/GearRay.gg` was still the historical baseline during review.

No cooperative promotion, fixed-time/control change, offscreen AI deletion, reduced art/view, uniform angles, unsafe copy, bank reshuffle or broad rewrite. Deliver source diff, full current-asset comparison, resource evidence and precise limitations for review. Leave accepted production unchanged if a required equivalence or benefit gate fails.
''')
import re
for p in D.glob('*.md'):
    text=p.read_text(encoding='utf-8')
    text=re.sub(r'\b(all|All|of|and|for|with|by|the|after|before|than|roughly|approximately|complete|Full|full|costs|saves|retains|retained|reproduces|passes|pass|stays|shrinks|leaves|same|maximum|minimum|measured|observed|candidate|production|source|sentinel|height|depth|offset|actor|index|count|frame|below|over|adds|initial|RAM|VRAM|Bank)(?=\d)',r'\1 ',text)
    text=re.sub(r'(?<=\d)(?=(?:bytes|records|compiled|million|refreshes|updates|cases)\b)',' ',text)
    text=text.replace('SHA256','SHA-256')
    text=re.sub(r'SHA-256(?=[0-9A-Fa-f])','SHA-256 ',text)
    p.write_text(text,encoding='utf-8')
print('Refined all reports for final C verdict, row-cache evidence and concurrent-art scope.')
