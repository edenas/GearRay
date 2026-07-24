# Contributing to GearRay

Thank you for helping improve GearRay. Contributions should strengthen the
project without obscuring its small, deterministic architecture.

## Development Principles

- **Readability:** Prefer direct code and descriptive names over cleverness.
- **Deterministic behaviour:** The same state and input must produce the same
  result.
- **Measure first:** Profile, inspect generated SDCC code, or establish a
  reproducible baseline before optimizing.
- **Maintainability:** Accept complexity only when it provides a measurable
  benefit.
- **Architecture before implementation:** Identify state ownership, module
  responsibility, data flow, and hardware constraints before adding a system.
- **Preserve working contracts:** Do not rewrite stable renderer, movement,
  input, or banking systems merely to follow current trends.

## Before Starting

For a small fix, open a focused pull request. For architectural changes,
performance work, new dependencies, or changes to the Engine Foundation
contracts, open an issue first and describe:

1. the problem;
2. the current evidence or measurement;
3. the proposed ownership and module boundary;
4. expected ROM, RAM, stack, performance, and behavioural effects;
5. how the result will be validated.

Review the [engine architecture](docs/ENGINE_ARCHITECTURE.md),
[ROM banking contract](docs/ROM_BANKING.md), and
[build guide](docs/BUILDING.md) before changing those areas.

## Making a Change

- Keep each change focused.
- Follow the naming, formatting, and module style already present.
- Avoid unrelated cleanup in performance-sensitive code.
- Add comments for hardware constraints, invariants, and non-obvious decisions,
  not for self-evident statements.
- Do not add third-party code or assets without documenting their origin,
  author, license, and required notices.
- Update public documentation when behaviour or supported workflows change.
- Add a changelog entry for user-visible changes.

## Validation

Run the checks relevant to the change:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/validate_final_controls.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tools/validate_renderer_equivalence.ps1
```

Build both configurations when changing C, generated assets, CMake, or the
toolchain:

```bat
build.bat
build-profile.bat
```

Renderer and hardware-facing changes should also be checked in an emulator and,
when possible, on original Game Gear hardware. Record ROM size, bank usage,
warnings, relevant measurements, and visual results in the pull request.

## Pull Requests

A pull request should explain:

- what changed and why;
- which files and responsibilities are affected;
- what was deliberately left unchanged;
- the validation performed and its results;
- any compatibility, licensing, provenance, or hardware concerns.

By contributing, you agree that your contribution may be distributed under the
project's [MIT License](LICENSE).
