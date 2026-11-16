# Authored artwork inspection — refreshed 2026-11-16

**READY FOR IMPLEMENTATION.** The owner supplied both scientist attack frames and the corpse frame and explicitly resumed handoff preparation. All three are verified 32×32 with binary alpha. The old color error is corrected in the source. This replaces the earlier missing-art/pending-color status; it is input verification, not in-game acceptance.

No images were edited by the agent. All **122** current assets, including the new editor copies, are hashed in [ready-input-identity.json](evidence/ready-input-identity.json). [Current image details](evidence/ready-artwork-inspection.json) cover **81 PNGs** in the zombie/weapon trees. The table below lists the **52 direct inputs: 45 zombie files and seven weapon files**. Editor copies remain protected but are not automatic runtime inputs.

Alpha is binary (0/255) for every direct input. Dimensions are decoded. Changed means current RGBA pixels differ from tracked HEAD; hashes identify the exact current source files. Original initial-identity.json, artwork-inspection.json, architecture-evidence.json, generator rejection logs and planning-completion.json remain dated pre-correction evidence. Never use their older art identities to overwrite current PNGs.

| File | Actual size | Git / pixel comparison | SHA-256 |
| --- | --- | --- | --- |
| `zombie_01_attack_01.png` | 8×8 | unchanged | `6847e340c772ceb4093096d8119a75c26804fca1eae602fd751f58a6bb538a70` |
| `zombie_01_attack_01_32x32.png` | 32×32 | unchanged | `3ba499b2539e421ba5b70671e1b6aaa6158796a7fa98b9000498a5fec446ffa1` |
| `zombie_01_attack_02.png` | 8×8 | unchanged | `a9df2752d252fcca1bfdc28a77190846ee822698109d70146c4cb98eaf40af2b` |
| `zombie_01_attack_02_32x32.png` | 32×32 | unchanged | `e436edb085d42bccd0e765a69ec4566037b7434261dc942eee1b243a0ac3ebc4` |
| `zombie_01_corps.png` | 8×8 | unchanged | `9291dfbb37af7c9b3476003f81dc222f696cc61a1a007a972a1a31e5ee91e347` |
| `zombie_01_corps_16x16.png` | 16×16 | unchanged | `177e19ca93299e3b02a1829d6dded86fe660bb976833957dce644897097616d8` |
| `zombie_01_corps_32x32.png` | 32×32 | unchanged | `b435d1d11068f240439d0c9c770478ec663e874c03452e43530cd4db0182fbb9` |
| `zombie_01_shot_01.png` | 8×8 | unchanged | `441a492568cc469c042b08c779d92673db54b83e7d06b586881e03ff08d60d93` |
| `zombie_01_shot_01_16x16.png` | 16×16 | pixels changed | `7e0790d1147de68846ca448167b273cb4f0b9e49cabe01e16dbff1a0473a81f7` |
| `zombie_01_shot_01_32x32.png` | 32×32 | pixels changed | `26b03241c02a136003b737cff8c8cc75877d6d6a70c7cfa3707c78fc400ae355` |
| `zombie_01_shot_02.png` | 8×8 | unchanged | `491bc27aad2a9069c169a343783aecd6bfa1bb754a1439a7b2fe47187a816179` |
| `zombie_01_shot_dead.png` | 8×8 | unchanged | `67771b12bb41a8d7b5b605212c6b963cc6c4b698f0c88a032dba0172fd02e861` |
| `zombie_01_shot_dead_16x16.png` | 16×16 | unchanged | `04f50613ee572ec90c082f937f2d8c4ae9db21f4339b2c8c17e49e40595c270b` |
| `zombie_01_standing.png` | 8×8 | unchanged | `98eae1215dea2cbb790d8871029402447b1e863f9ac95f51e16889d3a9cc6972` |
| `zombie_01_standing_16x16.png` | 16×16 | unchanged | `ab9e88279fe7fef5aa3b32f26f28d706db63e0188a6c155476f435af0b7ccfaa` |
| `zombie_01_standing_32x32.png` | 32×32 | unchanged | `ae5d949f7f7bc62464480449695db6346a24de225a163bbc79fc84117d540dda` |
| `zombie_01_standing_attack_32x32.png` | 32×32 | pixels changed | `d55a3b11e8d21d6323c65fd0348d88cc7265efafdaffe5b5643b00d3a15c56c5` |
| `zombie_01_walking_01.png` | 8×8 | unchanged | `ca21b8dd5646b34a8d0515c0b8d5d9a6d28863fa484e47acf050bb821e5f52a7` |
| `zombie_01_walking_01_16x16.png` | 16×16 | unchanged | `73aa581c082c35edc04a3ac6f547050f40f3abf89307dfc37de0f2a027c7a6b0` |
| `zombie_01_walking_01_32x32.png` | 32×32 | unchanged | `f78986131cdd370861a8d8966ab1a92807911234afd14cd8d54be6da7ac42db2` |
| `zombie_01_walking_02.png` | 8×8 | unchanged | `498e9f766a3a6636d195608148883524f4fe3352f40dde46cef84fc1efe21ebd` |
| `zombie_01_walking_02_16x16.png` | 16×16 | unchanged | `5018c3d478cf432348011c28cb9f67e7cec29c3382904fb5d3f319aa36b3ce33` |
| `zombie_01_walking_02_32x32.png` | 32×32 | unchanged | `a63e0be3f9179d29e1b98c9922882bc7269d9bc4ce2878e57fc5b78d7b0b9918` |
| `zombie_02_attack_01.png` | 8×8 | unchanged | `cc8a2be105dfaa38f321599873d98ca6e3dc063d776ce8c509c6985beda97e04` |
| `zombie_02_attack_01_32x32.png` | 32×32 | new, untracked | `6c02643a121e75d900dc0fc56855ceb22cfe1f59d4caad1876a76d4da5c97a0c` |
| `zombie_02_attack_02_32x32.png` | 32×32 | new, untracked | `5fd0f9226092bd55035ca175854a0898ce3bb3f96ef693060cbdd4dab6f08021` |
| `zombie_02_corps.png` | 8×8 | unchanged | `968e062e6cfd45b6b6b0c3f20c96a1edbd27750039352f429b01d509e0edd017` |
| `zombie_02_corps_16x16.png` | 16×16 | unchanged | `3bb701694e8b4d2b4c4450cd70d75e82ced8386e1ca453b486b5ce91009f2577` |
| `zombie_02_corps_32x32.png` | 32×32 | new, untracked | `48b3f424862a8fc5b21169b9ad2b5361828019cab74aeb1f1520a553017b83d1` |
| `zombie_02_shot_01.png` | 8×8 | unchanged | `7fd15bff9b6c7c7fd868014acd253be6e6df4a6b1f09f407078c3b81f608991d` |
| `zombie_02_shot_01_16x16.png` | 16×16 | new, untracked | `2ccddc45e1ee9caf5670397b446762be85c02fe86ab82e1b9698f579f5526087` |
| `zombie_02_shot_01_32x32.png` | 32×32 | new, untracked | `0ff74954913c4a82309e08c5f7d0b82940979fa4fe2ca641b44d1e886bf31047` |
| `zombie_02_shot_02.png` | 8×8 | unchanged | `cdf45cff29a8f9cf453322f4766201dfeac835baa5026b466668a01cbd3e5cfc` |
| `zombie_02_shot_dead.png` | 8×8 | unchanged | `e42ff9dd4e251da4931ed0869c0f57ae4c781cdfdc492fd07cbb172ce1bdc0c0` |
| `zombie_02_shot_dead_16x16.png` | 16×16 | new, untracked | `623ade932c3eb5cb56df2b46618edba61a6173aaa2a5818ce0b90d99cf6b080e` |
| `zombie_02_standing.png` | 8×8 | unchanged | `2e2e9dfa2bdeb7127055e5a88c626d53e98ce307c27456c3091b61b840203ed0` |
| `zombie_02_standing_16x16.png` | 16×16 | unchanged | `27a5f188c93265880e2794c059c04596e386bbf7b9c935add70b3b08efa1f9eb` |
| `zombie_02_standing_32x32.png` | 32×32 | new, untracked | `c331fddf2a0e625c0596467118887945b49ac87e04e374b57b19c861da31a9c7` |
| `zombie_02_standing_attack_32x32.png` | 32×32 | new, untracked | `9c00271d649df5ee06a723eedd1ecc9752b058aea00b6879cd2c99c35ba420f6` |
| `zombie_02_walking_01.png` | 8×8 | unchanged | `3a09a608138a0b7f135ec10b1231f51618044820d5257f35219c02e002b92468` |
| `zombie_02_walking_01_16x16.png` | 16×16 | unchanged | `142342ce0a0445c5e76da2c23b0ca76102e817f171b90f3299d76e0cde389047` |
| `zombie_02_walking_01_32x32.png` | 32×32 | new, untracked | `e3e20872b5c17fca05a06aaf7ba2f660650e4fbff7d58c822baccc0f51b1cfb8` |
| `zombie_02_walking_02.png` | 8×8 | unchanged | `1c15f16f806531b708757a4f7bf6f8375407d752c9b576d163d0f10f30daf6da` |
| `zombie_02_walking_02_16x16.png` | 16×16 | unchanged | `e4c672cf2cfd0501f433b7d99a094686b2e4af903b0558228b11db8917159b2a` |
| `zombie_02_walking_02_32x32.png` | 32×32 | new, untracked | `60faec43b682584b8d186f4731269d8001135ab01a62729a51b534e3b9eee28a` |
| `gun_12x12.png` | 12×12 | unchanged | `c57da998706b2aa7c7e53effa4698bb2900336aa8728733d3298f0fddf1faae4` |
| `gun_shoot_12x12.png` | 12×12 | unchanged | `6771c3c91e213ea51ade8ae5eab92fb686e12eb706ce914c59a6388c9f73a8b4` |
| `pick_up_shotgun.png` | 16×16 | unchanged | `1b747722508e39baca417dc2a1edd533eb98f9c5e56ac201665e767d28d952b4` |
| `pistol.png` | 16×16 | unchanged | `cfec151e56ac979d24897a9b63a27436eab96492fd18dff12b05e91d0baf57c8` |
| `shotgun.png` | 16×16 | unchanged | `2ae5a0ab9c0e8de5f0440de96231535061e9f1d7bb33a666d56353fa419af5d1` |
| `shotgun_held.png` | 20×16 | pixels changed | `783e345527752eef2ae815331494a85efd395ea088fa0e356a81fd4a5babbfaf` |
| `shotgun_held_shoot.png` | 20×16 | pixels changed | `30dd22ca80cf4332755943255178b4040a58116af4a57eb42ca142b727db25f0` |

