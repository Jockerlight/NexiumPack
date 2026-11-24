#!/usr/bin/env python3
"""Generates every cosmetic of the pack from tools/gen/*.py (HD voxel models).

    python tools/build_cos.py            models + textures into pack/
    python tools/build_cos.py --preview  also preview sheets into previews/
    python tools/build_cos.py --only hat:crown,back:angel_wings --preview
                                         just these (quick look while drawing)

Writes (all generated, don't edit by hand):
  pack/assets/nexium/models/item/<kind>/<id>.json    the models
  pack/assets/nexium/textures/item/cos/<kind>/<id>.png  their baked textures
  pack/assets/nexium/items/<kind>/<id>.json          item model definitions
  pack/assets/nexium/equipment/<id>.json + armour textures (outfits)
  cosmetics.json                                      id, name, rarity, kind
Item model ids: nexium:hat/<id>, nexium:back/<id>, nexium:outfit/<id>_head,
nexium:outfit/<id>_back, nexium:pick/<id> (the server sets them as the
item_model component).
"""
import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "gen"))

import bake  # noqa: E402
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
    S = 128
    im = Image.new("RGBA", (S, S))
    px = im.load()
    for y in range(S):
        for x in range(S):
            d = min(1.0, math.hypot(x - S / 2 + 0.5, y - S / 2 + 0.5) / (S * 0.72))
            a, b = (22, 70, 64), (8, 14, 20)
            px[x, y] = tuple(round(a[i] + (b[i] - a[i]) * d) for i in range(3)) + (255,)
    big = pick.resize((96, 96), Image.NEAREST)
    shadow = Image.new("RGBA", big.size, (0, 0, 0, 0))
    shadow.putalpha(big.getchannel("A").point(lambda a: 110 if a else 0))
    im.alpha_composite(shadow, (18, 20))
    im.alpha_composite(big, (16, 16))
    im.save(ROOT / "pack" / "pack.png", optimize=True)


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(bake.dumps(obj), encoding="utf-8")


def collect(only=None):
    def want(kind, id):
        return only is None or (kind, id) in only or (kind, "*") in only
    items = []
    from hats import HATS
    for id, name, rarity, fn in HATS:
        if want("hat", id):
            items.append({"kind": "hat", "id": id, "name": name, "rarity": rarity, "fn": fn})
    from backs import BACKS
    for id, name, rarity, fn in BACKS:
        if want("back", id):
            items.append({"kind": "back", "id": id, "name": name, "rarity": rarity, "fn": fn})
    from outfits import OUTFITS
    for id, name, rarity, fn in OUTFITS:
        if want("outfit", id):
            head, back = fn()
            items.append({"kind": "outfit", "id": id + "_head", "name": name, "rarity": rarity, "vox": head, "part": "head", "outfit": id})
            items.append({"kind": "outfit", "id": id + "_back", "name": name + " (back)", "rarity": rarity, "vox": back, "part": "back", "outfit": id})
    if want("misc", "skin_crate"):
        from misc import skin_crate
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


def displays(kind, model, part=None):
    if part == "block":
        return {"gui": fit(model, GUI_ROT, 15), "fixed": {"scale": [1, 1, 1]},
                "ground": {"translation": [0, 2, 0], "scale": [0.4, 0.4, 0.4]}}
    if kind == "hat" or part == "head":
        return {"head": {"scale": [1.6, 1.6, 1.6]},
                "gui": fit(model, GUI_ROT),
                "ground": {"translation": [0, 2, 0], "scale": [0.5, 0.5, 0.5]},
                "fixed": fit(model, [0, 180, 0], 14)}
    # back items are shown by item displays (transform "none"); menus show them from behind
    return {"gui": fit(model, BACK_ROT),
            "ground": {"translation": [0, 2, 0], "scale": [0.5, 0.5, 0.5]},
            "fixed": fit(model, [0, 180, 0], 14)}


def armor_elems():
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
    # inflated like Minecraft draws armour: chestplate / boots 1.0, leggings 0.5
    return [box([3, 1, 5], [13, 15, 11], 16, 16, 8, 12, 4, "a"),
            box([-1, 1, 5], [5, 15, 11], 40, 16, 4, 12, 4, "a"),
            box([11, 1, 5], [17, 15, 11], 40, 16, 4, 12, 4, "a"),
            box([3.5, -10.5, 5.5], [8.5, 2.5, 10.5], 0, 16, 4, 12, 4, "l"),
            box([7.5, -10.5, 5.5], [12.5, 2.5, 10.5], 0, 16, 4, 12, 4, "l"),
            box([3, -11, 5], [9, 3, 11], 0, 16, 4, 12, 4, "a"),
            box([7, -11, 5], [13, 3, 11], 0, 16, 4, 12, 4, "a")]


