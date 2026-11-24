"""HD voxel models -> Minecraft item models with baked textures.

A model is a dense grid of voxels, RES (4) voxels per model unit: a player
head (8 units) is 32 voxels wide, like a 32x skin. Shapes are signed
"inside" tests on the voxel centres, so anything (spheres, tori, tubes,
rotated parts) can be drawn at any size.

Every voxel has a colour from a MATERIAL (gold, gem, fabric, knit, metal,
wood, glow ...): each material is a ramp of tones with its own pattern and
per-voxel noise, so surfaces are never flat.

Bake:
  - voxels are merged into as few boxes as possible by SHAPE (not colour),
  - every visible box face gets its own pixels in the model's texture
    (1 pixel per voxel face) with ambient occlusion in creases and a light
    bevel on edges baked in,
  - one texture per model (all faces packed, 1 px gutters, <= 256 colours),
  - glowing voxels become their own boxes with light_emission (they shine
    in the dark).
"""
import math

import numpy as np

RES = 4

# --------------------------------------------------------------- colours


def hexc(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return np.array([int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)], float)


def C(h):
    return hexc(h) if isinstance(h, str) else np.array(h, float)


def mix(a, b, t):
    return C(a) + (C(b) - C(a)) * t


def tone(c, f):
    """f < 1 darker (and a bit cooler), f > 1 lighter (and a bit warmer)."""
    c = C(c)
    if f <= 1:
        cool = np.array([18.0, 14.0, 40.0])
        return np.clip(c * f + cool * (1 - f) * 0.35, 0, 255)
    warm = np.array([255.0, 250.0, 225.0])
    return np.clip(c + (warm - c) * min(1.0, f - 1), 0, 255)


def ramp(c, n=5, lo=0.55, hi=1.45):
    """n tones from dark to light around c (index n//2 = c)."""
    out = []
    for i in range(n):
        t = i / (n - 1)
        f = lo + (hi - lo) * t if t != 0.5 else 1.0
        out.append(tone(c, f))
    return np.array(out)


# --------------------------------------------------------------- noise


def hash3(i, j, k, seed=0):
    """Deterministic noise in [0, 1) per integer voxel index (numpy arrays)."""
    i = np.asarray(i, np.int64)
    j = np.asarray(j, np.int64)
    k = np.asarray(k, np.int64)
    h = (i * 73856093) ^ (j * 19349663) ^ (k * 83492791) ^ (seed * 2654435761)
    h = h & 0xFFFFFFFF
    h = (h ^ (h >> 13)) * 1274126177 & 0xFFFFFFFF
    h = h ^ (h >> 16)
    return (h & 0xFFFF) / 65536.0


def vnoise(x, y, z, scale=1.0, seed=0):
    """Smooth value noise on model coordinates (0..1)."""
    x = np.asarray(x, float) / scale
    y = np.asarray(y, float) / scale
    z = np.asarray(z, float) / scale
    xi, yi, zi = np.floor(x), np.floor(y), np.floor(z)
    xf, yf, zf = x - xi, y - yi, z - zi
    u, v, w = xf * xf * (3 - 2 * xf), yf * yf * (3 - 2 * yf), zf * zf * (3 - 2 * zf)
    out = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                n = hash3(xi + dx, yi + dy, zi + dz, seed)
                wx = u if dx else 1 - u
                wy = v if dy else 1 - v
                wz = w if dz else 1 - w
                out = out + n * wx * wy * wz
    return out


# --------------------------------------------------------------- shapes