## Completed inputs and generator work

All selected scientist poses are now present: seven used 8×8 base sources, six 16×16 sources and eight 32×32 poses. The new attacks each contain 483 opaque pixels; the corpse contains 370. Both species have authored near standing frames to integrate. Preserve unused frames too; no substitutes are needed.

The two held shotgun images are still 20×16; pickup/pause sources remain unchanged 16×16. Current content replaces historical generated expectations. Recheck generated output during implementation rather than claiming these PNG checks prove a playable ROM.

The earlier bad color at scientist walking_02_32×32 (5,29) and shotgun_held_shoot (4,2)/(5,2), zero-based, is verified as opaque #000000. No #03000F occurs in any of the 52 direct inputs. **Do not introduce the earlier proposed alias.**

Required explicit generator mappings: scientist base white #FFFFFF → existing index 12; near gray #797878 → existing index 3; new attack dark gray #4D4D4D → existing index 2. Each attack contains 14 pixels of the last color. The weapon branch already uses these gray mappings; extend the zombie branch without changing hardware palette values or PNGs. This is scoped implementation work, not an unresolved owner-art decision.

[Artwork readiness](evidence/artwork-readiness.json) includes exact new-frame hashes, colors, corrected coordinates and the change set since the original inspection. Four original direct files changed during owner editing (both held-shotgun files and both scientist 32×32 walk frames); the current versions are authoritative. Three direct frames and five protected editor copies were added.
