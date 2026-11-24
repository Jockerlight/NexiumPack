"""The 8 outfits, built from their pixel art in tools/art/outfits/<id>/:

  humanoid.png, humanoid_leggings.png   the armour (128x64, Minecraft's
                                        64x32 armour layout at 2x)
  head_front.png, head_back.png         the helmet's front and back faces
  <on>_<n>_<mode>.png                   sprites for the helmet ("head") and
                                        the back piece ("back")
  art.json                              where every sprite goes

Everything is placed in body space (torso x 4..12, y 2..14, z 6..10, the
player looks to +z, the player's left is +x); the head piece is turned into
hat space at the end. One sprite pixel = one voxel (art.json "voxel").

Sprite modes:
  wing  the LEFT wing drawn flat from its root out to +x; turned back by
        "sweep" degrees around the root in game, the right wing mirrors it
  flat  a thin plate at z "z" (capes, rings behind the head)
  slab  the sprite pushed through z "z" (crests, spikes, antlers, cannons)
  band  the sprite on all four sides of the head ("band": [lo, hi, depth])
  ring  the sprite bent round a level ring ("ring": [x, z, r_in, r_out]):
        seen from the front or back it shows the sprite (halos)
"""
import colorsys
import json
from pathlib import Path

import numpy as np
from PIL import Image

from hd import Model, C
from wings import mirrored

ART = Path(__file__).resolve().parent.parent / "art" / "outfits"
ART_BACKS = ART.parent / "backs"
OUTFITS = []
ARMOR = {}   # id -> (humanoid image, humanoid_leggings image)
RES = 4


def outfit(id, name, rarity):
    def deco(fn):
        OUTFITS.append((id, name, rarity, fn))
        return fn
    return deco


def _rgba(path):
    return np.asarray(Image.open(path).convert("RGBA"))


def _glow(cols, rules):
    """Light level (0 = none) per colour from hue / saturation / value rules."""
    lv = np.zeros(len(cols), np.uint8)
    for i, c in enumerate(cols):
        h, s, v = colorsys.rgb_to_hsv(*(c[:3] / 255.0))
        for r in rules:
            lo, hi = r["hue"]
            hd = h * 360
            if (lo <= hd <= hi if lo <= hi else (hd >= lo or hd <= hi)) and s >= r["sat"] and v >= r["val"]:
                lv[i] = r["level"]
                break
    return lv


def _put(m, X, Y, Z, cols, rules):
    """Voxels at body-space centres X, Y, Z (1-d arrays) with colours."""
    i = np.floor((X - m.lo[0]) * m.res).astype(int)
    j = np.floor((Y - m.lo[1]) * m.res).astype(int)
    k = np.floor((Z - m.lo[2]) * m.res).astype(int)
    ok = (i >= 0) & (j >= 0) & (k >= 0) & (i < m.n[0]) & (j < m.n[1]) & (k < m.n[2])
    i, j, k, cols = i[ok], j[ok], k[ok], cols[ok]
    m.col[i, j, k] = cols[:, :3]
    lv = _glow(cols, rules) if rules else np.zeros(len(cols), np.uint8)
    m.mat[i, j, k] = np.where(lv > 0, 1 + lv, 1)


def _sprite_px(img, rect, v):
    """Opaque pixels of a sprite -> (x, y) centres in body space + colours."""
    x0, y0, x1, y1 = rect
    r, c = np.nonzero(img[..., 3] > 127)
    x = x0 + (c + 0.5) * v
    y = y0 + (img.shape[0] - r - 0.5) * v
    return x, y, img[r, c].astype(np.float32)


def _slab(m, img, rect, z0, z1, v, rules):
    x, y, cols = _sprite_px(img, rect, v)
    for z in np.arange(z0 + v / 2, z1, v):
        _put(m, x, y, np.full(len(x), z), cols, rules)


