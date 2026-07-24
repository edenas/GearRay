# Third-Party Notices

GearRay's own source code, documentation, and confirmed project assets are
licensed under the [MIT License](LICENSE). The tools and libraries below are
separate projects and retain their own copyright and licensing terms.

GearRay does not currently vendor these projects. They are installed
separately and used to build the ROM. This notice also records components that
may be present in a generated GearRay ROM.

## SDCC

- **Purpose:** Compiles and links GearRay's C sources for the Z80 target.
- **Upstream:** [Small Device C Compiler](https://sdcc.sourceforge.net/)
- **License:** GNU General Public License; consult the license distributed with
  the installed SDCC version for its exact version and component terms.
- **Required notice:** No SDCC executable or source is distributed in this
  repository. Redistributors of SDCC itself must comply with SDCC's GPL terms.
  Compiler output is not made GPL solely because SDCC produced it; any linked
  runtime or library terms still apply independently.

GearRay Engine Foundation v1.0.0 was tested with SDCC 4.6.0.

## devkitSMS

- **Purpose:** Provides the Sega Master System/Game Gear development toolkit
  containing SMSlib, the startup CRT, and ROM-packaging utilities.
- **Upstream:** [sverx/devkitSMS](https://github.com/sverx/devkitSMS)
- **License:** Component-specific. devkitSMS publishes a `LICENSES.txt` file
  that identifies the license for each included component.
- **Required notice:** Preserve the notices and licenses belonging to any
  devkitSMS component that is redistributed. GearRay does not treat the
  toolkit as being covered by GearRay's MIT license.

The exact devkitSMS revision used for Engine Foundation v1.0.0 has not yet been
recorded and must be confirmed before producing a reproducible release
toolchain archive.

## SMSlib

- **Purpose:** Supplies Game Gear hardware initialization, input, video, text,
  and other platform access used by GearRay.
- **Upstream:** Included in
  [sverx/devkitSMS](https://github.com/sverx/devkitSMS/tree/master/SMSlib)
- **License:** Dedicated to the public domain using an Unlicense-style notice,
  according to the `SMSlib/LICENSE` and devkitSMS `LICENSES.txt` files.
- **Required notice:** Preserve the upstream license when redistributing
  SMSlib source or binaries. devkitSMS notes that optional ZX7 decompression
  routines have their own notice requirements. GearRay does not knowingly call
  those routines, but a release maintainer must confirm the contents of the
  linked SMSlib build before binary distribution.

## devkitSMS CRT (`crt0_sms`)

- **Purpose:** Supplies the Game Gear ROM startup code, interrupt vectors,
  memory initialization, Sega mapper support, and entry into GearRay's
  `main`.
- **Upstream:** Included in
  [sverx/devkitSMS](https://github.com/sverx/devkitSMS/tree/master/crt0)
- **License:** GNU General Public License version 2 or later, with the special
  linking exception included in `crt0/src/crt0_sms.s`.
- **Required notice:** Preserve the CRT copyright, GPL text, and special
  exception when redistributing the CRT itself. The exception states that
  linking the CRT with files compiled by SDCC does not, by itself, cause the
  resulting executable to be covered by the GPL. Other reasons for GPL
  coverage, if any, remain unaffected.

## `makesms`

- **Purpose:** Converts the linked Intel HEX image into the final Sega
  Master System/Game Gear ROM image and applies the expected ROM packaging.
- **Upstream:** Included in
  [sverx/devkitSMS](https://github.com/sverx/devkitSMS/tree/master/makesms)
- **License:** Dedicated to the public domain using an Unlicense-style notice,
  according to `makesms/LICENSE`.
- **Required notice:** Preserve the upstream license when redistributing the
  utility or its source. The utility is not included in this repository.

## Release Checklist

Before distributing a GearRay ROM or toolchain bundle:

1. Record the exact SDCC and devkitSMS versions or commits.
2. Confirm which SMSlib objects and optional routines are linked.
3. Include the applicable upstream license and exception texts.
4. Keep GearRay's MIT notice and the asset provenance record with the release.

This file is an attribution and compliance record, not legal advice.