class Shape:
    """inside(X, Y, Z) -> bool array, bbox ((x0,y0,z0), (x1,y1,z1))."""

    def __init__(self, fn, bbox):
        self.fn = fn
        self.bbox = (np.array(bbox[0], float), np.array(bbox[1], float))

    def __call__(self, X, Y, Z):
        return self.fn(X, Y, Z)

    def __or__(self, o):
        return Shape(lambda X, Y, Z: self.fn(X, Y, Z) | o.fn(X, Y, Z),
                     (np.minimum(self.bbox[0], o.bbox[0]), np.maximum(self.bbox[1], o.bbox[1])))

    def __and__(self, o):
        return Shape(lambda X, Y, Z: self.fn(X, Y, Z) & o.fn(X, Y, Z),
                     (np.maximum(self.bbox[0], o.bbox[0]), np.minimum(self.bbox[1], o.bbox[1])))

    def __sub__(self, o):
        return Shape(lambda X, Y, Z: self.fn(X, Y, Z) & ~o.fn(X, Y, Z), self.bbox)

    def move(self, dx, dy, dz):
        d = np.array([dx, dy, dz], float)
        return Shape(lambda X, Y, Z: self.fn(X - dx, Y - dy, Z - dz), (self.bbox[0] + d, self.bbox[1] + d))

    def mirror_x(self, axis=8.0):
        """This shape plus its mirror image around x = axis."""
        m = Shape(lambda X, Y, Z: self.fn(2 * axis - X, Y, Z),
                  (np.array([2 * axis - self.bbox[1][0], self.bbox[0][1], self.bbox[0][2]]),
                   np.array([2 * axis - self.bbox[0][0], self.bbox[1][1], self.bbox[1][2]])))
        return self | m

    def flip_x(self, axis=8.0):
        return Shape(lambda X, Y, Z: self.fn(2 * axis - X, Y, Z),
                     (np.array([2 * axis - self.bbox[1][0], self.bbox[0][1], self.bbox[0][2]]),
                      np.array([2 * axis - self.bbox[0][0], self.bbox[1][1], self.bbox[1][2]])))

    def rot(self, axis, deg, origin):
        """Rotated copy (around axis 'x'/'y'/'z' through origin)."""
        a = math.radians(deg)
        c, s = math.cos(a), math.sin(a)
        ox, oy, oz = origin

        def fn(X, Y, Z):
            x, y, z = X - ox, Y - oy, Z - oz
            # inverse rotation of the query points
            if axis == "y":
                x, z = x * c - z * s, x * s + z * c
            elif axis == "x":
                y, z = y * c + z * s, -y * s + z * c
            else:
                x, y = x * c + y * s, -x * s + y * c
            return self.fn(x + ox, y + oy, z + oz)
        # bbox: rotate the 8 corners
        lo, hi = self.bbox
        pts = []
        for px in (lo[0], hi[0]):
            for py in (lo[1], hi[1]):
                for pz in (lo[2], hi[2]):
                    x, y, z = px - ox, py - oy, pz - oz
                    if axis == "y":
                        x, z = x * c + z * s, -x * s + z * c
                    elif axis == "x":
                        y, z = y * c - z * s, y * s + z * c
                    else:
                        x, y = x * c - y * s, x * s + y * c
                    pts.append((x + ox, y + oy, z + oz))
        pts = np.array(pts)
        return Shape(fn, (pts.min(0), pts.max(0)))


def box(x0, y0, z0, x1, y1, z1):
    return Shape(lambda X, Y, Z: (X >= x0) & (X < x1) & (Y >= y0) & (Y < y1) & (Z >= z0) & (Z < z1),
                 ((x0, y0, z0), (x1, y1, z1)))


