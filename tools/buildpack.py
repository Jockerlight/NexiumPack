#!/usr/bin/env python3
"""Builds the server resource pack from pack/ into one .zip.

    python tools/buildpack.py                 -> build/NexiumPack.zip
    python tools/buildpack.py --out x.zip     -> another file
    python tools/buildpack.py --manifest URL  -> also build/pack.json for NexiumPack
                                                 ({"url": URL, "sha1": ...})

In the --manifest link, {short} becomes the first 12 characters of the
pack's SHA-1 (the release workflow names each release pack-{short}).

The zip is the same byte for byte for the same files (sorted names, fixed
dates), so its SHA-1 only changes when the pack really changes and players
only download it again then.

Checks before zipping: pack.mcmeta is there, every .json parses, and every
texture a model names exists (a missing one shows as the purple/black
"missing texture" in game).
"""
import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "pack"
DEFAULT_OUT = ROOT / "build" / "NexiumPack.zip"
SKIP = {".DS_Store", "Thumbs.db", "desktop.ini"}
FIXED_DATE = (2020, 1, 1, 0, 0, 0)


def files():
    for p in sorted(SRC.rglob("*")):
        if p.is_file() and p.name not in SKIP and not p.name.startswith("."):
            yield p


def check(paths):
    errors = []
    rel = {p.relative_to(SRC).as_posix() for p in paths}
    if "pack.mcmeta" not in rel:
        errors.append("pack.mcmeta is missing")
    for p in paths:
        r = p.relative_to(SRC).as_posix()
        if p.suffix in (".json", ".mcmeta"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except Exception as e:  # noqa: BLE001
                errors.append(f"{r}: not valid JSON ({e})")
                continue
            # assets/<ns>/models/...: every texture it names must exist
            parts = r.split("/")
            if len(parts) > 3 and parts[0] == "assets" and parts[2] == "models":
                for tex in (data.get("textures") or {}).values():
                    if not isinstance(tex, str) or tex.startswith("#"):
                        continue
                    ns, _, path = tex.partition(":") if ":" in tex else ("minecraft", "", tex)
                    if ns == "minecraft":
                        continue  # vanilla texture: comes with the game
                    if f"assets/{ns}/textures/{path}.png" not in rel:
                        errors.append(f"{r}: texture {tex} not found (assets/{ns}/textures/{path}.png)")
    return errors


def build(out):
    paths = list(files())
    errors = check(paths)
    if errors:
        for e in errors:
            print("ERROR", e)
        sys.exit(1)
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in paths:
            info = zipfile.ZipInfo(p.relative_to(SRC).as_posix(), FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, p.read_bytes())
    data = out.read_bytes()
    return len(paths), len(data), hashlib.sha1(data).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--manifest", metavar="URL", help="also write pack.json next to the zip with this download link ({short} = first 12 characters of the SHA-1)")
    a = ap.parse_args()
    n, size, sha1 = build(a.out)
    print(f"{a.out}: {n} files, {size / 1024:.1f} KB, SHA-1 {sha1}")
    if a.manifest:
        url = a.manifest.replace("{short}", sha1[:12])
        m = a.out.parent / "pack.json"
        m.write_text(json.dumps({"url": url, "sha1": sha1, "size": size}) + "\n", encoding="utf-8")
        print(f"{m}: {url}")


if __name__ == "__main__":
    main()
