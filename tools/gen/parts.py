"""Reusable HD parts for hats, back items and outfits.

Hat space: the head is x/y/z 4..12, front = north (z = 4), top at y = 12.
A skin's outer layer reaches 0.5 further (3.5..12.5): everything that wraps
the head stays outside that, so hair / hat layers never poke through.
"""
import math

import numpy as np

from hd import (Model, box, rbox, ellipsoid, sphere, cyl, cyl_x, cyl_z, ring, torus, cone, dome,
                capsule, tube, bezier, prism, bitmap, half, solid, flat, gold, silver, gem, velvet,
                fabric, knit, fur, wood, leather, straw, stone, glow, glass, metal, crystal, grad,
                stripes, checker, by, C, tone, mix, hash3, vnoise, Mat)

CX = CZ = 8.0
SIDES = (0, 90, 180, 270)


def hat_model(name):
    return Model(name, (-6, 0, -6), (22, 32, 22))


def around(shape, deg):
    """Turn a shape drawn for the front (north) side around the head."""
    return shape if deg % 360 == 0 else shape.rot("y", deg, (CX, 0, CZ))


def all_sides(m, make, mat, sides=SIDES):
    for d in sides:
        m.fill(around(make(), d), mat)


def head_band(y0, y1, out=0.9, r=0.45):
    """Rounded-square band hugging the head (outside the skin layer)."""
    out = max(out, 0.75)
    return rbox(4 - out, y0, 4 - out, 12 + out, y1, 12 + out, r) - box(3.5, y0 - 1, 3.5, 12.5, y1 + 1, 12.5)


def square_points(h, step, y, skip_corners=False):
    """Points on a square path (half size h) around the head, step apart."""
    pts = []
    n = max(1, int(round(2 * h / step)))
    for d in SIDES:
        for i in range(n):
            t = -h + i * (2 * h / n)
            if skip_corners and i == 0:
                continue
            a = math.radians(d)
            x, z = t, -h
            # rotate (x, z) around the centre by d (same sense as Shape.rot)
            rx = x * math.cos(a) + z * math.sin(a)
            rz = -x * math.sin(a) + z * math.cos(a)
            pts.append((CX + rx, y, CZ + rz))
    return pts


def circle_points(cx, cz, r, n, y, phase=0.0):
    return [(cx + r * math.cos(2 * math.pi * k / n + phase), y, cz + r * math.sin(2 * math.pi * k / n + phase))
            for k in range(n)]


def studs(m, pts, r, mat):
    for p in pts:
        m.fill(sphere(p[0], p[1], p[2], r), mat)


def set_gem(m, c, axis, size, colour, bezel=None, prongs=True, shape="oval"):
    """A gem in a metal setting on a surface; axis = outward direction
    ('-z' front, '+z' back, '-x', '+x', '+y' up)."""
    bezel = bezel or gold()
    x, y, z = c
    s = size
    sgn = 1 if axis[0] == "+" else -1
    a = axis[1]
    if a == "z":
        m.fill(ellipsoid(x, y, z, s * 1.25, s * 1.25, 0.35), bezel)
        if shape == "oval":
            g = ellipsoid(x, y, z + sgn * 0.3, s, s * 1.15, 0.4)
        else:
            g = prism([(-s, 0), (0, s * 1.2), (s, 0), (0, -s * 1.2)], "z", z + sgn * 0.0, z + sgn * 0.55).move(x, y, 0) \
                if sgn > 0 else prism([(-s, 0), (0, s * 1.2), (s, 0), (0, -s * 1.2)], "z", z - 0.55, z).move(x, y, 0)
        m.fill(g, gem(colour, facet=max(0.25, s * 0.6)))
        if prongs:
            for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                m.fill(sphere(x + dx * s * 0.85, y + dy * s * 0.95, z + sgn * 0.35, 0.2), bezel)
    elif a == "x":
        m.fill(ellipsoid(x, y, z, 0.35, s * 1.25, s * 1.25), bezel)
        m.fill(ellipsoid(x + sgn * 0.3, y, z, 0.4, s * 1.15, s), gem(colour, facet=max(0.25, s * 0.6)))
        if prongs:
            for dz, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                m.fill(sphere(x + sgn * 0.35, y + dy * s * 0.95, z + dz * s * 0.85, 0.2), bezel)
    else:
        m.fill(ellipsoid(x, y, z, s * 1.25, 0.35, s * 1.25), bezel)
        m.fill(ellipsoid(x, y + 0.3, z, s, 0.45, s), gem(colour, facet=max(0.25, s * 0.6)))


