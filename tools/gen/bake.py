"""Bake an hd.Model into a Minecraft item model + its own texture.

Face directions and texture orientation follow Minecraft's element faces
(default UV directions):
  up    u = +x, v = +z          down  u = +x, v = -z
  north u = -x, v = -y          south u = +x, v = -y
  west  u = +z, v = -y          east  u = -z, v = -y
"""
import hashlib
import json

import numpy as np
from PIL import Image

DIRS = {"up": (1, 1), "down": (1, -1), "east": (0, 1), "west": (0, -1), "south": (2, 1), "north": (2, -1)}

AO_STEP = 0.085
AO_MIN = 0.6
BEVEL = {"up": 0.10, "down": 0.0, "north": 0.06, "south": 0.06, "east": 0.06, "west": 0.06}


def _shift(a, ax, d):
    """out[p] = a[p + d * e_ax] (False / 0 outside)."""
    out = np.zeros_like(a)
    src = [slice(None)] * 3
    dst = [slice(None)] * 3
    n = a.shape[ax]
    if d > 0:
        src[ax] = slice(d, n)
        dst[ax] = slice(0, n - d)
    else:
        src[ax] = slice(0, n + d)
        dst[ax] = slice(-d, n)
    out[tuple(dst)] = a[tuple(src)]
    return out


def _shift3(a, off):
    out = a
    for ax in range(3):
        if off[ax]:
            out = _shift(out, ax, off[ax])
    return out


def face_colours(m):
    """{dir: (exposed bool array, colour array uint8)} with AO + bevel."""
    occ = m.mat > 0
    glowing = m.mat > 1
    out = {}
    for name, (ax, s) in DIRS.items():
        e = [0, 0, 0]
        e[ax] = s
        exposed = occ & ~_shift3(occ, e)
        t1, t2 = [a for a in range(3) if a != ax]
        w = np.zeros(occ.shape, np.float32)
        conv = np.zeros(occ.shape, np.float32)
        for a in (-1, 0, 1):
            for b in (-1, 0, 1):
                if a == 0 and b == 0:
                    continue
                off = list(e)
                off[t1] += a
                off[t2] += b
                wt = 1.0 if (a == 0 or b == 0) else 0.5
                w += wt * _shift3(occ, off)
                if a == 0 or b == 0:
                    side = [0, 0, 0]
                    side[t1] = a
                    side[t2] = b
                    conv += ~_shift3(occ, side)
        ao = np.clip(1 - AO_STEP * w, AO_MIN, 1)
        bev = 1 + BEVEL[name] * np.minimum(conv, 2) / 2
        col = m.col * ao[..., None]
        col = col + (255 - col) * (bev[..., None] - 1)
        col = np.where(glowing[..., None], m.col, col)
        out[name] = (exposed, np.clip(np.round(col), 0, 255).astype(np.uint8))
    return out


def greedy(mat):
    """Boxes (x0, y0, z0, x1, y1, z1, value) of equal non-zero mat values."""
    used = np.zeros(mat.shape, bool)
    nx, ny, nz = mat.shape
    boxes = []
    for x, y, z in np.argwhere(mat > 0):
        if used[x, y, z]:
            continue
        v = mat[x, y, z]
        z1 = z + 1
        while z1 < nz and mat[x, y, z1] == v and not used[x, y, z1]:
            z1 += 1
        x1 = x + 1
        while x1 < nx and (mat[x1, y, z:z1] == v).all() and not used[x1, y, z:z1].any():
            x1 += 1
        y1 = y + 1
        while y1 < ny and (mat[x:x1, y1, z:z1] == v).all() and not used[x:x1, y1, z:z1].any():
            y1 += 1
        used[x:x1, y:y1, z:z1] = True
        boxes.append((int(x), int(y), int(z), int(x1), int(y1), int(z1), int(v)))
    return boxes


def face_image(fc, b, name):
    """(exposed?, image rows x cols x 3) of one box face, Minecraft-oriented."""
    exposed, col = fc[name]
    x0, y0, z0, x1, y1, z1, _ = b
    if name == "up":
        e = exposed[x0:x1, y1 - 1, z0:z1]
        img = col[x0:x1, y1 - 1, z0:z1].transpose(1, 0, 2)
    elif name == "down":
        e = exposed[x0:x1, y0, z0:z1]
        img = col[x0:x1, y0, z0:z1].transpose(1, 0, 2)[::-1]
    elif name == "north":
        e = exposed[x0:x1, y0:y1, z0]
        img = col[x0:x1, y0:y1, z0].transpose(1, 0, 2)[::-1, ::-1]
    elif name == "south":
        e = exposed[x0:x1, y0:y1, z1 - 1]
        img = col[x0:x1, y0:y1, z1 - 1].transpose(1, 0, 2)[::-1, :]
    elif name == "west":
        e = exposed[x0, y0:y1, z0:z1]
        img = col[x0, y0:y1, z0:z1][::-1, :]
    else:
        e = exposed[x1 - 1, y0:y1, z0:z1]
        img = col[x1 - 1, y0:y1, z0:z1][::-1, ::-1]
    return bool(e.any()), np.ascontiguousarray(img)