def _band(m, img, rect, lo, hi, t, v, rules):
    """The sprite on the four sides of the head, as seen from each side."""
    x, y, cols = _sprite_px(img, rect, v)
    x0, _, x1, _ = rect
    u = (x - x0) / (x1 - x0)            # 0..1 across the sprite (screen left -> right)
    a = lo + u * (hi - lo)
    for d in np.arange(v / 2, t, v):
        _put(m, a, y, np.full(len(a), hi - d), cols, rules)          # front (+z), +x on the right
        _put(m, lo + hi - a, y, np.full(len(a), lo + d), cols, rules)  # back
        _put(m, np.full(len(a), hi - d), y, lo + hi - a, cols, rules)  # left side (+x)
        _put(m, np.full(len(a), lo + d), y, a, cols, rules)           # right side


def _ring(m, img, rect, cx, cz, r0, r1, v, rules):
    x, y, cols = _sprite_px(img, rect, v)
    zs = np.arange(cz - r1 + v / 2, cz + r1, v)
    for xv in np.unique(x):
        sel = x == xv
        dz = zs - cz
        rr = np.hypot(xv - cx, dz)
        zz = zs[(rr >= r0) & (rr <= r1)]
        for z in zz:
            _put(m, x[sel], y[sel], np.full(sel.sum(), z), cols[sel], rules)


def _helmet(m, art, d, rules):
    x0, x1, y0, y1 = art["head_box"]
    v = art["voxel"]
    front = _rgba(d / "head_front.png")[..., :3].astype(np.float32)
    back = _rgba(d / "head_back.png")[..., :3].astype(np.float32)
    n = front.shape[0]
    ii = np.floor((x0 - m.lo[0]) * m.res).astype(int)
    jj = np.floor((y0 - m.lo[1]) * m.res).astype(int)
    kk = np.floor((x0 - m.lo[2]) * m.res).astype(int)
    s = slice(ii, ii + n), slice(jj, jj + n), slice(kk, kk + n)
    m.mat[s] = 1
    m.col[s] = front.reshape(-1, 3).mean(0) * 0.6
    I = np.arange(n)
    rows = n - 1 - I           # image row for voxel layer j (row 0 = top)
    h = n // 2
    # sides: the front's edge column towards the front, the back's towards the back
    for j in range(n):
        r = rows[j]
        m.col[ii + n - 1, jj + j, kk + h:kk + n] = front[r, n - 1]
        m.col[ii + n - 1, jj + j, kk:kk + h] = back[r, 0]
        m.col[ii, jj + j, kk + h:kk + n] = front[r, 0]
        m.col[ii, jj + j, kk:kk + h] = back[r, n - 1]
    # top: the front's top row towards the front, the back's towards the back
    m.col[ii:ii + n, jj + n - 1, kk + h:kk + n] = front[0][:, None]
    m.col[ii:ii + n, jj + n - 1, kk:kk + h] = back[0][::-1][:, None]
    m.col[ii:ii + n, jj, kk:kk + n] = front[n - 1].mean(0) * 0.5
    # front (+z) and back faces win at the edges
    m.col[ii:ii + n, jj:jj + n, kk + n - 1] = front[rows][:, :].transpose(1, 0, 2)
    m.col[ii:ii + n, jj:jj + n, kk] = back[rows][:, ::-1].transpose(1, 0, 2)
    if rules:
        for face in (np.s_[ii:ii + n, jj:jj + n, kk + n - 1], np.s_[ii:ii + n, jj:jj + n, kk]):
            c = m.col[face].reshape(-1, 3)
            lv = _glow(c, rules).reshape(m.col[face].shape[:2])
            sub = m.mat[face]
            sub[lv > 0] = 1 + lv[lv > 0]


def _hat_space(m):
    """Body-space head model -> hat space (Minecraft turns worn heads round)."""
    m.col = np.ascontiguousarray(m.col[::-1, :, ::-1])
    m.mat = np.ascontiguousarray(m.mat[::-1, :, ::-1])
    m.lo = np.array([-6.0, 0.0, -6.0])
    return m


