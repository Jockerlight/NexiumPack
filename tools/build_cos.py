#!/usr/bin/env python3
"""Generates every cosmetic of the pack from tools/gen/*.py.

    python tools/build_cos.py            models + textures into pack/
    python tools/build_cos.py --preview  also preview sheets into previews/

Writes (all generated, don't edit by hand):
  pack/assets/nexium/textures/item/cos/palette.png   one colour per 4x4 cell
  pack/assets/nexium/models/item/<kind>/<id>.json    the models
  pack/assets/nexium/items/<kind>/<id>.json          item model definitions
  cosmetics.json                                      id, name, rarity, kind
Item model ids: nexium:hat/<id>, nexium:back/<id>, nexium:outfit/<id>,
nexium:pick/<id> (set as the item_model component on the server).
"""
import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "gen"))

from vox import Palette, export, dumps  # noqa: E402
import render as R  # noqa: E402

PACK = ROOT / "pack" / "assets" / "nexium"
GUI_ROT = [30, 225, 0]
BACK_ROT = [15, 160, 0]   # back items: seen from behind


def corners(model):
    out = []
    for el in model["elements"]:
        f, t = el["from"], el["to"]
        rot = el.get("rotation")
        for cx in (f[0], t[0]):
            for cy in (f[1], t[1]):
                for cz in (f[2], t[2]):
                    p = (cx, cy, cz)
                    if rot:
                        p = R.rot_axis(p, rot["axis"], rot["angle"], rot["origin"])
                    out.append(p)
    return out


def fit(model, rot, size=15.0, max_scale=1.0):
    """Display transform that shows the whole model centred in a 16x16 slot."""
    pts = [R.transform(p, {"rotation": rot}) for p in corners(model)]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    w = max(xs) - min(xs)
    h = max(ys) - min(ys)
    s = min(max_scale, size / max(w, h, 1e-3))
    cx = (max(xs) + min(xs)) / 2 * s
    cy = (max(ys) + min(ys)) / 2 * s
    r = lambda a: round(a, 3)
    return {"rotation": rot, "translation": [r(-cx), r(-cy), 0], "scale": [r(s)] * 3}


def icon(pick):
    """pack.png: the Nexium Core pickaxe on a dark glow (128x128)."""
    from PIL import Image
    from vox import mix
    S = 128
    im = Image.new("RGBA", (S, S))
    for y in range(S):
        for x in range(S):
            d = math.hypot(x - S / 2 + 0.5, y - S / 2 + 0.5) / (S * 0.72)
            im.putpixel((x, y), mix((22, 70, 64), (8, 14, 20), min(1.0, d)) + (255,))
    big = pick.resize((96, 96), Image.NEAREST)
    shadow = Image.new("RGBA", big.size, (0, 0, 0, 0))
    shadow.putalpha(big.getchannel("A").point(lambda a: 110 if a else 0))
    im.alpha_composite(shadow, (18, 20))
    im.alpha_composite(big, (16, 16))
    im.save(ROOT / "pack" / "pack.png", optimize=True)


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps(obj), encoding="utf-8")


def collect():
    from hats import HATS
    items = []
    for id, name, rarity, fn in HATS:
        items.append({"kind": "hat", "id": id, "name": name, "rarity": rarity, "vox": fn()})
    from backs import BACKS
    for id, name, rarity, fn in BACKS:
        items.append({"kind": "back", "id": id, "name": name, "rarity": rarity, "vox": fn()})
    from outfits import OUTFITS
    for id, name, rarity, fn in OUTFITS:
        head, back = fn()
        items.append({"kind": "outfit", "id": id + "_head", "name": name, "rarity": rarity, "vox": head, "part": "head", "outfit": id})
        items.append({"kind": "outfit", "id": id + "_back", "name": name + " (back)", "rarity": rarity, "vox": back, "part": "back", "outfit": id})
    from pickaxes import skin_crate
    base, lid = skin_crate()
    items.append({"kind": "misc", "id": "skin_crate", "name": "Skin Crate", "rarity": "", "vox": base, "part": "block"})
    items.append({"kind": "misc", "id": "skin_crate_lid", "name": "Skin Crate Lid", "rarity": "", "vox": lid, "part": "block"})
    return items


GENERATED = ["models/item/hat", "models/item/back", "models/item/outfit", "models/item/pick", "models/item/misc",
             "items/hat", "items/back", "items/outfit", "items/pick", "items/misc",
             "textures/item/cos", "textures/item/pick", "textures/entity/equipment", "equipment"]


def clean():
    import shutil
    for d in GENERATED:
        shutil.rmtree(PACK / d, ignore_errors=True)
    for f in ("items/test_pickaxe.json", "models/item/test_pickaxe.json", "textures/item/test_pickaxe.png"):
        (PACK / f).unlink(missing_ok=True)