class Atlas:
    """Packs face images (1 px gutter) and single colours into one texture."""

    def __init__(self):
        self.rects = {}     # key -> image
        self.order = []

    def add(self, img):
        if (img == img[0, 0]).all():
            key = ("c",) + tuple(int(v) for v in img[0, 0])
            if key not in self.rects:
                self.rects[key] = np.tile(img[0, 0], (1, 1, 1))
                self.order.append(key)
            return key
        key = ("i", img.shape, hashlib.md5(img.tobytes()).hexdigest())
        if key not in self.rects:
            self.rects[key] = img
            self.order.append(key)
        return key

    def pack(self):
        """Smallest power-of-two rectangle the faces fit in (both sides powers
        of two, so the game keeps all its mipmap levels)."""
        items = sorted(self.order, key=lambda k: (-(self.rects[k].shape[0]), -(self.rects[k].shape[1])))
        area = sum((self.rects[k].shape[0] + 2) * (self.rects[k].shape[1] + 2) for k in items)
        sizes = sorted(((w, h) for w in (16, 32, 64, 128, 256, 512, 1024, 2048) for h in (16, 32, 64, 128, 256, 512, 1024, 2048)
                        if w >= h and w * h >= area and w <= 8 * h), key=lambda wh: (wh[0] * wh[1], wh[0]))
        pos = None
        for W, Hh in sizes:
            pos = self._try(items, W, Hh)
            if pos is not None:
                break
        self.W, self.H = W, Hh
        self.pos = pos
        im = np.zeros((Hh, W, 3), np.uint8)
        for k, (px, py) in pos.items():
            r = self.rects[k]
            h, w = r.shape[:2]
            g = np.pad(r, ((1, 1), (1, 1), (0, 0)), mode="edge")
            im[py:py + h + 2, px:px + w + 2] = g
        self.image = Image.fromarray(im, "RGB")
        return self

    def _try(self, items, SW, SH):
        pos = {}
        x = y = row_h = 0
        for k in items:
            h, w = self.rects[k].shape[:2]
            W, H = w + 2, h + 2
            if W > SW or H > SH:
                return None
            if x + W > SW:
                x = 0
                y += row_h
                row_h = 0
            if y + H > SH:
                return None
            pos[k] = (x, y)
            x += W
            row_h = max(row_h, H)
        return pos

    def uv(self, key):
        px, py = self.pos[key]
        h, w = self.rects[key].shape[:2]
        kx = 16.0 / self.W
        ky = 16.0 / self.H
        return [r5((px + 1) * kx), r5((py + 1) * ky), r5((px + 1 + w) * kx), r5((py + 1 + h) * ky)]


def r5(v):
    v = round(float(v), 5)
    return int(v) if v == int(v) else v


def _elements(m, atlas, rotation=None):
    fc = face_colours(m)
    els = []
    for b in greedy(m.mat):
        x0, y0, z0, x1, y1, z1, v = b
        faces = {}
        for name in ("north", "east", "south", "west", "up", "down"):
            vis, img = face_image(fc, b, name)
            if not vis:
                continue
            faces[name] = atlas.add(img)
        if not faces:
            continue
        r = m.res
        el = {"from": [r5(m.lo[0] + x0 / r), r5(m.lo[1] + y0 / r), r5(m.lo[2] + z0 / r)],
              "to": [r5(m.lo[0] + x1 / r), r5(m.lo[1] + y1 / r), r5(m.lo[2] + z1 / r)],
              "faces": faces}
        if v > 1:
            el["light_emission"] = min(15, v - 1)
            el["shade"] = False
        if rotation:
            el["rotation"] = {"angle": rotation["angle"], "axis": rotation["axis"],
                              "origin": [r5(a) for a in rotation["origin"]]}
        els.append(el)
    return els


def export(m, texture):
    """-> (model dict without display, PIL texture). texture: 'nexium:item/..'"""
    atlas = Atlas()
    els = _elements(m, atlas)
    for p, rot in m.parts:
        els += _elements(p, atlas, rot)
    atlas.pack()
    for el in els:
        for name, key in list(el["faces"].items()):
            el["faces"][name] = {"uv": atlas.uv(key), "texture": "#0"}
        for a in el["from"] + el["to"]:
            if a < -16 or a > 32:
                raise ValueError("%s: element outside -16..32: %s %s" % (m.name, el["from"], el["to"]))
    img = atlas.image
    if len(img.getcolors(1 << 16) or range(300)) > 256:
        img = img.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    return {"textures": {"0": texture, "particle": texture}, "elements": els}, img


def dumps(obj):
    return json.dumps(obj, separators=(",", ":"))