def rbox(x0, y0, z0, x1, y1, z1, r):
    """Box with rounded edges (radius r)."""
    cx, cy, cz = (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2
    hx, hy, hz = (x1 - x0) / 2 - r, (y1 - y0) / 2 - r, (z1 - z0) / 2 - r

    def fn(X, Y, Z):
        qx = np.maximum(np.abs(X - cx) - hx, 0)
        qy = np.maximum(np.abs(Y - cy) - hy, 0)
        qz = np.maximum(np.abs(Z - cz) - hz, 0)
        return qx * qx + qy * qy + qz * qz <= r * r
    return Shape(fn, ((x0, y0, z0), (x1, y1, z1)))


def ellipsoid(cx, cy, cz, rx, ry, rz):
    return Shape(lambda X, Y, Z: ((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2 + ((Z - cz) / rz) ** 2 <= 1,
                 ((cx - rx, cy - ry, cz - rz), (cx + rx, cy + ry, cz + rz)))


def sphere(cx, cy, cz, r):
    return ellipsoid(cx, cy, cz, r, r, r)


def cyl(cx, cz, r, y0, y1, rz=None):
    """Vertical cylinder (elliptic with rz)."""
    rz = r if rz is None else rz
    return Shape(lambda X, Y, Z: (((X - cx) / r) ** 2 + ((Z - cz) / rz) ** 2 <= 1) & (Y >= y0) & (Y < y1),
                 ((cx - r, y0, cz - rz), (cx + r, y1, cz + rz)))


def cyl_x(cy, cz, r, x0, x1):
    return Shape(lambda X, Y, Z: ((Y - cy) ** 2 + (Z - cz) ** 2 <= r * r) & (X >= x0) & (X < x1),
                 ((x0, cy - r, cz - r), (x1, cy + r, cz + r)))


def cyl_z(cx, cy, r, z0, z1):
    return Shape(lambda X, Y, Z: ((X - cx) ** 2 + (Y - cy) ** 2 <= r * r) & (Z >= z0) & (Z < z1),
                 ((cx - r, cy - r, z0), (cx + r, cy + r, z1)))


def ring(cx, cz, r_out, r_in, y0, y1, rz_scale=1.0):
    """Flat vertical-axis ring / tube wall."""
    def fn(X, Y, Z):
        d = np.sqrt((X - cx) ** 2 + ((Z - cz) / rz_scale) ** 2)
        return (d <= r_out) & (d > r_in) & (Y >= y0) & (Y < y1)
    return Shape(fn, ((cx - r_out, y0, cz - r_out * rz_scale), (cx + r_out, y1, cz + r_out * rz_scale)))


def torus(cx, cy, cz, R, r, rz_scale=1.0):
    """Horizontal torus (ring around the y axis), tube radius r."""
    def fn(X, Y, Z):
        d = np.sqrt((X - cx) ** 2 + ((Z - cz) / rz_scale) ** 2) - R
        return d * d + (Y - cy) ** 2 <= r * r
    return Shape(fn, ((cx - R - r, cy - r, cz - (R + r) * rz_scale), (cx + R + r, cy + r, cz + (R + r) * rz_scale)))


def cone(cx, cz, r0, y0, h, r1=0.0, lean=(0.0, 0.0), rz_scale=1.0):
    """Frustum from radius r0 at y0 to r1 at y0+h, top shifted by lean."""
    def fn(X, Y, Z):
        t = (Y - y0) / h
        r = r0 + (r1 - r0) * t
        x = X - cx - lean[0] * t
        z = Z - cz - lean[1] * t
        return (t >= 0) & (t < 1) & ((x / np.maximum(r, 1e-6)) ** 2 + (z / np.maximum(r * rz_scale, 1e-6)) ** 2 <= 1)
    m = max(r0, r1)
    return Shape(fn, ((cx - m + min(0, lean[0]), y0, cz - m * rz_scale + min(0, lean[1])),
                      (cx + m + max(0, lean[0]), y0 + h, cz + m * rz_scale + max(0, lean[1]))))


def dome(cx, cz, rx, y0, h, rz=None, thick=None):
    """Upper half ellipsoid (a cap), optionally hollow with wall `thick`."""
    rz = rx if rz is None else rz

    def fn(X, Y, Z):
        d = ((X - cx) / rx) ** 2 + ((Y - y0) / h) ** 2 + ((Z - cz) / rz) ** 2
        m = (d <= 1) & (Y >= y0)
        if thick:
            d2 = ((X - cx) / (rx - thick)) ** 2 + ((Y - y0) / (h - thick)) ** 2 + ((Z - cz) / (rz - thick)) ** 2
            m &= d2 > 1
        return m
    return Shape(fn, ((cx - rx, y0, cz - rz), (cx + rx, y0 + h, cz + rz)))


def capsule(a, b, r0, r1=None):
    """Tube from point a to b, radius r0 at a to r1 at b (tapered)."""
    r1 = r0 if r1 is None else r1
    a = np.array(a, float)
    b = np.array(b, float)
    ab = b - a
    L2 = float(ab @ ab) or 1e-9

    def fn(X, Y, Z):
        px, py, pz = X - a[0], Y - a[1], Z - a[2]
        t = np.clip((px * ab[0] + py * ab[1] + pz * ab[2]) / L2, 0, 1)
        dx, dy, dz = px - ab[0] * t, py - ab[1] * t, pz - ab[2] * t
        r = r0 + (r1 - r0) * t
        return dx * dx + dy * dy + dz * dz <= r * r
    m = max(r0, r1)
    return Shape(fn, (np.minimum(a, b) - m, np.maximum(a, b) + m))


def tube(points, r0, r1=None):
    """Polyline tube through points, radius r0 -> r1 along its length."""
    r1 = r0 if r1 is None else r1
    pts = [np.array(p, float) for p in points]
    lens = [np.linalg.norm(pts[i + 1] - pts[i]) for i in range(len(pts) - 1)]
    tot = sum(lens) or 1
    out = None
    acc = 0
    for i in range(len(pts) - 1):
        ra = r0 + (r1 - r0) * acc / tot
        acc += lens[i]
        rb = r0 + (r1 - r0) * acc / tot
        s = capsule(pts[i], pts[i + 1], ra, rb)
        out = s if out is None else out | s
    return out


def bezier(p0, p1, p2, p3=None, n=12):
    """Points along a quadratic (or cubic) bezier curve."""
    out = []
    for i in range(n + 1):
        t = i / n
        if p3 is None:
            p = [(1 - t) ** 2 * p0[k] + 2 * (1 - t) * t * p1[k] + t * t * p2[k] for k in range(3)]
        else:
            p = [(1 - t) ** 3 * p0[k] + 3 * (1 - t) ** 2 * t * p1[k] + 3 * (1 - t) * t * t * p2[k] + t ** 3 * p3[k]
                 for k in range(3)]
        out.append(p)
    return out


def prism(poly2d, axis, a0, a1):
    """2D polygon (list of (u, v)) extruded along axis between a0 and a1.
    axis 'z': polygon in x/y; 'x': polygon in z/y; 'y': polygon in x/z."""
    P = np.array(poly2d, float)

    def inside(u, v):
        res = np.zeros(np.shape(u), bool)
        n = len(P)
        j = n - 1
        for i in range(n):
            xi, yi = P[i]
            xj, yj = P[j]
            cond = ((yi > v) != (yj > v)) & (u < (xj - xi) * (v - yi) / ((yj - yi) or 1e-12) + xi)
            res ^= cond
            j = i
        return res

    if axis == "z":
        fn = lambda X, Y, Z: inside(X, Y) & (Z >= a0) & (Z < a1)
        bb = ((P[:, 0].min(), P[:, 1].min(), a0), (P[:, 0].max(), P[:, 1].max(), a1))
    elif axis == "x":
        fn = lambda X, Y, Z: inside(Z, Y) & (X >= a0) & (X < a1)
        bb = ((a0, P[:, 1].min(), P[:, 0].min()), (a1, P[:, 1].max(), P[:, 0].max()))
    else:
        fn = lambda X, Y, Z: inside(X, Z) & (Y >= a0) & (Y < a1)
        bb = ((P[:, 0].min(), a0, P[:, 1].min()), (P[:, 0].max(), a1, P[:, 1].max()))
    return Shape(fn, bb)


def bitmap(rows, axis, a0, a1, x0, y0, px=1.0):
    """Pixel mask (list of strings, '.'/' ' empty) as a shape.
    axis 'z': rows in x (right) / y (down), extruded along z."""
    h = len(rows)
    w = max(len(r) for r in rows)
    grid = np.zeros((w, h), bool)
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch not in ". ":
                grid[i, j] = True

    def look(u, v):
        i = np.floor((u - x0) / px).astype(int)
        j = np.floor((y0 + h * px - v) / px).astype(int)
        ok = (i >= 0) & (i < w) & (j >= 0) & (j < h)
        out = np.zeros(np.shape(u), bool)
        out[ok] = grid[i[ok], j[ok]]
        return out

    if axis == "z":
        fn = lambda X, Y, Z: look(X, Y) & (Z >= a0) & (Z < a1)
        bb = ((x0, y0, a0), (x0 + w * px, y0 + h * px, a1))
    else:
        fn = lambda X, Y, Z: look(Z, Y) & (X >= a0) & (X < a1)
        bb = ((a0, y0, x0), (a1, y0 + h * px, x0 + w * px))
    return Shape(fn, bb)


def everything():
    return Shape(lambda X, Y, Z: np.ones(np.shape(X), bool), ((-64, -64, -64), (64, 64, 64)))


def half(axis, at, above=True):
    i = "xyz".index(axis)

    def fn(X, Y, Z):
        v = (X, Y, Z)[i]
        return v >= at if above else v < at
    lo = [-64, -64, -64]
    hi = [64, 64, 64]
    if above:
        lo[i] = at
    else:
        hi[i] = at
    return Shape(fn, (lo, hi))


# --------------------------------------------------------------- materials

SOLID, GLOW = 1, 2


class Mat:
    """colour(X, Y, Z, I, J, K) -> (N, 3) array; glow = light level 0..15."""

    def __init__(self, fn, glow=0):
        self.fn = fn
        self.glow = glow


def _pick(r, idx):
    idx = np.clip(np.asarray(idx).astype(int), 0, len(r) - 1)
    return r[idx]


def solid(c, var=0.5, seed=1, soft=0.0):
    """Base colour with a little per-voxel tone noise (soft: smooth blotches)."""
    r = ramp(c, 7, 0.78, 1.22)

    def fn(X, Y, Z, I, J, K):
        n = hash3(I, J, K, seed)
        idx = 3 + np.where(n < 0.12 * var, -1, np.where(n > 1 - 0.08 * var, 1, 0))
        if soft:
            b = vnoise(X, Y, Z, 1.8, seed)
            idx = idx + np.where(b < 0.25 * soft, -1, np.where(b > 1 - 0.2 * soft, 1, 0))
        return _pick(r, idx)
    return Mat(fn)


def flat(c):
    cc = C(c)
    return Mat(lambda X, Y, Z, I, J, K: np.tile(cc, (len(X), 1)))


def grad(c0, c1, axis="y", a0=0.0, a1=16.0, var=0.4, seed=2):
    """Gradient from c0 at a0 to c1 at a1 along axis, with noise."""
    i = "xyz".index(axis)
    c0, c1 = C(c0), C(c1)

    def fn(X, Y, Z, I, J, K):
        v = (X, Y, Z)[i]
        t = np.clip((v - a0) / ((a1 - a0) or 1e-9), 0, 1)
        t = t + (hash3(I, J, K, seed) - 0.5) * 0.12 * var
        t = np.clip(np.round(t * 6) / 6, 0, 1)   # banded like pixel art
        return c0[None] + (c1 - c0)[None] * t[:, None]
    return Mat(fn)


def metal(c, seed=3, brushed="x", spec=0.06):
    """Brushed metal: streaks along `brushed`, small bright specks."""
    r = ramp(c, 7, 0.6, 1.5)
    ax = "xyz".index(brushed)

    def fn(X, Y, Z, I, J, K):
        idx = [I, J, K]
        idx[ax] = idx[ax] * 0 + 7   # constant along the streak
        n = hash3(idx[0] // 1, idx[1], idx[2], seed)
        s = hash3(I, J, K, seed + 7)
        t = 3 + np.where(n < 0.25, -1, np.where(n > 0.8, 1, 0))
        t = np.where(s > 1 - spec, 5, t)
        return _pick(r, t)
    return Mat(fn)


GOLD = ["7a4a0c", "b8741a", "dc9b22", "f2bb2e", "ffd54a", "ffec94", "fffbe6"]
ROSE = ["6e2f2a", "a65a4c", "cf8770", "e9a88e", "f7c6ad", "ffe2d2", "fff6f0"]
SILV = ["4a5160", "7a8292", "a6adbb", "c8ced9", "e2e6ee", "f4f6fa", "ffffff"]


def gold(seed=4, tones=GOLD, sparkle=0.012):
    """Polished metal: smooth light / dark sweeps, rare glints."""
    r = np.array([C(t) for t in tones])

    def fn(X, Y, Z, I, J, K):
        n = hash3(I, J, K, seed)
        b = vnoise(X + Y * 0.6, Y, Z - Y * 0.6, 2.4, seed)
        t = 2 + np.round(b * 2.0).astype(int)
        t = np.where(n > 1 - sparkle, 6, np.where(n > 1 - 3 * sparkle, 5, t))
        return _pick(r, t)
    return Mat(fn)


def rose_gold(seed=4):
    return gold(seed, ROSE)


def silver(seed=5):
    return gold(seed, SILV, 0.01)


def gem(c, seed=6, facet=1.0):
    """Faceted gem: diagonal light / dark facets and sparkles."""
    r = ramp(c, 7, 0.5, 1.55)

    def fn(X, Y, Z, I, J, K):
        f = np.floor((X + Y * 1.3 - Z * 0.7) / facet) % 3
        t = np.where(f == 0, 4, np.where(f == 1, 3, 2))
        n = hash3(I, J, K, seed)
        t = np.where(n > 0.96, 6, t)
        return _pick(r, t)
    return Mat(fn)


def crystal(c, seed=7, glow=0):
    """Crystal: brighter towards the core axis, glints."""
    r = ramp(c, 7, 0.55, 1.6)

    def fn(X, Y, Z, I, J, K):
        n = hash3(I, J, K, seed)
        b = vnoise(X, Y, Z, 0.9, seed)
        t = 2 + np.round(b * 3).astype(int)
        t = np.where(n > 0.94, 6, t)
        return _pick(r, t)
    return Mat(fn, glow)


def fabric(c, seed=8, weave=1):
    """Woven cloth: checker of threads, soft noise."""
    r = ramp(c, 7, 0.7, 1.25)

    def fn(X, Y, Z, I, J, K):
        w = ((I // weave + J // weave + K // weave) % 2)
        n = hash3(I, J, K, seed)
        b = vnoise(X, Y, Z, 2.5, seed)
        t = 3 + w - (b < 0.3) + (n > 0.95)
        return _pick(r, t)
    return Mat(fn)


def velvet(c, seed=9):
    r = ramp(c, 7, 0.62, 1.3)

    def fn(X, Y, Z, I, J, K):
        b = vnoise(X, Y, Z, 1.6, seed)
        t = 2 + np.round(b * 2).astype(int)
        return _pick(r, t)
    return Mat(fn)


def knit(c, seed=10, axis="y"):
    """Knitted wool: V-shaped stitches in columns."""
    r = ramp(c, 7, 0.65, 1.3)

    def fn(X, Y, Z, I, J, K):
        col = (I + K) % 4
        v = (J + np.abs(col - 1.5).astype(int)) % 3
        t = np.where(v == 0, 2, np.where(col == 3, 3, 4))
        n = hash3(I, J, K, seed)
        t = t - (n < 0.08) + (n > 0.95)
        return _pick(r, t)
    return Mat(fn)


def fur(c, seed=11):
    """Fur: strands along y."""
    r = ramp(c, 7, 0.6, 1.35)

    def fn(X, Y, Z, I, J, K):
        s = hash3(I, J // 3, K, seed)
        n = hash3(I, J, K, seed + 1)
        t = 2 + np.round(s * 3).astype(int) + (n > 0.9) - (n < 0.1)
        return _pick(r, t)
    return Mat(fn)


def wood(c, seed=12, axis="y"):
    """Wood grain along axis."""
    r = ramp(c, 7, 0.6, 1.3)
    ax = "xyz".index(axis)

    def fn(X, Y, Z, I, J, K):
        q = [X, Y, Z]
        other = [q[k] for k in range(3) if k != ax]
        g = vnoise(other[0] * 2.5, other[1] * 2.5, q[ax] * 0.25, 1.0, seed)
        t = np.where(g < 0.33, 2, np.where(g < 0.6, 3, 4))
        n = hash3(I, J, K, seed)
        t = np.where(n > 0.97, 1, t)
        return _pick(r, t)
    return Mat(fn)


def leather(c, seed=13):
    r = ramp(c, 7, 0.6, 1.3)

    def fn(X, Y, Z, I, J, K):
        b = vnoise(X, Y, Z, 0.8, seed)
        n = hash3(I, J, K, seed)
        t = 2 + np.round(b * 2).astype(int) - (n < 0.1) + (n > 0.95)
        return _pick(r, t)
    return Mat(fn)


def straw(c="e8c15a", seed=14):
    """Woven straw: diagonal braid."""
    r = ramp(c, 7, 0.6, 1.3)

    def fn(X, Y, Z, I, J, K):
        d = ((I + J * 0 + K) // 2 + (J // 2)) % 3
        e = ((I - K) // 2) % 4
        t = np.where(d == 0, 2, np.where(e == 0, 5, 4))
        n = hash3(I, J, K, seed)
        t = t - (n < 0.07)
        return _pick(r, t)
    return Mat(fn)


def stone(c, seed=15):
    r = ramp(c, 7, 0.6, 1.3)

    def fn(X, Y, Z, I, J, K):
        b = vnoise(X, Y, Z, 1.0, seed)
        n = hash3(I, J, K, seed)
        t = 1 + np.round(b * 3.5).astype(int) + (n > 0.93) - (n < 0.07)
        return _pick(r, t)
    return Mat(fn)


def glow(c, level=15, seed=16, core=None):
    """Glowing material (light_emission): bright with hot spots."""
    cc = C(c)
    hot = tone(cc, 1.55) if core is None else C(core)

    def fn(X, Y, Z, I, J, K):
        n = hash3(I, J, K, seed)
        b = vnoise(X, Y, Z, 1.1, seed)
        t = np.clip(b * 0.9 + (n > 0.9) * 0.4, 0, 1)[:, None]
        return cc[None] * (1 - t) + hot[None] * t
    return Mat(fn, level)


def glass(c="9fe6ff", seed=17):
    """Opaque glass: tinted, diagonal glints."""
    r = ramp(c, 7, 0.55, 1.6)

    def fn(X, Y, Z, I, J, K):
        d = (I + J) % 9
        t = np.where(d == 0, 6, np.where(d == 1, 5, 3))
        b = vnoise(X, Y, Z, 2.0, seed)
        t = t - (b < 0.35)
        return _pick(r, t)
    return Mat(fn)


def stripes(c0, c1, period=1.0, axis="y", offset=0.0, width=0.5):
    m0, m1 = solid(c0), solid(c1)
    ax = "xyz".index(axis)

    def fn(X, Y, Z, I, J, K):
        v = ((X, Y, Z)[ax] + offset) / period
        sel = (v - np.floor(v)) < width
        a = m0.fn(X, Y, Z, I, J, K)
        b = m1.fn(X, Y, Z, I, J, K)
        return np.where(sel[:, None], a, b)
    return Mat(fn)


def checker(c0, c1, size=1.0):
    m0, m1 = solid(c0), solid(c1)

    def fn(X, Y, Z, I, J, K):
        s = (np.floor(X / size) + np.floor(Y / size) + np.floor(Z / size)) % 2 == 0
        return np.where(s[:, None], m0.fn(X, Y, Z, I, J, K), m1.fn(X, Y, Z, I, J, K))
    return Mat(fn)


def by(fn_sel, *mats):
    """Choose a material per voxel: fn_sel(X, Y, Z) -> index array."""
    def fn(X, Y, Z, I, J, K):
        sel = np.asarray(fn_sel(X, Y, Z)).astype(int)
        out = np.zeros((len(X), 3))
        for k, m in enumerate(mats):
            w = sel == k
            if w.any():
                out[w] = m.fn(X[w], Y[w], Z[w], I[w], J[w], K[w])
        return out
    return Mat(fn)


# --------------------------------------------------------------- model


class Model:
    def __init__(self, name, lo=(-8, -8, -8), hi=(24, 32, 24), res=RES):
        self.name = name
        self.res = res
        self.lo = np.array(lo, float)
        self.n = np.ceil((np.array(hi, float) - self.lo) * res).astype(int)
        self.col = np.zeros(tuple(self.n) + (3,), np.float32)
        self.mat = np.zeros(tuple(self.n), np.uint8)    # 0 empty, 1 solid, 2+ glow level + 1
        self.parts = []     # (Model, rotation) baked as separate rotated groups

    # ---- grid helpers
    def _region(self, sh):
        lo = np.floor((sh.bbox[0] - self.lo) * self.res).astype(int) - 1
        hi = np.ceil((sh.bbox[1] - self.lo) * self.res).astype(int) + 1
        lo = np.clip(lo, 0, self.n)
        hi = np.clip(hi, 0, self.n)
        if (hi <= lo).any():
            return None
        I, J, K = np.meshgrid(np.arange(lo[0], hi[0]), np.arange(lo[1], hi[1]), np.arange(lo[2], hi[2]), indexing="ij")
        X = self.lo[0] + (I + 0.5) / self.res
        Y = self.lo[1] + (J + 0.5) / self.res
        Z = self.lo[2] + (K + 0.5) / self.res
        return lo, hi, I, J, K, X, Y, Z

    def fill(self, sh, mat, only_empty=False):
        r = self._region(sh)
        if r is None:
            return self
        lo, hi, I, J, K, X, Y, Z = r
        m = sh(X, Y, Z)
        if only_empty:
            m &= self.mat[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]] == 0
        if not m.any():
            return self
        cols = np.asarray(mat.fn(X[m], Y[m], Z[m], I[m], J[m], K[m]), float)
        sub = self.col[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]]
        sub[m] = cols
        msub = self.mat[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]]
        msub[m] = SOLID if not mat.glow else 1 + mat.glow
        return self

    def paint(self, sh, mat):
        """Recolour existing voxels inside the shape (decals, bands)."""
        r = self._region(sh)
        if r is None:
            return self
        lo, hi, I, J, K, X, Y, Z = r
        m = sh(X, Y, Z) & (self.mat[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]] > 0)
        if not m.any():
            return self
        sub = self.col[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]]
        sub[m] = np.asarray(mat.fn(X[m], Y[m], Z[m], I[m], J[m], K[m]), float)
        if mat.glow:
            msub = self.mat[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]]
            msub[m] = 1 + mat.glow
        return self

    def surface(self, sh, mat, depth=1):
        """Recolour only the outer `depth` voxels inside the shape."""
        occ = self.mat > 0
        inner = occ.copy()
        for _ in range(depth):
            e = inner.copy()
            for ax in range(3):
                for d in (1, -1):
                    s = np.roll(inner, d, ax)
                    idx = [slice(None)] * 3
                    idx[ax] = 0 if d == 1 else -1
                    s[tuple(idx)] = False
                    e &= s
            inner = e
        shell = occ & ~inner
        r = self._region(sh)
        if r is None:
            return self
        lo, hi, I, J, K, X, Y, Z = r
        m = sh(X, Y, Z) & shell[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]]
        if not m.any():
            return self
        sub = self.col[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]]
        sub[m] = np.asarray(mat.fn(X[m], Y[m], Z[m], I[m], J[m], K[m]), float)
        if mat.glow:
            self.mat[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]][m] = 1 + mat.glow
        return self

    def carve(self, sh):
        r = self._region(sh)
        if r is None:
            return self
        lo, hi, I, J, K, X, Y, Z = r
        m = sh(X, Y, Z)
        self.mat[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]][m] = 0
        return self

    def part(self, axis, deg, origin, lo=None, hi=None):
        """A sub-model drawn upright and turned as a whole in game (element
        rotation): wings swept back, tilted blades."""
        p = Model(self.name + "/part", self.lo if lo is None else lo,
                  self.lo + self.n / self.res if hi is None else hi, self.res)
        self.parts.append((p, {"axis": axis, "angle": deg, "origin": list(origin)}))
        return p

    def count(self):
        return int((self.mat > 0).sum()) + sum(p.count() for p, _ in self.parts)