def brim(cx, cz, r_out, r_in, y, thick=0.5, droop=0.0, rz=1.0):
    """Hat brim: flat ring, edge bent down by `droop`."""
    def fn(X, Y, Z):
        d = np.sqrt((X - cx) ** 2 + ((Z - cz) / rz) ** 2)
        t = np.clip((d - r_in) / max(1e-6, r_out - r_in), 0, 1)
        yy = y - droop * t * t
        return (d <= r_out) & (d > r_in) & (Y >= yy) & (Y < yy + thick)
    from hd import Shape
    return Shape(fn, ((cx - r_out, y - droop - 0.1, cz - r_out * rz), (cx + r_out, y + thick, cz + r_out * rz)))


def rolled_edge(cx, cz, R, y, r, rz=1.0):
    return torus(cx, y, cz, R, r, rz)


def horn(m, pts, r0, r1, mat, band=None, every=1.0):
    """Tapered curved horn through pts; optional ring bands."""
    m.fill(tube(pts, r0, r1), mat)
    if band is not None:
        P = np.array(pts, float)
        L = np.sum(np.linalg.norm(np.diff(P, axis=0), axis=1))
        acc = 0
        k = 1
        for i in range(len(P) - 1):
            seg = np.linalg.norm(P[i + 1] - P[i])
            while acc + seg >= k * every and k * every < L * 0.85:
                t = (k * every - acc) / seg
                p = P[i] + (P[i + 1] - P[i]) * t
                r = r0 + (r1 - r0) * (k * every / L)
                m.paint(sphere(p[0], p[1], p[2], r * 1.05) - sphere(p[0], p[1], p[2], r * 0.6), band)
                k += 1
            acc += seg


def ear(m, base, h, w, d, lean, mat, inner=None, tilt=0.0):
    """Animal ear: flattened tapered cone, inner colour on the front."""
    x, y, z = base
    m.fill(cone(x, z, w, y, h, r1=0.15, lean=(lean, tilt), rz_scale=d / w), mat)
    if inner is not None:
        m.paint(cone(x, z - d * 0.55, w * 0.62, y + 0.4, h * 0.8, r1=0.1, lean=(lean, tilt), rz_scale=d / w), inner)


def flower(m, c, colour, petals=5, r=0.9, centre="ffd54a", axis="y"):
    x, y, z = c
    for k in range(petals):
        a = 2 * math.pi * k / petals
        if axis == "y":
            m.fill(ellipsoid(x + math.cos(a) * r * 0.7, y, z + math.sin(a) * r * 0.7, r * 0.55, 0.3, r * 0.55),
                   solid(colour, 0.6))
        else:
            m.fill(ellipsoid(x + math.cos(a) * r * 0.7, y + math.sin(a) * r * 0.7, z, r * 0.55, r * 0.55, 0.3),
                   solid(colour, 0.6))
    m.fill(sphere(x, y + (0.15 if axis == "y" else 0), z - (0.15 if axis != "y" else 0), r * 0.38), solid(centre, 0.8))


def leaf(m, c, length, width, ang, mat, y_tilt=0.0):
    """Flat leaf lying around point c, pointing at angle ang (degrees, around y)."""
    a = math.radians(ang)
    tip = (c[0] + math.cos(a) * length, c[1] + y_tilt, c[2] + math.sin(a) * length)
    m.fill(capsule(c, tip, width, 0.12) & ellipsoid((c[0] + tip[0]) / 2, (c[1] + tip[1]) / 2, (c[2] + tip[2]) / 2,
                                                    length * 0.6, max(0.3, width * 0.6), length * 0.6), mat)


