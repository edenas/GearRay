"""Verify content fingerprints in an isolated Release source copy.

This intentionally mutates only copied PNG metadata, keeps file length and
mtime fixed, and restores the exact input bytes in a finally block.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import subprocess
import time
import zlib
from pathlib import Path


def run(args: list[str], cwd: Path, log: Path) -> str:
    completed = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    log.write_text(completed.stdout + completed.stderr, encoding="utf-8")
    if completed.returncode:
        raise RuntimeError(f"Command failed ({completed.returncode}): {args}; log={log}")
    return completed.stdout + completed.stderr


def mutate_text_metadata(path: Path) -> None:
    data = bytearray(path.read_bytes())
    offset = 8
    while offset < len(data):
        length = int.from_bytes(data[offset:offset + 4], "big")
        kind = bytes(data[offset + 4:offset + 8])
        start = offset + 8
        end = start + length
        if kind == b"tEXt":
            payload = data[start:end]
            separator = payload.find(b"\0")
            if separator < 0 or separator + 1 >= len(payload):
                raise RuntimeError(f"No editable tEXt value in {path}")
            index = start + separator + 1
            data[index] = ord("Z") if data[index] != ord("Z") else ord("Y")
            crc = zlib.crc32(bytes(data[offset + 4:end])) & 0xFFFFFFFF
            data[end:end + 4] = struct.pack(">I", crc)
            path.write_bytes(data)
            return
        offset = end + 4
    raise RuntimeError(f"No tEXt chunk in {path}")


def configure(root: Path, build: Path, log: Path) -> str:
    return run([
        "cmake", "-S", str(root), "-B", str(build), "-G", "Ninja",
        "-DCMAKE_BUILD_TYPE=Release", "-DGEARRAY_PROFILE_RENDERER=OFF",
        "-DGEAR_RAY_ROM_FILENAME=GearRay.gg", f"-DGEAR_RAY_ROM_DIR={root / 'rom'}",
    ], root, log)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    options = parser.parse_args()
    root = options.source_root.resolve()
    evidence = options.evidence_dir.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    build = root / "build" / "release"
    generated = build / "generated"
    configure(root, build, evidence / "preserved-mtime-baseline-configure.log")
    run(["cmake", "--build", str(build)], root,
        evidence / "preserved-mtime-baseline-build.log")
    records = []
    inputs = [
        (root / "assets/sprites/enemies/zombie/zombie_02_standing_32x32.png",
         build / "zombie_asset_inputs.sha256", generated / "zombie_visuals_assets.c"),
        (root / "assets/sprites/weapons/shotgun_held.png",
         build / "zombie_asset_inputs.sha256", generated / "shotgun_held.c"),
    ]
    canonical = hashlib.sha256((root / "rom" / "GearRay.gg").read_bytes()).hexdigest()
    for index, (asset, fingerprint_file, generated_file) in enumerate(inputs, 1):
        original = asset.read_bytes()
        original_hash = hashlib.sha256(original).hexdigest()
        original_stat = asset.stat()
        fingerprint_before = fingerprint_file.read_text(encoding="ascii").strip()
        generated_before = generated_file.stat().st_mtime_ns
        mutation_log = evidence / f"preserved-mtime-{index}-mutation-build.log"
        restore_log = evidence / f"preserved-mtime-{index}-restore-build.log"
        try:
            mutate_text_metadata(asset)
            os.utime(asset, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))
            if len(asset.read_bytes()) != len(original):
                raise RuntimeError(f"Mutation changed PNG byte length: {asset}")
            if asset.stat().st_mtime_ns != original_stat.st_mtime_ns:
                raise RuntimeError(f"Mutation changed PNG mtime: {asset}")
            changed_hash = hashlib.sha256(asset.read_bytes()).hexdigest()
            configure(root, build, evidence / f"preserved-mtime-{index}-configure.log")
            fingerprint_changed = fingerprint_file.read_text(encoding="ascii").strip()
            if fingerprint_changed == fingerprint_before:
                raise RuntimeError(f"Configure missed preserved-mtime content change: {asset}")
            mutation_output = run([
                "cmake", "--build", str(build)
            ], root, mutation_log)
            generated_after_mutation = generated_file.stat().st_mtime_ns
            if generated_after_mutation <= generated_before:
                raise RuntimeError(f"Generator output was not refreshed for {asset}")
            if "Generating explicit security/scientist authored sprite manifest" not in mutation_output:
                if "shotgun_held" in asset.name and "Generating generated/shotgun_held.c" not in mutation_output:
                    raise RuntimeError(f"Shotgun generator did not run for {asset}")
                if "zombie_02" in asset.name and "Generating explicit security/scientist authored sprite manifest" not in mutation_output:
                    raise RuntimeError(f"Zombie generator did not run for {asset}")
        finally:
            asset.write_bytes(original)
            os.utime(asset, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))
        if hashlib.sha256(asset.read_bytes()).hexdigest() != original_hash:
            raise RuntimeError(f"Exact PNG restore failed: {asset}")
        if asset.stat().st_mtime_ns != original_stat.st_mtime_ns:
            raise RuntimeError(f"PNG mtime restore failed: {asset}")
        configure(root, build, evidence / f"preserved-mtime-{index}-restore-configure.log")
        restore_output = run([
            "cmake", "--build", str(build)
        ], root, restore_log)
        restored_fingerprint = fingerprint_file.read_text(encoding="ascii").strip()
        rom_hash = hashlib.sha256((root / "rom" / "GearRay.gg").read_bytes()).hexdigest()
        if restored_fingerprint != fingerprint_before:
            raise RuntimeError(f"Fingerprint did not return to exact baseline for {asset}")
        if rom_hash != canonical:
            raise RuntimeError(f"Restored candidate ROM differs for {asset}: {rom_hash}")
        records.append({
            "input": str(asset.relative_to(root)).replace("\\", "/"),
            "original_sha256": original_hash,
            "mutated_sha256": changed_hash,
            "preserved_bytes": len(original),
            "preserved_mtime_ns": original_stat.st_mtime_ns,
            "fingerprint_before_sha256": fingerprint_before,
            "fingerprint_mutated_sha256": fingerprint_changed,
            "fingerprint_restored_sha256": restored_fingerprint,
            "generated_output": str(generated_file.relative_to(root)).replace("\\", "/"),
            "generated_output_mtime_refreshed": generated_after_mutation > generated_before,
            "restored_rom_sha256": rom_hash,
            "restored_build_output_log": str(restore_log),
        })
    (evidence / "preserved-mtime-fingerprints.json").write_text(
        json.dumps({"source_root": str(root), "candidate_sha256": canonical,
                    "cases": records, "status": "PASS"}, indent=2), encoding="utf-8")
    print("Preserved-mtime content fingerprint checks PASS")
    for item in records:
        print(item["input"], item["fingerprint_before_sha256"],
              "->", item["fingerprint_mutated_sha256"],
              "->", item["fingerprint_restored_sha256"])


if __name__ == "__main__":
    main()
