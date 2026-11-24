"""HD wing generators. Body space: torso x 4..12, y 2..14, z 6..10, back side
at z = 6 (items live at z < 6), the player's left is +x.

A wing is drawn flat for the LEFT side (from the root out to +x) into its
own part, which is turned back around the y axis at the root (sweep) in
game; the right wing is the mirror image (same voxels mirrored around
x = 8, turned the other way).
"""
import math

import numpy as np

from hd import (Model, box, rbox, ellipsoid, sphere, capsule, tube, prism, cone, bezier, solid, flat, grad,
                glow, crystal, metal, gold, silver, C, tone, mix, hash3, Mat, Shape)

ROOT_Y = 11.5
ROOT_Z = 4.4


def back_model(name):
    return Model(name, (-10, -8, -6), (26, 28, 8))


def outline(part, colour, z0, z1, width=1):
    """Dark pixel outline around the part's silhouette (seen along z)."""
    occ = part.mat > 0
    sil = occ.any(axis=2)
    d = sil.copy()
    for _ in range(width):
        e = d.copy()
        e[1:, :] |= d[:-1, :]
        e[:-1, :] |= d[1:, :]
        e[:, 1:] |= d[:, :-1]
        e[:, :-1] |= d[:, 1:]
        d = e
    ring = d & ~sil
    k0 = int(np.floor((z0 - part.lo[2]) * part.res))
    k1 = int(np.ceil((z1 - part.lo[2]) * part.res))
    c = C(colour)
    for k in range(max(0, k0), min(part.n[2], k1)):
        part.mat[ring, k] = 1
        part.col[ring, k] = c


def mirrored(m, part_l, sweep, root):
    """Add the right wing: mirror of part_l, turned the other way."""
    rx, ry, rz = root
    pr = m.part("y", -sweep, (16 - rx, ry, rz))
    pr.col[:] = part_l.col[::-1]
    pr.mat[:] = part_l.mat[::-1]
    return pr


def wing_pair(m, draw, sweep=22.5, root=(9.0, ROOT_Y, ROOT_Z), outline_col="17141f", outline_w=1, depth=(3.6, 5.2)):
    """draw(part, root) paints the left wing; adds both wings to m."""
    pl = m.part("y", sweep, root)
    draw(pl, root)
    if outline_col:
        outline(pl, outline_col, depth[0], depth[0] + 0.25, outline_w)
    mirrored(m, pl, sweep, root)
    return pl


# ------------------------------------------------------------------ feathers


def feather(p, base, tip, w, c_base, c_tip, z0, z1, shaft=None, edge=None, seed=0):
    """One feather: tapered rounded blade from base to tip, colour gradient,
    darker edge and shaft line."""
    bx, by_ = base
    tx, ty = tip
    L = math.hypot(tx - bx, ty - by_)
    zc = (z0 + z1) / 2
    blade = capsule((bx, by_, zc), (tx, ty, zc), w * 0.55, w) & box(-50, -50, z0, 50, 50, z1)
    blade = blade & ellipsoid((bx + tx) / 2, (by_ + ty) / 2, zc, L * 0.62 + w, L * 0.62 + w, 5)
    cb, ct = C(c_base), C(c_tip)

    def colfn(X, Y, Z, I, J, K):
        t = np.clip(((X - bx) * (tx - bx) + (Y - by_) * (ty - by_)) / (L * L + 1e-9), 0, 1)
        t = np.round(t * 5) / 5
        n = hash3(I, J, K, seed)
        col = cb[None] + (ct - cb)[None] * t[:, None]
        col = col * (0.95 + 0.07 * n[:, None])
        return col
    p.fill(blade, Mat(colfn))
    if edge is not None:
        inner = capsule((bx, by_, zc), (tx, ty, zc), w * 0.55 - 0.25, w - 0.3) & box(-50, -50, z0 - 1, 50, 50, z1 + 1)
        p.paint((blade - inner) & box(-50, -50, z0 - 1, 50, 50, z0 + 0.26), solid(edge, 0.3))
    if shaft is not None:
        p.paint(capsule((bx, by_, z0), (bx + (tx - bx) * 0.82, by_ + (ty - by_) * 0.82, z0), 0.13) & box(-50, -50, z0 - 1, 50, 50, z0 + 0.26),
                solid(shaft, 0.2))


