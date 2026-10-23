# Current gameplay behavior

This page owns gameplay contracts. [Architecture](ENGINE_ARCHITECTURE.md), [banking](ROM_BANKING.md) and [measurements](PERFORMANCE_BASELINE.md) own implementation/resource details.

## Input and movement

Up/Down move forward/backward; Left/Right rotate. Button 2 with Left/Right strafes. A non-strafe Button 2 press/release requests interaction on release. Button 1 fires on a fresh edge; held input does not auto-fire. START requests pause on a fresh edge. `input_blocked` retains UI-held gameplay buttons until release, preventing UI holds from becoming gameplay actions.

Movement uses signed fixed-point coordinates with scale 256, speed 74 per completed movement update and radius 32. Forward/backward and strafe use the current direction/plane; combined diagonal movement uses the existing 177/256 normalization. Collision tests the four radius corners against walls and closed doors, moving X then Y to permit sliding. Out-of-bounds world access is solid VOID. Rotation follows the exact legacy camera graph; there is no new uniform-angle approximation.

## Weapons and pickup

The player starts with the pistol. Two weapon IDs and an owned mask represent pistol/shotgun. The independent shotgun world pickup does not consume a zombie slot. First pickup acquisition grants ownership, immediately equips shotgun and clears the old pose before accepting a fresh fire edge from that update. Already-owned pickup state does not switch selection.

The held HUD uses a two-update firing pose. Combat resolves the previous update's pending shot against the current camera/world/rays, then latches the current fire request. Pause does not advance this pending work. The pistol acquires the nearest qualifying projected target, respects wall occlusion and uses the preserved 12/6/4/3 damage bands. Shotgun tests three screen-space lines against the same projected body footprint, applies its 12/6/2 bands and preserves strict wall-depth ties. These are bounded gameplay rules, not a general physics or ammunition system. Ammo, audio and progression are not implemented by this cleanup.

## Zombies, health and corpses

`WorldSprite` is **9 bytes** under the accepted toolchain. Capacity is **8** records (72 storage bytes), plus a separate renderer entry for the pickup. The world contains only the existing zombie implementation; zombie_02 is **art only**.

Sprite timers update each completed gameplay update. All live actors remain eligible for AI, including offscreen actors; the all-actor AI pass occurs every fourth completed update. Awareness uses distance hysteresis (activation 963, loss 1260) and line of sight. Chase state, hit counts, attack cooldown and walking/attack phases use the existing packed fields/masks. Door-aware movement separates the player and living zombies.

Player health starts at 100. Melee includes distance 280, applies 20 damage, updates health HUD and damage shake, and retains the existing two-AI-tick cooldown/presentation rules. A lethal pass exits before interaction/raycast/drawing continues. Zombies have cumulative health 12, temporary hit/death presentations and persistent corpse state. Nearby corpse merging and door crushing keep bounded storage; hidden/distant corpse LOD does not delete the underlying gameplay state. No offscreen-AI deletion is enabled.

## Doors, switch, death and restart

Standard registered doors toggle via the interaction ray. Closing is prevented when the player's collision extent occupies the target doorway; zombie/corpse crushing retains its current relocation/merge rules. The red door is controlled by its switch, not direct door interaction. Switch animation changes terminal materials and preserves geometry unless door state changes.

At death the pending shot is cleared, the timed Game Over presentation runs, and the outer initialization loop shows the startup logo and recreates the authored world/player/camera/input/weapon state. Health returns to 100 and the selected weapon to pistol. Restart clears processed keys, previous_keys and input_blocked to zero. The first gameplay poll reads the current hardware state, so a still-held Button 1 can become a fresh processed fire edge. No gameplay action queue survives restart. Game-over timing and the compiled restart playthrough are tested separately.

## Pause map and weapon selection

START enters the blocking pause UI; a fresh START edge leaves it. Holding START does not repeatedly enter/exit. The UI starts in weapon focus. Left/Right select an owned weapon circularly. Up selects map focus; Down returns weapon focus. Button 1 on map focus enters map browsing; directions pan with existing repeat delay and Button 2 leaves browsing. The map displays the current player orientation and corpse markers.

Gameplay timers, AI divider, positions, pending shot, health and simulation state freeze during UI polls. Weapon selection is intentional UI state. On exit, held gameplay buttons are blocked until release; processed key history cannot turn a Button 2 release into interaction. Restore blanks/rebuilds display and renderer caches using frozen rays, restores health/HUD/shake and returns to the normal loop without a gameplay tick or session reinitialization.

Production timing is one update per completed synchronous loop. Rendering cost changes real-time speed; display 60 FPS is not gameplay 60 updates/s. Complete interactive A/B and physical Game Gear qualification remain pending. See [TESTING](TESTING.md) for the distinction between host, compiled, GUI and hardware evidence.
