# Contributing to GearRay

Keep changes focused, deterministic and consistent with current ownership. Read the [documentation hub](docs/README.md), [development guide](docs/DEVELOPMENT_GUIDE.md), [architecture](docs/ENGINE_ARCHITECTURE.md), [banking](docs/ROM_BANKING.md) and [build guide](docs/BUILDING.md).

For architecture, performance, dependency, banking or stable-contract changes, explain the problem, current evidence, proposed ownership, ROM/RAM/stack/timing effects and validation before implementation. Small fixes can use a focused pull request. Avoid unrelated changes in performance-sensitive code.

Run `build.bat` and the complete 24-validator [testing entry point](docs/TESTING.md); use `build-profile.bat` separately when needed. Record actual compiled checks, ROM identity, resource effects and remaining human/hardware limits. Temporary experiments belong in build/experiments/name and must not clobber canonical rom/GearRay.gg or rewrite dated evidence. Do not run historical source-mutating setup scripts against current work.

Preserve original artwork and user work. Document origin/license/notices for new media or third-party dependencies. Update the relevant single topic owner and Unreleased changelog for user-visible behavior. Historical reports retain their dates, bytes and rejected decisions.

A pull request should lead with the concrete problem and resulting behavior, then the relevant validation and trade-offs. Do not claim universal speedups, fixed gameplay FPS or physical hardware acceptance from emulator automation. By contributing, you agree that your contribution may be distributed under the project's [MIT License](LICENSE).