def displays(kind, model, part=None):
    if part == "block":
        return {"gui": fit(model, GUI_ROT, 15), "fixed": {"scale": [1, 1, 1]},
                "ground": {"translation": [0, 2, 0], "scale": [0.4, 0.4, 0.4]}}
    if kind == "hat" or part == "head":
        d = {"head": {"scale": [1.6, 1.6, 1.6]},
             "gui": fit(model, GUI_ROT),
             "ground": {"translation": [0, 2, 0], "scale": [0.5, 0.5, 0.5]},
             "fixed": fit(model, [0, 180, 0], 14)}
    else:
        # back items are shown by item displays (transform "none"); the
        # menus show them from behind
        d = {"gui": fit(model, BACK_ROT),
             "ground": {"translation": [0, 2, 0], "scale": [0.5, 0.5, 0.5]},
             "fixed": fit(model, [0, 180, 0], 14)}
    return d


def armor_elems(oid):
    """Mannequin parts textured with the outfit's armour (preview only)."""
    def box(f, t, ox, oy, w, h, d, tex):
        k = lambda x, y: [x / 4, y / 2]
        faces = {
            "up": k(ox + d, oy) + k(ox + d + w, oy + d),
            "down": k(ox + d + w, oy) + k(ox + d + 2 * w, oy + d),
            "west": k(ox, oy + d) + k(ox + d, oy + d + h),
            "south": k(ox + d, oy + d) + k(ox + d + w, oy + d + h),
            "east": k(ox + d + w, oy + d) + k(ox + 2 * d + w, oy + d + h),
            "north": k(ox + 2 * d + w, oy + d) + k(ox + 2 * d + 2 * w, oy + d + h),
        }
        return {"from": f, "to": t, "faces": {n: {"uv": uv, "texture": "#" + tex} for n, uv in faces.items()}}
    return [box([4, 2, 6], [12, 14, 10], 16, 16, 8, 12, 4, "a"),
            box([0, 2, 6], [4, 14, 10], 40, 16, 4, 12, 4, "a"),
            box([12, 2, 6], [16, 14, 10], 40, 16, 4, 12, 4, "a"),
            box([4, -10, 6], [8, 2, 10], 0, 16, 4, 12, 4, "l"),
            box([8, -10, 6], [12, 2, 10], 0, 16, 4, 12, 4, "l"),
            box([3.9, -10.1, 5.9], [8.1, 2.1, 10.1], 0, 16, 4, 12, 4, "a"),
            box([7.9, -10.1, 5.9], [12.1, 2.1, 10.1], 0, 16, 4, 12, 4, "a")]