def feather_wing(p, root, W=14.0, H=14.0, base="f4f6fa", mid="dfe5ef", tip="ffffff", shaft="c9d0de", edge="aab3c4",
                 arm="e8ecf4", n=11, coverts=True, cov_base=None, cov_tip=None, curl=0.0, acc=None):
    """Bird wing: leading edge arc, long flight feathers below, coverts over them."""
    rx, ry, rz = root
    lead = bezier((rx, ry, 0), (rx + W * 0.35, ry + H * 0.42, 0), (rx + W * 0.8, ry + H * 0.42, 0), (rx + W, ry + H * 0.18, 0), n=40)
    lead = [(q[0], q[1]) for q in lead]
    zb0, zb1 = rz - 0.8, rz - 0.2       # flight feathers (back layer)
    zc0, zc1 = rz - 1.1, rz - 0.6       # coverts (in front of them, seen from behind)
    for i in range(n):
        t = (i + 0.5) / n
        bx, by_ = lead[int(t * (len(lead) - 1))]
        ang = math.radians(-100 + 62 * t ** 1.2)
        L = H * (0.42 + 0.58 * t ** 0.9)
        tipx, tipy = bx + math.cos(ang) * L, by_ + math.sin(ang) * L + curl * t
        w = 0.85 + 0.45 * t
        feather(p, (bx, by_), (tipx, tipy), w, mid, tip, zb0, zb1, shaft, edge, seed=i)
    if coverts:
        for i in range(n + 2):
            t = (i + 0.3) / (n + 2)
            bx, by_ = lead[int(t * (len(lead) - 1))]
            ang = math.radians(-96 + 50 * t)
            L = H * (0.22 + 0.2 * t)
            feather(p, (bx, by_ - 0.2), (bx + math.cos(ang) * L, by_ - 0.2 + math.sin(ang) * L), 0.9 + 0.3 * t,
                    cov_base or base, cov_tip or mid, zc0, zc1, None, edge, seed=50 + i)
    # leading edge (arm)
    pts = [(x, y, rz - 0.6) for x, y in lead[::4]] + [(lead[-1][0], lead[-1][1], rz - 0.6)]
    p.fill(tube(pts, 0.75, 0.4), solid(arm, 0.4))
    if acc:
        p.fill(tube(pts[:5], 0.5, 0.45), acc)


# ------------------------------------------------------------------ membrane


