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

Made small on purpose (players download it on join): every JSON is
minified, every PNG is re-saved as the smallest lossless PNG (an indexed
palette when it has 256 colours or fewer), nothing else goes in.

Checks before zipping: pack.mcmeta is there, every .json parses, and every
texture a model names exists (a missing one shows as the purple/black
"missing texture" in game).
"""
import argparse
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

from PIL import Image

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
            if r == "pack.mcmeta":
                errors += check_overlays(data)
    return errors


def _major(v):
    return v[0] if isinstance(v, list) else v


def check_overlays(meta):
    """The overlay rules of Minecraft 1.21.9+ (resource pack format 65).

    A pack.mcmeta that breaks them is rejected as a whole: the game drops
    the entire pack, players see missing textures everywhere.
      - The pack supports formats below 65 (min_format < 65): old clients
        read only "formats", so every overlay entry needs it, and new
        clients only accept "formats" when at least one overlay entry
        reaches below 65 (that is what the nx_compat entry is for).
      - The pack starts at 65 or later: no entry may have "formats".
      - "formats" must say the same range as min_format / max_format.
    """
    errors = []
    entries = (meta.get("overlays") or {}).get("entries") or []
    if not entries:
        return errors
    pack_min = _major(meta.get("pack", {}).get("min_format", meta.get("pack", {}).get("pack_format", 0)))
    old = pack_min < 65
    reaches_old = any(_major(e.get("min_format", 999)) < 65 for e in entries)
    for e in entries:
        d = e.get("directory", "?")
        if "min_format" not in e or "max_format" not in e:
            errors.append(f'pack.mcmeta: overlay "{d}" needs min_format and max_format')
            continue
        lo, hi = _major(e["min_format"]), _major(e["max_format"])
        if old:
            f = e.get("formats")
            if f is None:
                errors.append(f'pack.mcmeta: overlay "{d}" needs "formats" (the pack supports clients older than format 65)')
            else:
                rng = [f, f] if isinstance(f, int) else ([f.get("min_inclusive"), f.get("max_inclusive")] if isinstance(f, dict) else list(f))
                if rng != [lo, hi]:
                    errors.append(f'pack.mcmeta: overlay "{d}": formats {f} doesn\'t match min_format/max_format {lo}..{hi}')
        elif "formats" in e:
            errors.append(f'pack.mcmeta: overlay "{d}" must not have "formats" (the pack starts at format 65 or later)')
    if old and not reaches_old:
        errors.append('pack.mcmeta: with "formats" in the overlays, at least one overlay must reach below format 65 '
                       '(Minecraft 26.x rejects the whole pack otherwise), keep the nx_compat entry')
    return errors


def small_png(data):
    """The smallest lossless PNG of an image (indexed when it fits)."""
    im = Image.open(io.BytesIO(data))
    im.load()
    best = data
    rgba = im.convert("RGBA")
    cands = []
    cols = rgba.getcolors(256)
    if cols is not None:
        pal_im = Image.new("P", rgba.size)
        palette = []
        index = {}
        trans = []
        for _, c in sorted(cols, key=lambda t: (t[1][3] != 0, t[1])):
            index[c] = len(palette)
            palette.append(c)
        flat = []
        for c in palette:
            flat += list(c[:3])
            trans.append(c[3])
        pal_im.putpalette(flat + [0] * (768 - len(flat)))
        px = rgba.get_flattened_data() if hasattr(rgba, "get_flattened_data") else rgba.getdata()
        pal_im.putdata([index[c] for c in px])
        b = io.BytesIO()
        if any(a < 255 for a in trans):
            pal_im.save(b, "PNG", optimize=True, transparency=bytes(trans))
        else:
            pal_im.save(b, "PNG", optimize=True)
        cands.append(b.getvalue())
    b = io.BytesIO()
    rgba.save(b, "PNG", optimize=True)
    cands.append(b.getvalue())
    for c in cands:
        if len(c) < len(best):
            best = c
    return best


def packed(p):
    """The bytes that go into the zip for a source file."""
    data = p.read_bytes()
    if p.suffix in (".json", ".mcmeta"):
        return json.dumps(json.loads(data.decode("utf-8")), separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    if p.suffix == ".png":
        return small_png(data)
    return data


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
            z.writestr(info, packed(p))
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
