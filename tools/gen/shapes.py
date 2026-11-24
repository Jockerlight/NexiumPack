"""Shape helpers shared by the cosmetics (on top of vox.Vox)."""
import math
from vox import hexc, shade, mix

# the player's head in hat models: x/y/z 4..12, front = north (z = 4 side)
H0, H1 = 4, 12


def C(h):
    return hexc(h)


def sq_ring(v, x0, z0, x1, z1, y0, y1, c):
    """Square frame on the x/z plane (end exclusive), heights y0..y1."""
    for x in range(x0, x1):
        for z in range(z0, z1):
            if x in (x0, x1 - 1) or z in (z0, z1 - 1):
                for y in range(y0, y1):
                    v.set(x, y, z, c(x, y, z) if callable(c) else c)


def slab(v, x0, z0, x1, z1, y, c, y1=None):
    v.box(x0, y, z0, x1, (y + 1) if y1 is None else y1, z1, c)


def dome(v, cx, cz, r, y0, h, c, flat=0.0):
    """Rounded cap: discs from radius r at y0 to ~0 at y0+h."""
    for i in range(h):
        t = (i + 0.5) / h
        rr = r * math.sqrt(max(0.0, 1 - t ** (2 - flat)))
        if rr < 0.6:
            rr = 0.6
        v.disc(cx, cz, rr, y0 + i, c)


def cone(v, cx, cz, r0, y0, h, c, lean=(0.0, 0.0), r1=0.5):
    """Stacked discs from radius r0 to r1; lean = total x/z drift at the top."""
    for i in range(h):
        t = i / max(1, h - 1)
        rr = r0 + (r1 - r0) * t
        dx = lean[0] * t * t
        dz = lean[1] * t * t
        v.disc(cx + dx, cz + dz, max(0.5, rr), y0 + i, c)


def circle_pts(cx, cz, r, n, phase=0.0):
    out = []
    for k in range(n):
        a = phase + 2 * math.pi * k / n
        out.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return out


def stud(v, x, y, z, c):
    v.set(int(math.floor(x)), y, int(math.floor(z)), c)


def ear(v, x0, z0, w, h, y0, outer, inner=None, tip=None, depth=1, taper=True):
    """A flat triangular-ish ear standing up (x/y plane) at z0..z0+depth."""
    for j in range(h):
        ww = w
        if taper:
            ww = max(1, round(w * (1 - j / (h + 0.5))))
        off = (w - ww) // 2
        for i in range(ww):
            col = outer
            if inner is not None and 0 < i < ww - 1 and j < h - 1:
                col = inner
            if tip is not None and j >= h - 1:
                col = tip
            for d in range(depth):
                v.set(x0 + off + i, y0 + j, z0 + d, col)


def stripes(c1, c2, n=2, axis=1):
    """Colour function: bands of n along an axis."""
    def f(x, y, z):
        k = (x, y, z)[axis]
        return c1 if (k // n) % 2 == 0 else c2
    return f


def noise(c, amt=0.08, seed=1):
    """Colour function: a light, the base or a dark shade per voxel (hash, no
    RNG state). Only 3 colours, so neighbours still merge into big boxes."""
    lo, hi = shade(c, 1 - amt), shade(c, 1 + amt * 0.6)
    def f(x, y, z):
        h = (x * 73856093) ^ (y * 19349663) ^ (z * 83492791) ^ (seed * 2654435761)
        h = (h & 0xFFFFFFFF) % 7
        return lo if h == 0 else (hi if h == 1 else c)
    return f