def outfit_cells(items, tex):
    from outfits import ARMOR
    from PIL import Image
    cells = []
    by = {}
    for it in items:
        if it["kind"] == "outfit":
            by.setdefault(it["outfit"], {})[it["part"]] = it
    for oid, parts in by.items():
        hum, leg = ARMOR[oid]
        t = dict(tex)
        t["A"] = hum
        t["L"] = leg
        els = armor_elems(oid)
        head = parts["head"]["model"]
        # worn heads face north (Minecraft turns them round): turn the
        # preview copy 180 degrees so its face looks the way the body does
        swap = {"north": "south", "south": "north", "east": "west", "west": "east", "up": "up", "down": "down"}
        for el in head["elements"]:
            e = dict(el)
            e["from"] = [16 - el["to"][0], el["from"][1] + 10, 16 - el["to"][2]]
            e["to"] = [16 - el["from"][0], el["to"][1] + 10, 16 - el["from"][2]]
            e["faces"] = {swap[k]: v for k, v in el["faces"].items()}
            e.pop("rotation", None)
            els.append(e)
        els += parts["back"]["model"]["elements"]
        texs = {"a": "A", "l": "L"}
        texs.update(head["textures"])
        texs.update(parts["back"]["model"]["textures"])
        m = {"textures": texs, "elements": els}
        img = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
        f = R.render(m, t, {"rotation": [8, 20, 0]}, size=150, px=3.6)
        b = R.render(m, t, {"rotation": [8, 200, 0]}, size=150, px=3.6)
        img.paste(f, (0, 70), f)
        img.paste(b, (150, 70), b)
        cells.append((parts["head"]["name"], img))
    return cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    clean()
    items = collect()
    pal = Palette()
    for it in items:
        for c in sorted(it["vox"].colors()):
            pal.add(c)
    pal.finalize()
    (PACK / "textures/item/cos").mkdir(parents=True, exist_ok=True)
    pal.image().save(PACK / "textures/item/cos/palette.png", optimize=True)
    import sprite
    tex = {"nexium:item/cos/palette": pal.image()}
    for name, im in sprite.TEXTURES.items():
        tex[name] = im
        im.save(PACK / "textures/item/cos" / (name.split("/")[-1] + ".png"), optimize=True)
    manifest = []
    stats = {}
    for it in items:
        m = export(it["vox"], pal, {})
        m["display"] = displays(it["kind"], m, it.get("part"))
        it["model"] = m
        write_json(PACK / "models/item" / it["kind"] / (it["id"] + ".json"), m)
        write_json(PACK / "items" / it["kind"] / (it["id"] + ".json"),
                   {"model": {"type": "minecraft:model", "model": "nexium:item/%s/%s" % (it["kind"], it["id"])}})
        if it.get("part") != "back":
            e = {k: it[k] for k in ("kind", "id", "name", "rarity")}
            if it.get("outfit"):
                e["id"] = it["outfit"]
            manifest.append(e)
        s = stats.setdefault(it["kind"], [0, 0])
        s[0] += 1
        s[1] += len(m["elements"])
    # outfits: equipment assets + armour textures
    from outfits import ARMOR
    for oid, (hum, leg) in ARMOR.items():
        for layer, im in (("humanoid", hum), ("humanoid_leggings", leg)):
            d = PACK / "textures/entity/equipment" / layer
            d.mkdir(parents=True, exist_ok=True)
            im.save(d / (oid + ".png"), optimize=True)
        write_json(PACK / "equipment" / (oid + ".json"),
                   {"layers": {"humanoid": [{"texture": "nexium:" + oid}],
                               "humanoid_leggings": [{"texture": "nexium:" + oid}]}})
    # pickaxe skins: 2D sprites on the vanilla handheld model
    from pickaxes import PICKS
    pick_imgs = []
    (PACK / "textures/item/pick").mkdir(parents=True, exist_ok=True)
    for id, name, rarity, fn, text in PICKS:
        im = fn().image()
        im.save(PACK / "textures/item/pick" / (id + ".png"), optimize=True)
        write_json(PACK / "models/item/pick" / (id + ".json"),
                   {"parent": "minecraft:item/handheld", "textures": {"layer0": "nexium:item/pick/" + id}})
        write_json(PACK / "items/pick" / (id + ".json"),
                   {"model": {"type": "minecraft:model", "model": "nexium:item/pick/" + id}})
        manifest.append({"kind": "pick", "id": id, "name": name, "rarity": rarity, "text": text})
        pick_imgs.append((name, im))
    stats["pick"] = [len(PICKS), 0]
    icon(dict((n, i) for n, i in pick_imgs)["Nexium Core Pick"])
    (ROOT / "cosmetics.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    print("palette: %d colours, %dx%d" % (len(pal.cols), pal.w, pal.h))
    for k, (n, e) in stats.items():
        print("%s: %d models, %d elements (avg %.0f)" % (k, n, e, e / n))
    if a.preview:
        out = ROOT / "previews"
        out.mkdir(exist_ok=True)
        for kind, cols in (("hat", 8), ("back", 8)):
            cells = []
            for it in items:
                if it["kind"] != kind:
                    continue
                if kind == "hat":
                    im = R.render(it["model"], tex, {"rotation": GUI_ROT}, size=150, px=5.0, extra=R.head_cube())
                else:
                    im = R.render(it["model"], tex, {"rotation": [12, 160, 0]}, size=150, px=3.6, extra=R.body_parts())
                cells.append((it["name"], im))
            if cells:
                R.sheet(cells, cols, title="%sS - %d" % (kind.upper(), len(cells))).save(out / ("%ss.png" % kind))
        from PIL import Image
        cells = []
        for name, im in pick_imgs:
            c = Image.new("RGBA", (150, 150), (0, 0, 0, 0))
            big = im.resize((128, 128), Image.NEAREST)
            c.paste(big, (11, 11), big)
            cells.append((name, c))
        R.sheet(cells, 6, title="PICKAXE SKINS - %d" % len(cells)).save(out / "picks.png")
        crate = [it for it in items if it["kind"] == "misc"]
        m = {"textures": crate[0]["model"]["textures"], "elements": crate[0]["model"]["elements"] + crate[1]["model"]["elements"]}
        R.sheet([("Skin Crate", R.render(m, tex, {"rotation": GUI_ROT}, size=150, px=6.0))], 1, title="CRATE").save(out / "crate.png")
        R.sheet(outfit_cells(items, tex), 4, cell=300, title="OUTFITS - %d - FRONT / BACK" % len(ARMOR)).save(out / "outfits.png")
        print("previews in", out)


if __name__ == "__main__":
    main()
