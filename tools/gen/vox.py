"""Voxel models -> Minecraft item models.

A model is a set of coloured voxels (1 voxel = 1 model unit = 1 pixel of a
player by default) plus optional textured planes (wings, capes, banners).

Export:
  - same-coloured voxels are merged into as few boxes as possible (greedy),
  - every face samples ONE shared palette texture (nexium:item/cos/palette),
    so hundreds of models cost a few KB of texture in the pack,
  - faces fully hidden by other voxels are left out.
"""
import json
import math

Color = tuple  # (r, g, b)


def hexc(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def mix(a, b, t):
    return tuple(max(0, min(255, round(a[i] + (b[i] - a[i]) * t))) for i in range(3))


def shade(c, f):
    """f < 1 darker, f > 1 lighter (towards white)."""
    if f <= 1:
        return tuple(max(0, round(v * f)) for v in c)
    return mix(c, (255, 255, 255), min(1.0, f - 1))


class Vox:
    def __init__(self, name, scale=1.0, origin=(0.0, 0.0, 0.0)):
        self.name = name
        self.v = {}
        self.planes = []          # textured planes (see plane())
        self.scale = scale        # model units per voxel
        self.origin = origin      # model position of voxel (0,0,0)

    # ---------------------------------------------------------- drawing
    def set(self, x, y, z, c):
        if callable(c):
            c = c(x, y, z)
        if c is None:
            self.v.pop((x, y, z), None)
        else:
            self.v[(int(x), int(y), int(z))] = tuple(c)

    def get(self, x, y, z):
        return self.v.get((x, y, z))

    def box(self, x0, y0, z0, x1, y1, z1, c):
        """Filled box, end exclusive."""
        for x in range(x0, x1):
            for y in range(y0, y1):
                for z in range(z0, z1):
                    self.set(x, y, z, c)

    def frame(self, x0, y0, z0, x1, y1, z1, c):
        """Only the outer shell of a box."""
        for x in range(x0, x1):
            for y in range(y0, y1):
                for z in range(z0, z1):
                    if x in (x0, x1 - 1) or y in (y0, y1 - 1) or z in (z0, z1 - 1):
                        self.set(x, y, z, c)

    def disc(self, cx, cz, r, y, c, r_in=-1.0, y1=None):
        """Horizontal disc / ring (r_in) at height y (to y1, exclusive)."""
        y1 = y + 1 if y1 is None else y1
        for x in range(math.floor(cx - r - 1), math.ceil(cx + r + 1)):
            for z in range(math.floor(cz - r - 1), math.ceil(cz + r + 1)):
                d = math.hypot(x + 0.5 - cx, z + 0.5 - cz)
                if r_in < d <= r:
                    for yy in range(y, y1):
                        self.set(x, yy, z, c(x, yy, z) if callable(c) else c)

    def ellipsoid(self, cx, cy, cz, rx, ry, rz, c, hollow=False):
        for x in range(math.floor(cx - rx), math.ceil(cx + rx) + 1):
            for y in range(math.floor(cy - ry), math.ceil(cy + ry) + 1):
                for z in range(math.floor(cz - rz), math.ceil(cz + rz) + 1):
                    d = ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 + ((z + 0.5 - cz) / rz) ** 2
                    if d <= 1 and (not hollow or d > 0.55):
                        self.set(x, y, z, c(x, y, z) if callable(c) else c)

    def line(self, a, b, c, r=0.0):
        """3D line of voxels from a to b (voxel coords), optional radius."""
        n = int(max(abs(b[i] - a[i]) for i in range(3)) * 2) + 1
        for i in range(n + 1):
            t = i / n
            p = [a[k] + (b[k] - a[k]) * t for k in range(3)]
            if r <= 0:
                self.set(round(p[0]), round(p[1]), round(p[2]), c)
            else:
                ri = math.ceil(r)
                for dx in range(-ri, ri + 1):
                    for dy in range(-ri, ri + 1):
                        for dz in range(-ri, ri + 1):
                            if dx * dx + dy * dy + dz * dz <= r * r + 0.01:
                                self.set(round(p[0]) + dx, round(p[1]) + dy, round(p[2]) + dz, c)

    def sprite(self, rows, legend, x0, y0, z0, axis="z", depth=1):
        """Paint a 2D pixel sprite (rows top to bottom) as a layer of voxels.
        axis z: sprite in the x/y plane at z0..z0+depth; axis x: in z/y."""
        h = len(rows)
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                c = legend.get(ch)
                if c is None:
                    continue
                y = y0 + (h - 1 - j)
                for d in range(depth):
                    if axis == "z":
                        self.set(x0 + i, y, z0 + d, c)
                    else:
                        self.set(x0 + d, y, z0 + i, c)

    def mirror_x(self, axis2):
        """Copy every voxel to its mirror image around x = axis2 / 2."""
        for (x, y, z), c in list(self.v.items()):
            self.set(axis2 - 1 - x, y, z, c)

    def plane(self, frm, to, texture, faces, rot=None):
        """A textured plane (one element): frm/to in MODEL units, one size 0.
        faces = {"north": [u0, v0, u1, v1], "south": [...]} (u1 < u0 mirrors).
        rot = (axis, angle, origin) with angle in -45/-22.5/0/22.5/45."""
        self.planes.append({"from": frm, "to": to, "tex": texture, "rot": rot, "faces": faces})

    # ---------------------------------------------------------- meshing
    def boxes(self):
        """Greedy merge of same-coloured voxels into boxes."""
        left = dict(self.v)
        out = []
        for key in sorted(self.v.keys(), key=lambda k: (k[1], k[2], k[0])):
            if key not in left:
                continue
            c = left[key]
            x, y, z = key
            x1 = x + 1
            while left.get((x1, y, z)) == c:
                x1 += 1
            y1 = y + 1
            while all(left.get((xx, y1, z)) == c for xx in range(x, x1)):
                y1 += 1
            z1 = z + 1
            while all(left.get((xx, yy, z1)) == c for xx in range(x, x1) for yy in range(y, y1)):
                z1 += 1
            for xx in range(x, x1):
                for yy in range(y, y1):
                    for zz in range(z, z1):
                        del left[(xx, yy, zz)]
            out.append((x, y, z, x1, y1, z1, c))
        return out

    def hidden(self, b, face):
        x0, y0, z0, x1, y1, z1, _ = b
        v = self.v
        if face == "up":
            return all((x, y1, z) in v for x in range(x0, x1) for z in range(z0, z1))
        if face == "down":
            return all((x, y0 - 1, z) in v for x in range(x0, x1) for z in range(z0, z1))
        if face == "east":
            return all((x1, y, z) in v for y in range(y0, y1) for z in range(z0, z1))
        if face == "west":
            return all((x0 - 1, y, z) in v for y in range(y0, y1) for z in range(z0, z1))
        if face == "south":
            return all((x, y, z1) in v for x in range(x0, x1) for y in range(y0, y1))
        return all((x, y, z0 - 1) in v for x in range(x0, x1) for y in range(y0, y1))

    def colors(self):
        return set(self.v.values())


class Palette:
    """All voxel colours of all models in one texture, CELL x CELL pixels each."""
    CELL = 4

    def __init__(self):
        self.cols = []
        self.idx = {}
        self.w = self.h = 0

    def add(self, c):
        if c not in self.idx:
            self.idx[c] = len(self.cols)
            self.cols.append(c)

    def finalize(self):
        n = max(1, len(self.cols))
        per = 1
        while per * per < n:
            per *= 2
        self.per = per
        rows = math.ceil(n / per)
        self.w = per * self.CELL
        self.h = max(1, rows) * self.CELL
        # Minecraft UVs are 0..16 on both axes: keep the texture square
        self.h = max(self.h, self.w)
        self.w = self.h = max(self.w, self.h)

    def uv(self, c):
        i = self.idx[c]
        cx = (i % self.per) * self.CELL
        cy = (i // self.per) * self.CELL
        k = 16.0 / self.w
        # sample the middle of the cell (no bleeding into the neighbours)
        return [r4((cx + 1) * k), r4((cy + 1) * k), r4((cx + self.CELL - 1) * k), r4((cy + self.CELL - 1) * k)]

    def image(self):
        from PIL import Image
        im = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        for c, i in self.idx.items():
            cx = (i % self.per) * self.CELL
            cy = (i // self.per) * self.CELL
            for dx in range(self.CELL):
                for dy in range(self.CELL):
                    im.putpixel((cx + dx, cy + dy), tuple(c) + (255,))
        return im


def r4(v):
    v = round(v, 4)
    return int(v) if v == int(v) else v


FACES = ("north", "south", "east", "west", "up", "down")


def export(vox, pal, display, plane_textures=None, extra_textures=None):
    """Item model JSON (dict). plane_textures: {name: 'nexium:item/cos/x'}."""
    textures = {"p": "nexium:item/cos/palette"}
    tex_keys = {}
    for pl in vox.planes:
        t = pl["tex"]
        if t not in tex_keys:
            k = "t%d" % len(tex_keys)
            tex_keys[t] = k
            textures[k] = t
    if extra_textures:
        textures.update(extra_textures)
    s = vox.scale
    ox, oy, oz = vox.origin
    els = []
    for b in vox.boxes():
        x0, y0, z0, x1, y1, z1, c = b
        faces = {}
        for f in FACES:
            if not vox.hidden(b, f):
                faces[f] = {"uv": pal.uv(c), "texture": "#p"}
        if not faces:
            continue
        els.append({"from": [r4(ox + x0 * s), r4(oy + y0 * s), r4(oz + z0 * s)],
                    "to": [r4(ox + x1 * s), r4(oy + y1 * s), r4(oz + z1 * s)],
                    "faces": faces})
    for pl in vox.planes:
        k = "#" + tex_keys[pl["tex"]]
        frm, to = pl["from"], pl["to"]
        faces = {f: {"uv": [r4(a) for a in uv], "texture": k} for f, uv in pl["faces"].items()}
        el = {"from": [r4(a) for a in frm], "to": [r4(a) for a in to], "faces": faces}
        if pl["rot"]:
            ax, ang, org = pl["rot"]
            el["rotation"] = {"angle": ang, "axis": ax, "origin": [r4(a) for a in org]}
        els.append(el)
    for el in els:
        for a in el["from"] + el["to"]:
            if a < -16 or a > 32:
                raise ValueError("%s: element outside -16..32: %s" % (vox.name, el))
    return {"textures": textures, "elements": els, "display": display}


def dumps(obj):
    return json.dumps(obj, separators=(",", ":"))