def rivets(m, pts, mat=None, r=0.22):
    mat = mat or silver()
    for p in pts:
        m.fill(sphere(p[0], p[1], p[2], r), mat)


def stitch_line(m, a, b, mat, dash=0.5):
    """Dashed line painted onto existing voxels between a and b."""
    a = np.array(a, float)
    b = np.array(b, float)
    L = np.linalg.norm(b - a)
    n = max(1, int(L / dash))
    for i in range(0, n, 2):
        p = a + (b - a) * (i + 0.5) / n
        m.paint(sphere(p[0], p[1], p[2], 0.2), mat)


def lens(m, c, r, depth, frame_mat, glass_col="7fd9ff", axis="-z", glow_lvl=0):
    x, y, z = c
    if axis[1] == "z":
        sg = -1 if axis[0] == "-" else 1
        m.fill(cyl_z(x, y, r + 0.35, min(z, z + sg * depth), max(z, z + sg * depth)), frame_mat)
        gl = glow(glass_col, glow_lvl) if glow_lvl else glass(glass_col)
        zz = z + sg * depth
        m.fill(cyl_z(x, y, r, min(zz, zz + sg * 0.25), max(zz, zz + sg * 0.25)), gl)
    else:
        sg = -1 if axis[0] == "-" else 1
        m.fill(cyl_x(y, z, r + 0.35, min(x, x + sg * depth), max(x, x + sg * depth)), frame_mat)
        gl = glow(glass_col, glow_lvl) if glow_lvl else glass(glass_col)
        xx = x + sg * depth
        m.fill(cyl_x(y, z, r, min(xx, xx + sg * 0.25), max(xx, xx + sg * 0.25)), gl)


def pearl():
    return solid("f6f2ff", 0.5)


def bow(m, c, w, h, mat, knot=None, axis="z"):
    x, y, z = c
    if axis == "z":
        m.fill(prism([(0, 0), (-w, h / 2), (-w, -h / 2)], "z", z - 0.35, z + 0.35).move(x, y, 0), mat)
        m.fill(prism([(0, 0), (w, h / 2), (w, -h / 2)], "z", z - 0.35, z + 0.35).move(x, y, 0), mat)
        m.fill(rbox(x - 0.45, y - 0.45, z - 0.5, x + 0.45, y + 0.45, z + 0.5, 0.2), knot or mat)
    else:
        m.fill(prism([(0, 0), (-w, h / 2), (-w, -h / 2)], "x", x - 0.35, x + 0.35).move(0, y, z), mat)
        m.fill(prism([(0, 0), (w, h / 2), (w, -h / 2)], "x", x - 0.35, x + 0.35).move(0, y, z), mat)
        m.fill(rbox(x - 0.5, y - 0.45, z - 0.45, x + 0.5, y + 0.45, z + 0.45, 0.2), knot or mat)


def star_points(cx, cy, r_out, r_in, n=5, rot=90.0):
    pts = []
    for k in range(2 * n):
        r = r_out if k % 2 == 0 else r_in
        a = math.radians(rot + 180.0 * k / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def cap_shell(y0, y1, out=0.8, r=1.6):
    """Rounded box hugging the (square) head from y0 up to y1."""
    return (rbox(4 - out, y0 - r, 4 - out, 12 + out, y1, 12 + out, r) & half("y", y0)) - box(3.5, y0 - 1, 3.5, 12.5, 12.5, 12.5)


def tri_dist(X, Z, cx=8.0, cz=8.0, rot=-90.0):
    """'Radius' of a point in a triangle (edge normals every 120 deg)."""
    d = None
    for k in range(3):
        a = math.radians(rot + 120 * k)
        v = (X - cx) * math.cos(a) + (Z - cz) * math.sin(a)
        d = v if d is None else np.maximum(d, v)
    return d


def helmet_shell(x0, y0, z0, x1, y1, z1, r, bottom_r=0.0):
    """Full helmet around the head: rounded top edges, straight sides down to y0."""
    outer = rbox(x0, y0 - r, z0, x1, y1, z1, r) & half("y", y0)
    return outer - rbox(3.45, y0 - 2, 3.45, 12.55, 12.55, 12.55, 0.3)