def membrane_wing(p, root, W=15.0, H=15.0, skin="3a2a4a", skin2="4e3a63", bone="2a1e36", claw="e6dfd0", fingers=4, glow_vein=None):
    rx, ry, rz = root
    z0, z1 = rz - 0.75, rz - 0.25
    wrist = (rx + W * 0.42, ry + H * 0.38)
    tips = []
    for k in range(fingers):
        a = math.radians(30 - k * (95 / max(1, fingers - 1)) - 15)
        L = W * (0.62 - 0.08 * k)
        tips.append((wrist[0] + math.cos(a) * L, wrist[1] + math.sin(a) * L))
    low = (rx + W * 0.08, ry - H * 0.55)
    poly_pts = [(rx, ry), wrist] + tips + [low]
    # membrane: fan of triangles, scalloped lower edge
    mem = None
    chain = [wrist] + tips + [low]
    for i in range(1, len(chain) - 1):
        tri = prism([wrist, chain[i], chain[i + 1]], "z", z0, z1)
        mem = tri if mem is None else mem | tri
    mem = mem | prism([(rx, ry), wrist, low], "z", z0, z1)
    for i in range(1, len(chain) - 1):
        a, b = chain[i], chain[i + 1]
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        nx, ny = dy / L, -dx / L
        if nx * (mx - wrist[0]) + ny * (my - wrist[1]) < 0:
            nx, ny = -nx, -ny
        cx, cy = mx + nx * L * 0.62, my + ny * L * 0.62
        mem = mem - ellipsoid(cx, cy, (z0 + z1) / 2, L * 0.6, L * 0.6, 3)
    sk, sk2 = C(skin), C(skin2)

    def mcol(X, Y, Z, I, J, K):
        d = np.hypot(X - wrist[0], Y - wrist[1]) / (W * 0.6)
        t = np.clip(np.round(d * 4) / 4, 0, 1)
        n = hash3(I // 2, J // 2, K, 3)
        c = sk[None] * (1 - t[:, None]) + sk2[None] * t[:, None]
        return c * (0.94 + 0.08 * n[:, None])
    p.fill(mem, Mat(mcol))
    zc = rz - 0.95
    p.fill(tube([(rx, ry, zc), (wrist[0], wrist[1], zc)], 0.75, 0.55), solid(bone, 0.4))
    for t in tips:
        p.fill(tube([(wrist[0], wrist[1], zc), (t[0], t[1], zc)], 0.45, 0.15), solid(bone, 0.4))
        if glow_vein:
            p.paint(capsule((wrist[0], wrist[1], z0), (t[0], t[1], z0), 0.12) & box(-50, -50, z0 - 1, 50, 50, z0 + 0.26), glow(glow_vein, 12))
    p.fill(cone(wrist[0], zc, 0.5, wrist[1] + 0.2, 1.6, r1=0.05, lean=(-0.8, 0)), solid(claw, 0.3))
    p.fill(sphere(wrist[0], wrist[1], zc, 0.85), solid(bone, 0.4))


# ------------------------------------------------------------------ insect


def insect_wing(p, root, W=12.0, H=12.0, fill="aab8cc", vein="6f7c92", edge="586477", spots=(), spot_col="f8f8f8",
                pattern=None, glassy=False):
    rx, ry, rz = root
    z0, z1 = rz - 0.6, rz - 0.2
    fore = ellipsoid(rx + W * 0.5, ry + H * 0.2, 0, W * 0.52, H * 0.36, 9).rot("z", 18, (rx, ry, 0)) & box(-50, -50, z0, 50, 50, z1)
    hind = ellipsoid(rx + W * 0.36, ry - H * 0.28, 0, W * 0.36, H * 0.3, 9).rot("z", -25, (rx, ry, 0)) & box(-50, -50, z0, 50, 50, z1)
    fc = C(fill)

    def col(X, Y, Z, I, J, K):
        n = hash3(I // 2, J // 2, K, 7)
        d = np.hypot(X - rx, Y - ry) / W
        base = fc[None] * (0.92 + 0.1 * n[:, None])
        if glassy:
            base = base * (1.05 - 0.15 * d[:, None]) + 18 * ((I + J) % 7 == 0)[:, None]
        return np.clip(base, 0, 255)
    p.fill(fore | hind, Mat(col) if pattern is None else pattern)
    # veins radiating from the root + edge
    for a in (-55, -30, -8, 14, 34, 52):
        r = math.radians(a)
        L = W * (0.95 if a > -20 else 0.7)
        p.paint(capsule((rx, ry, z0), (rx + math.cos(r) * L, ry + math.sin(r) * L, z0), 0.14) & box(-50, -50, z0 - 1, 50, 50, z0 + 0.26),
                solid(vein, 0.2))
    inner_f = ellipsoid(rx + W * 0.5, ry + H * 0.2, 0, W * 0.52 - 0.45, H * 0.36 - 0.45, 9).rot("z", 18, (rx, ry, 0))
    inner_h = ellipsoid(rx + W * 0.36, ry - H * 0.28, 0, W * 0.36 - 0.45, H * 0.3 - 0.45, 9).rot("z", -25, (rx, ry, 0))
    p.paint((fore - inner_f) | (hind - inner_h), solid(edge, 0.3))
    for sx, sy, r in spots:
        p.paint(ellipsoid(rx + sx, ry + sy, z0, r, r, 2), solid(spot_col, 0.3))


# ------------------------------------------------------------------ blades / shards / leaves


def blade_wing(p, root, n=5, L0=7.0, L1=13.0, w=1.3, plate="b8c0cc", dark="5c6474", line="39d4ff", spread=(10, -60)):
    rx, ry, rz = root
    zc = rz - 0.5
    for i in range(n):
        t = i / max(1, n - 1)
        a = math.radians(spread[0] + (spread[1] - spread[0]) * t)
        L = L0 + (L1 - L0) * (1 - abs(t - 0.35))
        sx, sy = rx + 0.6, ry - i * 0.5
        ex, ey = sx + math.cos(a) * L, sy + math.sin(a) * L
        bl = capsule((sx, sy, zc), (ex, ey, zc), w * 0.7, w * 0.45) & box(-50, -50, zc - 0.35 - 0.1 * i, 50, 50, zc + 0.35)
        p.fill(bl, metal(plate, brushed="x"))
        p.paint(capsule((sx, sy, zc - 0.5), (ex, ey, zc - 0.5), 0.18) & box(-50, -50, zc - 1, 50, 50, zc - 0.2 - 0.1 * i), glow(line, 14))
        p.fill(sphere(sx, sy, zc, 0.55), metal(dark))
    p.fill(rbox(rx - 0.4, ry - 3.2, zc - 0.6, rx + 1.6, ry + 1.2, zc + 0.6, 0.4), metal(dark))


def shard_wing(p, root, n=7, L0=5.0, L1=13.0, colour="9ce8ff", core="f0ffff", spread=(25, -70), seed=1):
    rx, ry, rz = root
    zc = rz - 0.55
    for i in range(n):
        t = i / max(1, n - 1)
        a = math.radians(spread[0] + (spread[1] - spread[0]) * t)
        L = L0 + (L1 - L0) * math.sin(math.pi * (0.25 + 0.6 * t))
        sx, sy = rx + 0.4, ry - 0.3 * i
        ex, ey = sx + math.cos(a) * L, sy + math.sin(a) * L
        w = 0.9 + 0.35 * math.sin(math.pi * t)
        p.fill(capsule((sx, sy, zc), (ex, ey, zc), w, 0.12) & box(-50, -50, zc - 0.45, 50, 50, zc + 0.45), crystal(colour, seed + i))
        p.paint(capsule((sx, sy, zc - 0.45), (sx + (ex - sx) * 0.7, sy + (ey - sy) * 0.7, zc - 0.45), 0.2)
                & box(-50, -50, zc - 1, 50, 50, zc - 0.2), glow(core, 13))


def leaf_wing(p, root, n=5, L0=7.0, L1=12.0, leaf_c="4fae45", vein="2f7a2a", light="8fdc6a", spread=(30, -60)):
    rx, ry, rz = root
    zc = rz - 0.5
    for i in range(n):
        t = i / max(1, n - 1)
        a = math.radians(spread[0] + (spread[1] - spread[0]) * t)
        L = L0 + (L1 - L0) * math.sin(math.pi * (0.3 + 0.55 * t))
        sx, sy = rx + 0.5, ry - 0.4 * i
        ex, ey = sx + math.cos(a) * L, sy + math.sin(a) * L
        mx, my = (sx + ex) / 2, (sy + ey) / 2
        lf = ellipsoid(mx, my, zc, L * 0.5, L * 0.19, 0.35).rot("z", math.degrees(a), (mx, my, zc))
        p.fill(lf, grad(leaf_c, light, "x", sx, ex))
        p.paint(capsule((sx, sy, zc - 0.35), (ex, ey, zc - 0.35), 0.13) & box(-50, -50, zc - 1, 50, 50, zc - 0.1), solid(vein, 0.2))
        for k in range(1, 5):
            q = k / 5
            px_, py_ = sx + (ex - sx) * q, sy + (ey - sy) * q
            for s in (-1, 1):
                b = a + s * math.radians(50)
                l2 = L * 0.15 * (1 - abs(q - 0.5))
                p.paint(capsule((px_, py_, zc - 0.35), (px_ + math.cos(b) * l2, py_ + math.sin(b) * l2, zc - 0.35), 0.1)
                        & box(-50, -50, zc - 1, 50, 50, zc - 0.1), solid(vein, 0.2))