def _sprites(head, back, art, d):
    v = art["voxel"]
    rules = art.get("glow", [])
    for sp in art["sprites"]:
        img = _rgba(d / sp["file"])
        m = head if sp["on"] == "head" else back
        r = sp.get("glow", rules)
        if sp["mode"] == "wing":
            rx, ry, rz = sp["root"]
            p = m.part("y", sp["sweep"], (rx, ry, rz))
            _slab(p, img, sp["rect"], rz - sp.get("depth", 0.5), rz, v, r)
            mirrored(m, p, sp["sweep"], (rx, ry, rz))
        elif sp["mode"] in ("flat", "slab"):
            _slab(m, img, sp["rect"], sp["z"][0], sp["z"][1], v, r)
        elif sp["mode"] == "ring":
            cx, cz, r0, r1 = sp["ring"]
            _ring(m, img, sp["rect"], cx, cz, r0, r1, v, r)
        elif sp["mode"] == "band":
            lo, hi, t = sp["band"]
            _band(m, img, sp["rect"], lo, hi, t, v, r)
    if "mount" in art:
        _box(back, art["mount"]["box"], C(art["mount"]["color"]), v)


def _box(m, b, col, v):
    x0, y0, z0, x1, y1, z1 = b
    X, Y, Z = np.meshgrid(np.arange(x0 + v / 2, x1, v), np.arange(y0 + v / 2, y1, v), np.arange(z0 + v / 2, z1, v),
                          indexing="ij")
    n = X.size
    _put(m, X.ravel(), Y.ravel(), Z.ravel(), np.tile(np.append(col, 255).astype(np.float32), (n, 1)), None)


def back_from_art(d, name):
    """A back item that is just art (wings lifted from the reference sheet);
    a small dark block joins the wings to the back."""
    art = json.loads((d / "art.json").read_text())
    back = Model(name, (-12, -10, -6), (28, 32, 10), RES)
    _sprites(None, back, art, d)
    for sp in art["sprites"]:
        if sp["mode"] == "wing":
            img = _rgba(d / sp["file"])
            a = img[:, :6][img[:, :6, 3] > 127][:, :3].astype(float)
            col = np.median(a, 0) * 0.7 if len(a) else C("1c1c22")
            rx, ry, rz = sp["root"]
            _box(back, [rx - 1.0, ry - 1.5, rz - 0.5, rx + 1.0, ry + 1.5, 5.0], col, art["voxel"])
    return back


def build(id):
    d = ART / id
    art = json.loads((d / "art.json").read_text())
    rules = art.get("glow", [])
    head = Model(id + "_head", (-6, 10, -6), (22, 42, 22), RES)
    back = Model(id + "_back", (-12, -10, -6), (28, 32, 10), RES)
    _helmet(head, art, d, rules)
    _sprites(head, back, art, d)
    ARMOR[id] = (Image.open(d / "humanoid.png").convert("RGBA"), Image.open(d / "humanoid_leggings.png").convert("RGBA"))
    return _hat_space(head), back


for _id, _name, _rarity in (("demon_lord", "Demon Lord", "MYTHIC"), ("shadow_knight", "Shadow Knight", "LEGENDARY"),
                            ("seraph", "Seraph", "MYTHIC"), ("frost_warden", "Frost Warden", "LEGENDARY"),
                            ("void_walker", "Void Walker", "MYTHIC"), ("jungle_spirit", "Jungle Spirit", "LEGENDARY"),
                            ("neon_mech", "Neon Mech", "LEGENDARY"), ("golden_emperor", "Golden Emperor", "MYTHIC")):
    if (ART / _id / "art.json").exists():
        OUTFITS.append((_id, _name, _rarity, (lambda i: lambda: build(i))(_id)))