def retex(model, key):
    """Copy of the model's elements with texture '#0' renamed to '#key'."""
    out = []
    for el in model["elements"]:
        e = dict(el)
        e["faces"] = {k: dict(v, texture="#" + key) for k, v in el["faces"].items()}
        out.append(e)
    return out


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
        els = armor_elems()
        head = parts["head"]["model"]
        # worn heads face north (Minecraft turns them round): turn the preview
        # copy 180 degrees so its face looks the way the body does
        swap = {"north": "south", "south": "north", "east": "west", "west": "east", "up": "up", "down": "down"}
        for el in retex(head, "h"):
            e = dict(el)
            e["from"] = [16 - el["to"][0], el["from"][1] + 10, 16 - el["to"][2]]
            e["to"] = [16 - el["from"][0], el["to"][1] + 10, 16 - el["from"][2]]
            e["faces"] = {swap[k]: v for k, v in el["faces"].items()}
            e.pop("rotation", None)
            els.append(e)
        els += retex(parts["back"]["model"], "b")
        texs = {"a": "A", "l": "L", "h": head["textures"]["0"], "b": parts["back"]["model"]["textures"]["0"]}
        m = {"textures": texs, "elements": els}
        img = Image.new("RGBA", (400, 400), (0, 0, 0, 0))
        f = R.render(m, t, {"rotation": [8, 20, 0], "translation": [0, -2, 0]}, size=200, px=5.2)
        b = R.render(m, t, {"rotation": [8, 200, 0], "translation": [0, -2, 0]}, size=200, px=5.2)
        img.paste(f, (0, 100), f)
        img.paste(b, (200, 100), b)
        cells.append((parts["head"]["name"], img))
    return cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--only", default=None, help="kind:id,kind:id (kind:* for all of a kind)")
    a = ap.parse_args()
    only = None
    if a.only:
        only = {tuple(x.split(":", 1)) for x in a.only.split(",")}
    else:
        clean()
    items = collect(only)
    tex = {}
    manifest = []
    stats = {}
    for it in items:
        vox = it.get("vox") or it["fn"]()
        tid = "nexium:item/cos/%s/%s" % (it["kind"], it["id"])
        m, img = bake.export(vox, tid)
        m["display"] = displays(it["kind"], m, it.get("part"))
        it["model"] = m
        tex[tid] = img
        tp = PACK / "textures/item/cos" / it["kind"] / (it["id"] + ".png")
        tp.parent.mkdir(parents=True, exist_ok=True)
        img.save(tp, optimize=True)
        write_json(PACK / "models/item" / it["kind"] / (it["id"] + ".json"), m)
        write_json(PACK / "items" / it["kind"] / (it["id"] + ".json"),
                   {"model": {"type": "minecraft:model", "model": "nexium:item/%s/%s" % (it["kind"], it["id"])}})
        if it.get("part") != "back":
            e = {k: it[k] for k in ("kind", "id", "name", "rarity")}
            if it.get("outfit"):
                e["id"] = it["outfit"]
            manifest.append(e)
        s = stats.setdefault(it["kind"], [0, 0, 0])
        s[0] += 1
        s[1] += len(m["elements"])
        s[2] += img.size[0] * img.size[1]
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
    # pickaxe skins
    pick_imgs = []
    if only is None or ("pick", "*") in only:
        import pickaxes as P
        pick_imgs = P.build(PACK, write_json, manifest)
        stats["pick"] = [len(pick_imgs), 0, 0]
        icon(dict(pick_imgs)["Nexium Core Pick"])
    if only is None:
        (ROOT / "cosmetics.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    for k, (n, e, px) in stats.items():
        print("%s: %d models, %d elements (avg %.0f), %d texture pixels" % (k, n, e, e / max(1, n), px))
    if a.preview:
        out = ROOT / "previews"
        out.mkdir(exist_ok=True)
        for kind, cols in (("hat", 8), ("back", 6)):
            cells = []
            for it in items:
                if it["kind"] != kind:
                    continue
                if kind == "hat":
                    im = R.render(it["model"], tex, {"rotation": GUI_ROT, "translation": [0, -3, 0]}, size=240, px=9.5,
                                  extra=R.head_cube())
                else:
                    im = R.render(it["model"], tex, {"rotation": [12, 160, 0], "translation": [0, -4, 0]}, size=300, px=7.0,
                                  extra=R.body_parts())
                cells.append((it["name"], im))
            if cells:
                R.sheet(cells, cols, cell=240 if kind == "hat" else 300,
                        title="%sS - %d" % (kind.upper(), len(cells))).save(out / ("%ss.png" % kind))
        crate = [it for it in items if it["kind"] == "misc"]
        if crate:
            m = {"textures": {"c": crate[0]["model"]["textures"]["0"], "l": crate[1]["model"]["textures"]["0"]},
                 "elements": retex(crate[0]["model"], "c") + retex(crate[1]["model"], "l")}
            R.sheet([("Skin Crate", R.render(m, tex, {"rotation": GUI_ROT}, size=300, px=13.0))], 1, cell=300,
                    title="CRATE").save(out / "crate.png")
        oc = outfit_cells(items, tex)
        if oc:
            R.sheet(oc, 4, cell=400, title="OUTFITS - %d - FRONT / BACK" % len(oc)).save(out / "outfits.png")
        if pick_imgs:
            from PIL import Image
            cells = []
            for name, im in pick_imgs:
                c = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
                big = im.resize((128, 128), Image.NEAREST)
                c.paste(big, (16, 16), big)
                cells.append((name, c))
            R.sheet(cells, 6, cell=160, title="PICKAXE SKINS - %d" % len(cells)).save(out / "picks.png")
        print("previews in", out)


if __name__ == "__main__":
    main()
