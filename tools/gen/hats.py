"""The 54 hats in HD (4 voxels per pixel). Head = x/y/z 4..12, front = north
(z = 4), top at y = 12; everything around the head stays outside 3.5..12.5."""
import math

import numpy as np

from parts import *  # noqa: F401,F403
from hd import Shape

HATS = []


def hat(id, name, rarity):
    def deco(fn):
        HATS.append((id, name, rarity, fn))
        return fn
    return deco


TOP = 12.5   # first free height above the head (skin layer included)


# ------------------------------------------------------------- row 1

@hat("cyber_halo", "Cyber Halo", "EPIC")
def cyber_halo():
    m = hat_model("cyber_halo")
    cyan = glow("39d4ff", 15, core="d8fbff")
    deep = glow("1f7bd6", 12)
    y = 16.2
    ringy = torus(8, y, 8, 4.3, 0.5)
    m.fill(ringy, cyan)
    # 12 segments: dark gaps
    for k in range(12):
        a = 2 * math.pi * k / 12
        m.carve(box(-0.18, -2, -6, 0.18, 2, 6).rot("y", math.degrees(a), (0, 0, 0)).move(8, y, 8)
                & torus(8, y, 8, 4.3, 0.6))
    m.fill(torus(8, y, 8, 3.35, 0.22), deep)
    m.fill(torus(8, y, 8, 5.25, 0.18), deep)
    # ticks and floating shards
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        x, z = 8 + math.cos(a) * 5.7, 8 + math.sin(a) * 5.7
        m.fill(prism([(0, -0.7), (0.4, 0), (0, 0.7), (-0.4, 0)], "z", z - 0.2, z + 0.2).move(x, y + (0.9 if k % 2 else -0.6), 0),
               glow("bff3ff", 15))
    for k in range(4):
        a = 2 * math.pi * k / 4
        x, z = 8 + math.cos(a) * 4.3, 8 + math.sin(a) * 4.3
        m.fill(rbox(x - 0.45, y - 0.45, z - 0.45, x + 0.45, y + 0.45, z + 0.45, 0.15), solid("e9f6ff", 0.3))
        m.fill(sphere(x, y + 1.0, z, 0.22), glow("ffffff", 15))
    return m


@hat("crown", "Crown", "RARE")
def crown():
    m = hat_model("crown")
    G = gold()
    m.fill(head_band(11.0, 13.6, 0.85, 0.4), G)
    m.fill(head_band(10.8, 11.3, 1.1, 0.25), G)
    m.fill(head_band(13.3, 13.8, 1.1, 0.25), G)
    m.fill(dome(8, 8, 4.1, TOP, 3.1), velvet("a3123a"))
    # velvet folds: darker meridians
    for k in range(8):
        a = math.degrees(2 * math.pi * k / 8)
        m.paint(box(-0.13, 12, -6, 0.13, 17, 0).rot("y", a, (0, 0, 0)).move(8, 0, 8), velvet("6e0a26"))
    m.fill(sphere(8, 15.7, 8, 0.75), G)
    m.fill(cyl(8, 8, 0.22, 16.2, 17.6), G)
    m.fill(box(7.3, 16.9, 7.85, 8.7, 17.3, 8.15), G)
    spike = prism([(-0.95, 0), (0.95, 0), (0.3, 2.4), (0, 3.1), (-0.3, 2.4)], "z", -0.25, 0.25)
    small = prism([(-0.6, 0), (0.6, 0), (0, 1.7)], "z", -0.2, 0.2)
    for d in SIDES:
        for t in (-2.9, 0, 2.9):
            m.fill(around(spike.move(8 + t, 13.7, 3.35), d), G)
            m.fill(around(sphere(8 + t, 13.7 + 3.25, 3.35, 0.42), d), pearl())
        for t in (-1.45, 1.45):
            m.fill(around(small.move(8 + t, 13.7, 3.35), d), G)
    m.fill(sphere(3.3, 17.0, 3.3, 0.45), pearl())
    gems = ["d4183a", "2f7bff", "1fbf5f", "2f7bff"]
    for i, d in enumerate(SIDES):
        for t, col in ((-2.9, "e8f6ff"), (0, gems[i]), (2.9, "e8f6ff")):
            s = 0.55 if t == 0 else 0.32
            m.fill(around(ellipsoid(8 + t, 12.2, 3.05, s * 1.3, s * 1.3, 0.3), d), G)
            m.fill(around(ellipsoid(8 + t, 12.2, 2.85, s, s * 1.15, 0.32), d), gem(col, facet=0.3))
    for p in square_points(4.95, 0.75, 10.95):
        m.fill(sphere(*p, 0.2), pearl())
    return m


@hat("fishing_cap", "Fishing Cap", "COMMON")
def fishing_cap():
    m = hat_model("fishing_cap")
    blue = fabric("2f5f9e")
    dark = fabric("1f3f6e")
    m.fill(rbox(3.1, 10.2, 3.1, 12.9, 15.0, 12.9, 1.3) - box(3.6, 9, 3.6, 12.4, 12.5, 12.4), blue)
    # panel seams + button
    for d in (45, 135):
        m.paint(box(-0.12, 10, -7, 0.12, 16, 7).rot("y", d, (0, 0, 0)).move(8, 0, 8), dark)
    m.paint(box(7.88, 10, 2, 8.12, 16, 14), dark)
    m.fill(cyl(8, 8, 0.6, 14.7, 15.4), dark)
    # band
    m.paint(head_band(10.2, 11.0, 1.2, 0.3), fabric("d8d2c2"))
    # visor (front brim), curved
    vis = ellipsoid(8, 10.4, 3.6, 4.6, 0.32, 3.4) & box(2, 9, -2, 14, 12, 3.6)
    m.fill(vis, dark)
    m.fill((ellipsoid(8, 10.35, 3.6, 4.85, 0.36, 3.65) - ellipsoid(8, 10.35, 3.6, 4.5, 0.6, 3.3)) & box(2, 9, -2, 14, 12, 3.6),
           fabric("d8d2c2"))
    for r in (1.6, 2.4):
        m.paint((ellipsoid(8, 10.4, 3.6, 4.6 - r + 0.12, 0.6, 3.4 - r + 0.12) - ellipsoid(8, 10.4, 3.6, 4.6 - r - 0.12, 0.7, 3.4 - r - 0.12))
                & box(2, 10.4, -2, 14, 12, 3.4), fabric("9db6dd"))
    # patch on the front
    m.fill(rbox(6.0, 12.4, 2.9, 10.0, 14.2, 3.4, 0.3), fabric("e9e2cf"))
    m.fill(prism([(-1.3, 0), (0.6, 0.6), (1.2, 0), (0.6, -0.6)], "z", 2.75, 2.95).move(7.8, 13.3, 0), solid("e06a2c"))
    m.fill(sphere(8.8, 13.45, 2.8, 0.12), solid("101010"))
    # bobber + hook on the side
    m.fill(sphere(13.5, 12.6, 8.5, 0.75), solid("e8e8e8"))
    m.fill(sphere(13.5, 12.6, 8.5, 0.75) & half("y", 12.6), solid("d22d2d"))
    m.fill(cyl(13.5, 8.5, 0.15, 13.2, 14.1), solid("333333"))
    m.fill(tube([(13.4, 12.0, 9.5), (13.45, 11.0, 9.7), (13.5, 10.6, 10.3), (13.5, 11.0, 10.9)], 0.12), silver())
    m.fill(tube([(13.4, 14.0, 8.5), (13.2, 14.6, 9.5), (13.0, 14.3, 10.8)], 0.08), solid("f0f0f0"))
    return m


@hat("straw_hat", "Straw Hat", "COMMON")
def straw_hat():
    m = hat_model("straw_hat")
    S = straw("e9c25e")
    m.fill(brim(8, 8, 8.6, 4.0, 11.6, 0.6, 0.9), S)
    m.fill(rolled_edge(8, 8, 8.4, 11.0, 0.42), straw("d6a843"))
    m.fill(cyl(8, 8, 4.6, 11.6, 14.2) - cyl(8, 8, 4.1, 11, 14), S)
    m.fill(dome(8, 8, 4.6, 14.1, 1.4), S)
    m.carve(dome(8, 8, 2.2, 15.2, 0.6))
    m.fill(dome(8, 8, 2.4, 14.9, 0.55), straw("cfa143"))
    # woven rings on the brim
    for r in (5.5, 6.7, 7.8):
        m.paint(ring(8, 8, r + 0.14, r - 0.14, 10, 13), straw("c49234"))
    # red ribbon + bow
    m.fill(ring(8, 8, 4.85, 4.3, 11.9, 13.0), velvet("c8283a"))
    m.paint(ring(8, 8, 4.9, 4.3, 12.35, 12.55), velvet("e85d6c"))
    bow(m, (12.95, 12.45, 8.0), 1.3, 1.2, velvet("c8283a"), velvet("9e1d2c"), axis="x")
    m.fill(tube([(13.1, 12.2, 8.2), (13.4, 10.9, 8.6), (13.5, 10.2, 9.0)], 0.28), velvet("b52233"))
    return m


@hat("miner_lamp", "Miner Lamp", "COMMON")
def miner_lamp():
    m = hat_model("miner_lamp")
    Y = solid("f3c623", 0.6, soft=1)
    Yd = solid("c99312")
    m.fill(dome(8, 8, 5.0, 11.2, 4.6, 5.2) - box(3.5, 9, 3.5, 12.5, 12.5, 12.5), Y)
    m.fill(brim(8, 8, 6.0, 4.6, 11.0, 0.5, 0.35, 1.08), Y)
    m.fill(rolled_edge(8, 8, 5.85, 11.05, 0.3, 1.08), Yd)
    # ridges
    for x in (6.6, 9.4):
        m.fill(capsule((x, 15.4, 4.2), (x, 15.6, 11.8), 0.38) & dome(8, 8, 5.5, 11.2, 5.0, 5.7), Yd)
    m.fill(capsule((8, 15.9, 3.6), (8, 16.0, 12.4), 0.45) & dome(8, 8, 5.6, 11.2, 5.1, 5.8), Y)
    # lamp mount + lamp
    m.fill(rbox(6.2, 12.6, 2.4, 9.8, 15.0, 3.6, 0.35), solid("3a3a42"))
    m.fill(cyl_z(8, 13.8, 1.25, 1.2, 2.6), silver())
    m.fill(cyl_z(8, 13.8, 0.95, 1.0, 1.3), glow("fff1a8", 15, core="ffffff"))
    for dx in (-0.5, 0, 0.5):
        m.fill(box(8 + dx - 0.07, 12.85, 0.9, 8 + dx + 0.07, 14.75, 1.05), solid("2a2a2a"))
    m.fill(box(7.05, 13.73, 0.9, 8.95, 13.87, 1.05), solid("2a2a2a"))
    # cable to the back + side clips
    m.fill(tube([(8, 14.5, 3.6), (9.5, 16.2, 6), (12.4, 14.5, 10), (12.9, 11.5, 12.5)], 0.18), solid("262626"))
    for x in (3.0, 13.0):
        m.fill(rbox(x - 0.35, 10.9, 7.2, x + 0.35, 12.0, 8.8, 0.15), solid("2e2e34"))
    m.fill(box(3.0, 10.3, 7.6, 13.0, 10.6, 8.4) - box(3.4, 9, 3.4, 12.6, 12, 12.6), leather("4a3324"))
    return m


@hat("space_helmet", "Space Helmet", "LEGENDARY")
def space_helmet():
    m = hat_model("space_helmet")
    W = solid("e6e9ef", 0.5, soft=1)
    Wd = solid("b9bec9")
    shell = helmet_shell(2.4, 3.0, 2.4, 13.6, 14.6, 13.6, 1.6)
    m.fill(shell, W)
    # visor
    vis = rbox(3.0, 5.0, 1.0, 13.0, 11.6, 6.0, 1.2) & box(0, 0, 0, 16, 20, 3.0)
    m.carve(rbox(3.4, 5.4, 2.0, 12.6, 11.2, 4.0, 1.0))
    m.fill(rbox(3.0, 5.0, 2.35, 13.0, 11.6, 3.0, 1.0) - rbox(3.6, 5.6, 2.0, 12.4, 11.0, 3.4, 0.8), Wd)
    m.fill(rbox(3.5, 5.5, 2.75, 12.5, 11.1, 3.1, 0.9), glass("2b3a55"))
    m.paint(box(4.0, 9.6, 2.5, 6.0, 10.4, 3.2) | box(4.3, 9.0, 2.5, 4.8, 10.4, 3.2), flat("cfe6ff"))
    # top stripe + panel seams
    m.paint(box(7.2, 13.0, 2.0, 8.8, 15.5, 14.0), solid("d9363e", 0.4))
    m.paint(box(6.95, 13.0, 2.0, 7.2, 15.5, 14.0) | box(8.8, 13.0, 2.0, 9.05, 15.5, 14.0), solid("8d1f26"))
    for y in (6.0, 9.0):
        m.paint(box(2.0, y - 0.1, 6.5, 14.0, y + 0.1, 14.0), Wd)
    # side modules with lights
    for x0, x1 in ((1.6, 2.6), (13.4, 14.4)):
        m.fill(rbox(x0, 6.4, 6.4, x1, 10.4, 10.4, 0.4), solid("9aa1ae"))
        xx = x0 - 0.2 if x0 < 8 else x1 - 0.05
        m.fill(box(xx, 7.0, 7.4, xx + 0.25, 9.8, 7.9), glow("39c6ff", 13))
        m.fill(box(xx, 7.0, 8.4, xx + 0.25, 9.8, 8.9), glow("39c6ff", 13))
    # antenna
    m.fill(cyl(5.0, 10.5, 0.2, 14.0, 17.6), silver())
    m.fill(sphere(5.0, 17.8, 10.5, 0.45), glow("ff3b3b", 15))
    # neck ring
    m.fill(ring(8, 8, 6.1, 4.9, 2.6, 3.4), silver())
    m.paint(ring(8, 8, 6.2, 4.9, 2.9, 3.1), solid("6c7383"))
    return m


@hat("crystal_horns", "Crystal Horns", "EPIC")
def crystal_horns():
    m = hat_model("crystal_horns")
    plate = metal("3b3f52", brushed="z")
    m.fill(rbox(3.2, TOP - 0.1, 3.2, 12.8, 13.1, 12.8, 0.5), plate)
    m.fill(head_band(11.2, 12.6, 0.8, 0.3), plate)
    for p in square_points(4.85, 1.2, 11.9):
        m.fill(sphere(*p, 0.18), silver())
    crys = [crystal("9b6bff", glow=0), crystal("c39bff"), crystal("7a46e6")]

    def shard(base, ang_x, ang_z, h, r, mat):
        x, y, z = base
        top = (x + h * math.sin(math.radians(ang_z)), y + h * math.cos(math.radians(ang_z)) * math.cos(math.radians(ang_x)),
               z + h * math.sin(math.radians(ang_x)))
        m.fill(tube([base, top], r, r * 0.35), mat)
        m.fill(sphere(top[0], top[1], top[2], r * 0.45), glow("f0e4ff", 13))

    for sx in (-1, 1):
        bx = 8 + sx * 3.2
        m.fill(rbox(bx - 1.2, 13.0, 4.3, bx + 1.2, 13.6, 7.7, 0.3), silver())
        shard((bx, 13.3, 6.0), -10, sx * 18, 5.2, 0.85, crys[0])
        shard((bx + sx * 0.7, 13.3, 5.0), -25, sx * 38, 3.2, 0.55, crys[1])
        shard((bx - sx * 0.6, 13.3, 6.8), 18, sx * 5, 3.6, 0.6, crys[2])
        shard((bx + sx * 0.2, 13.3, 7.3), 30, sx * 30, 2.2, 0.42, crys[1])
    m.fill(sphere(8, 13.3, 4.5, 0.55), glow("b48cff", 14))
    return m


@hat("bunny_ears", "Bunny Ears", "COMMON")
def bunny_ears():
    m = hat_model("bunny_ears")
    band = solid("f2a7c4", 0.5)
    m.fill(rbox(3.0, 12.5, 7.4, 13.0, 13.1, 8.6, 0.25), band)
    for x0 in (3.0, 12.5):
        m.fill(rbox(x0, 9.4, 7.4, x0 + 0.5, 13.0, 8.6, 0.2), band)
    W = fur("f5f1f4")
    P = solid("f7a9c5", 0.4)
    # left ear upright
    m.fill(tube([(6.0, 12.8, 8.0), (5.6, 16.0, 8.0), (5.4, 19.2, 8.2), (5.6, 20.6, 8.3)], 1.55, 0.7) & box(0, 0, 7.1, 16, 30, 9.1), W)
    m.paint(tube([(6.0, 13.2, 7.2), (5.6, 16.0, 7.2), (5.45, 19.0, 7.3)], 0.85, 0.4) & box(0, 0, 6.8, 16, 30, 7.4), P)
    # right ear bent over
    m.fill(tube([(10.0, 12.8, 8.0), (10.5, 16.0, 8.0), (11.0, 18.3, 8.2)], 1.55, 1.25) & box(0, 0, 7.1, 16, 30, 9.1), W)
    m.fill(tube([(11.0, 18.3, 8.2), (12.4, 18.9, 8.2), (13.6, 18.0, 8.1)], 1.25, 0.65) & box(0, 0, 7.1, 16, 30, 9.1), W)
    m.paint(tube([(10.0, 13.2, 7.2), (10.5, 16.0, 7.2), (11.0, 18.0, 7.3)], 0.85, 0.7) & box(0, 0, 6.8, 16, 30, 7.4), P)
    m.fill(sphere(8, 12.75, 8.0, 0.55), solid("ffffff", 0.3))
    return m


# ------------------------------------------------------------- row 2

@hat("wizard_hat", "Wizard Hat", "RARE")
def wizard_hat():
    m = hat_model("wizard_hat")
    P = velvet("5a2aa8")
    Pd = velvet("3c1a78")
    G = gold()
    m.fill(brim(8, 8, 7.6, 3.9, 11.9, 0.55, 0.5), P)
    m.fill(rolled_edge(8, 8, 7.45, 11.55, 0.3), G)
    path = bezier((8, 12.0, 8), (8, 18.5, 8.3), (10.5, 22.5, 10.5), (12.8, 21.0, 12.5), n=16)
    m.fill(tube(path, 4.6, 0.35), P)
    # gold band with buckle
    m.paint(cyl(8, 8, 6, 12.6, 13.7), G)
    m.fill(rbox(7.0, 12.4, 3.0, 9.0, 14.0, 3.6, 0.2) - box(7.4, 12.8, 2.0, 8.6, 13.6, 4.0), solid("cfd3dc", 0.3))
    # stars and moons on the cloth
    import random
    rnd = random.Random(7)
    pts = path
    for k in range(26):
        i = rnd.randint(2, 11)
        a = rnd.uniform(0, 2 * math.pi)
        c = pts[i]
        t = i / 16
        r = 4.6 + (0.35 - 4.6) * t
        p = (c[0] + math.cos(a) * r, c[1] + rnd.uniform(-0.4, 0.4), c[2] + math.sin(a) * r)
        m.paint(sphere(*p, 0.36 if k % 3 else 0.5), G if k % 4 else solid("f5f0ff", 0.3))
    m.fill(prism(star_points(0, 0, 1.0, 0.42), "z", -0.2, 0.2).move(12.8, 21.0, 12.5), glow("ffd54a", 14))
    m.paint(cyl(8, 8, 6, 12.0, 12.6), Pd)
    return m


@hat("goggles", "Goggles", "COMMON")
def goggles():
    m = hat_model("goggles")
    L = leather("6b4429")
    m.fill(head_band(10.6, 12.0, 0.55, 0.3), L)
    stitch_line(m, (3.2, 10.85, 3.2), (12.8, 10.85, 3.2), solid("c9a77c", 0.2), 0.45)
    brass = gold(tones=["5a3a10", "8a5a1c", "b07a2a", "c9944a", "dfb36a", "f0d39a", "fff1d0"])
    for x in (6.0, 10.0):
        m.fill(cyl_z(x, 11.3, 1.55, 2.0, 3.0), brass)
        m.fill(torus(0, 0, 0, 1.35, 0.32).rot("x", 90, (0, 0, 0)).move(x, 11.3, 2.0), brass)
        m.fill(cyl_z(x, 11.3, 1.12, 1.7, 2.0), glass("5fd3c8"))
        m.paint(box(x - 0.8, 11.5, 1.6, x - 0.3, 12.1, 2.0), flat("e8fffb"))
        for a in range(0, 360, 90):
            rx, ry = math.cos(math.radians(a + 45)) * 1.45, math.sin(math.radians(a + 45)) * 1.45
            m.fill(sphere(x + rx, 11.3 + ry, 1.95, 0.17), silver())
    m.fill(rbox(7.4, 10.95, 2.4, 8.6, 11.65, 3.1, 0.2), brass)
    return m


@hat("sunflower_crown", "Sunflower Crown", "COMMON")
def sunflower_crown():
    m = hat_model("sunflower_crown")
    vine = solid("3f8f3a", 0.6, soft=1)
    m.fill(head_band(12.3, 13.1, 0.7, 0.4), vine)
    for k, p in enumerate(square_points(4.6, 2.3, 12.8)):
        leaf(m, p, 1.4, 0.45, k * 47.0, solid("4fae45", 0.5), 0.3)
    for k, p in enumerate(square_points(4.6, 4.6, 13.1)):
        x, y, z = p
        m.fill(cyl(x, z, 0.15, 12.6, 13.4), vine)
        for j in range(10):
            a = 2 * math.pi * j / 10
            m.fill(ellipsoid(x + math.cos(a) * 0.95, y + 0.1, z + math.sin(a) * 0.95, 0.5, 0.22, 0.5),
                   solid("ffc928" if j % 2 else "f5b316", 0.4))
        m.fill(dome(x, z, 0.75, y + 0.1, 0.4), stone("5a3418"))
        m.paint(sphere(x - 0.2, y + 0.45, z - 0.2, 0.15), solid("8a5a2a"))
    return m


@hat("neon_visor", "Neon Visor", "RARE")
def neon_visor():
    m = hat_model("neon_visor")
    B = metal("23252e", brushed="x")
    m.fill(head_band(7.6, 10.2, 0.55, 0.5) & box(0, 0, 0, 16, 20, 10.5), B)
    m.fill(rbox(3.6, 7.4, 2.4, 12.4, 10.4, 3.6, 0.6), B)
    m.fill(rbox(4.0, 8.0, 2.15, 12.0, 9.8, 2.6, 0.4), glow("ff4fd8", 15, core="ffd2f6"))
    m.paint(box(4.0, 8.75, 2.0, 12.0, 9.05, 2.7), glow("ffffff", 15))
    for x0 in (2.25, 13.25):
        m.fill(rbox(x0, 7.2, 6.4, x0 + 0.6, 10.6, 9.6, 0.25), metal("3a3d4a"))
        m.fill(box(x0 + (0.5 if x0 > 8 else -0.05), 7.8, 7.2, x0 + (0.65 if x0 > 8 else 0.1), 10.0, 7.5), glow("39e1ff", 14))
        m.fill(box(x0 + (0.5 if x0 > 8 else -0.05), 7.8, 8.4, x0 + (0.65 if x0 > 8 else 0.1), 10.0, 8.7), glow("39e1ff", 14))
    m.fill(box(3.2, 10.15, 7.2, 12.8, 10.5, 8.8) - box(3.45, 0, 0, 12.55, 12.55, 16), B)
    return m


@hat("tiny_ufo", "Tiny UFO", "EPIC")
def tiny_ufo():
    m = hat_model("tiny_ufo")
    S = silver()
    y = 15.0
    m.fill(ellipsoid(8, y, 8, 4.6, 0.9, 4.6), S)
    m.fill(ellipsoid(8, y - 0.6, 8, 3.0, 0.7, 3.0), metal("8a909c"))
    m.fill(torus(8, y, 8, 4.4, 0.35), metal("6d7380"))
    for k in range(10):
        a = 2 * math.pi * k / 10
        m.fill(sphere(8 + math.cos(a) * 4.0, y + 0.25, 8 + math.sin(a) * 4.0, 0.32),
               glow(["ff4f6d", "ffd54a", "4fe36b", "39c6ff"][k % 4], 15))
    m.fill(dome(8, 8, 2.4, y + 0.6, 2.3), glass("8fe3ff"))
    # pilot
    m.fill(sphere(8, y + 1.8, 8, 0.95), solid("6fdc5a", 0.4))
    for x in (7.6, 8.4):
        m.fill(ellipsoid(x, y + 1.95, 7.15, 0.25, 0.38, 0.15), solid("101418", 0.1))
    m.fill(cyl(8, 8, 0.12, y + 2.7, y + 3.4), silver())
    m.fill(sphere(8, y + 3.5, 8, 0.25), glow("ff4f6d", 15))
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.5
        m.fill(capsule((8 + math.cos(a) * 1.6, y - 0.8, 8 + math.sin(a) * 1.6), (8 + math.cos(a) * 2.4, TOP + 0.1, 8 + math.sin(a) * 2.4), 0.18),
               metal("8a909c"))
    m.fill(cyl(8, 8, 1.2, y - 1.4, y - 0.8), glow("9df7ff", 12))
    return m


@hat("ghost_buddy", "Ghost Buddy", "RARE")
def ghost_buddy():
    m = hat_model("ghost_buddy")
    W = solid("f3f5fb", 0.4, soft=1)
    m.fill(capsule((8, 14.6, 8.4), (8, 16.2, 8.4), 2.4), W)
    m.fill(cyl(8, 8.4, 2.4, 12.6, 14.6), W)
    for k in range(8):
        a = 2 * math.pi * k / 8
        m.fill(sphere(8 + math.cos(a) * 2.0, 12.75, 8.4 + math.sin(a) * 2.0, 0.55), W)
    m.carve(box(0, 0, 0, 16, 12.5, 16))
    # arms
    m.fill(ellipsoid(5.4, 14.3, 8.2, 0.7, 0.45, 0.6).rot("z", -30, (5.4, 14.3, 8.2)), W)
    m.fill(ellipsoid(10.6, 14.6, 8.2, 0.7, 0.45, 0.6).rot("z", 40, (10.6, 14.6, 8.2)), W)
    # face
    for x in (7.1, 8.9):
        m.fill(ellipsoid(x, 15.4, 6.05, 0.42, 0.62, 0.2), solid("15151c", 0.1))
        m.fill(sphere(x - 0.15, 15.65, 5.9, 0.13), flat("ffffff"))
    m.fill(ellipsoid(8, 14.4, 6.05, 0.4, 0.3, 0.2), solid("15151c", 0.1))
    for x in (6.3, 9.7):
        m.fill(ellipsoid(x, 14.75, 6.15, 0.45, 0.22, 0.15), solid("ffa6c0", 0.2))
    return m


@hat("top_hat", "Top Hat", "RARE")
def top_hat():
    m = hat_model("top_hat")
    K = velvet("23232b")
    m.fill(brim(8, 8, 6.6, 3.9, 12.3, 0.5, -0.0, 1.0), K)
    m.fill(rolled_edge(8, 8, 6.45, 12.5, 0.34), velvet("15151b"))
    # curled sides
    m.fill(torus(8, 13.0, 8, 6.2, 0.3) & box(0, 0, 6.5, 16, 20, 9.5), velvet("15151b"))
    m.fill(cone(8, 8, 4.3, 12.5, 7.2, r1=4.7), K)
    m.fill(dome(8, 8, 4.7, 19.6, 0.4), K)
    m.paint(cyl(8, 8, 6, 13.0, 14.6), velvet("b3122e"))
    m.paint(cyl(8, 8, 6, 13.0, 13.2) | cyl(8, 8, 6, 14.4, 14.6), velvet("7a0c22"))
    G = gold()
    m.fill(rbox(6.8, 12.8, 3.4, 9.2, 14.8, 3.95, 0.25) - box(7.3, 13.3, 3.0, 8.7, 14.3, 4.4), G)
    m.fill(box(7.95, 13.3, 3.45, 8.2, 14.3, 3.9), G)
    # shine stripe
    m.paint(box(5.3, 15.0, 0, 5.8, 19.0, 16) & cone(8, 8, 4.4, 12.5, 7.2, r1=4.8), velvet("3b3b48"))
    return m


@hat("beanie", "Beanie", "COMMON")
def beanie():
    m = hat_model("beanie")
    R = knit("c8213a")
    m.fill((cap_shell(10.6, 15.2, 0.85, 2.4) | dome(8, 8, 3.4, 14.4, 1.4)) - box(3.5, 9, 3.5, 12.5, 12.5, 12.5), R)
    m.fill(head_band(10.4, 12.6, 0.95, 0.6), knit("e04a5c"))
    for k in range(32):
        a = 2 * math.pi * k / 32
        if k % 2 == 0:
            m.paint(box(-0.13, 10, -7, 0.13, 13, 0).rot("y", math.degrees(a), (0, 0, 0)).move(8, 0, 8), knit("a01a30"))
    for y in (10.9, 11.5, 12.1):
        m.paint(head_band(y, y + 0.2, 1.0, 0.6), knit("b8182e"))
    m.fill(sphere(8, 16.4, 8, 1.35), fur("f4f4f8"))
    for k in range(10):
        a = 2 * math.pi * k / 10
        m.fill(sphere(8 + math.cos(a) * 1.2, 16.4 + math.sin(a * 2) * 0.6, 8 + math.sin(a) * 1.2, 0.5), fur("e8e8ef"))
    m.fill(rbox(9.6, 12.7, 3.05, 11.4, 13.9, 3.4, 0.2), fabric("2d2d36"))
    m.paint(box(9.9, 13.2, 2.9, 11.1, 13.4, 3.5), solid("ffd54a", 0.2))
    return m


# ------------------------------------------------------------- row 3

@hat("headphones", "Headphones", "RARE")
def headphones():
    m = hat_model("headphones")
    K = metal("262832", brushed="x")
    arch = torus(8, 9.0, 8, 5.0, 0.42, 0.1).rot("x", 90, (8, 9.0, 8)) & half("y", 9.0)
    m.fill(torus(0, 0, 0, 5.1, 0.45).rot("x", 90, (0, 0, 0)).move(8, 9.2, 8) & half("y", 9.2), K)
    m.fill(torus(0, 0, 0, 4.6, 0.32).rot("x", 90, (0, 0, 0)).move(8, 9.2, 8) & half("y", 9.2), leather("3a2f2a"))
    for sx in (-1, 1):
        x = 8 + sx * 5.0
        m.fill(cyl_x(8.6, 8, 2.1, x - 0.9, x + 0.9), K)
        m.fill(cyl_x(8.6, 8, 2.15, x - (0.95 if sx < 0 else -0.6), x + (0.6 if sx < 0 else 0.95)) - cyl_x(8.6, 8, 1.55, 0, 16), metal("44485a"))
        xo = x + sx * 0.9
        m.fill(torus(0, 0, 0, 1.4, 0.2).rot("z", 90, (0, 0, 0)).move(xo, 8.6, 8), glow("31d6ff", 15))
        m.fill(cyl_x(8.6, 8, 0.6, min(xo, xo + sx * 0.25), max(xo, xo + sx * 0.25)), glow("bdf6ff", 13))
        m.fill(cyl_x(8.6, 8, 1.9, x - sx * 0.9 - (0.5 if sx > 0 else 0), x - sx * 0.9 + (0.5 if sx < 0 else 0)), leather("1c1c22"))
    m.fill(capsule((3.2, 8.0, 6.4), (2.6, 6.5, 4.3), 0.25), K)
    m.fill(sphere(2.6, 6.4, 4.2, 0.45), metal("444"))
    return m


@hat("cat_ears", "Cat Ears", "COMMON")
def cat_ears():
    m = hat_model("cat_ears")
    band = metal("2a2a33")
    m.fill(rbox(3.1, 12.5, 7.6, 12.9, 12.9, 8.4, 0.18), band)
    for x0 in (3.1, 12.5):
        m.fill(rbox(x0, 9.4, 7.6, x0 + 0.4, 12.9, 8.4, 0.15), band)
    F = fur("2b2b33")
    for sx in (-1, 1):
        x = 8 + sx * 2.7
        ear(m, (x, 12.6, 8.0), 4.0, 2.1, 0.95, sx * 0.7, F, solid("f2a2bd", 0.4))
        m.paint(cone(x, 8.0, 2.2, 15.9, 0.9, r1=0.1, lean=(sx * 0.15, 0)), fur("f0f0f4"))
    m.fill(sphere(8, 12.95, 7.6, 0.45), gold())
    m.fill(sphere(8, 12.55, 7.4, 0.32), gold())
    return m


@hat("viking_helmet", "Viking Helmet", "EPIC")
def viking_helmet():
    m = hat_model("viking_helmet")
    St = metal("8d9db5", brushed="y")
    m.fill(dome(8, 8, 5.1, 10.4, 6.0) - box(3.5, 9, 3.5, 12.5, 12.5, 12.5), St)
    m.fill(head_band(9.9, 11.4, 1.35, 0.4), leather("6d4a2c"))
    for p in square_points(5.3, 1.3, 10.65):
        m.fill(sphere(*p, 0.24), gold())
    # cross straps
    m.fill(box(7.3, 10.5, 2.6, 8.7, 16.6, 13.4) & (dome(8, 8, 5.45, 10.4, 6.35) - dome(8, 8, 5.0, 10.4, 5.9)), leather("7a5232"))
    m.fill(box(2.6, 10.5, 7.3, 13.4, 16.6, 8.7) & (dome(8, 8, 5.45, 10.4, 6.35) - dome(8, 8, 5.0, 10.4, 5.9)), leather("7a5232"))
    for p in [(8, 16.4, 8)] + [(8, 13.5 + i * 0.0, 2.95) for i in range(1)]:
        m.fill(sphere(*p, 0.45), gold())
    m.fill(rbox(7.4, 7.0, 2.45, 8.6, 10.6, 3.0, 0.25), St)
    # horns
    I = solid("efe5cc", 0.5, soft=1)
    for sx in (-1, 1):
        pts = bezier((8 + sx * 4.6, 12.8, 8), (8 + sx * 7.6, 13.6, 8), (8 + sx * 8.6, 17.0, 7.4), (8 + sx * 7.6, 20.4, 6.4), n=14)
        horn(m, pts, 1.25, 0.25, I, solid("cbb98f", 0.3), 1.2)
        m.fill(cyl_x(12.8, 8, 1.45, min(8 + sx * 4.4, 8 + sx * 5.3), max(8 + sx * 4.4, 8 + sx * 5.3)), gold())
    return m


@hat("flower_crown", "Flower Crown", "COMMON")
def flower_crown():
    m = hat_model("flower_crown")
    m.fill(torus(8, 12.9, 8, 4.7, 0.45), solid("3f8a3a", 0.6, soft=1))
    for k in range(18):
        a = 2 * math.pi * k / 18
        p = (8 + math.cos(a) * 4.9, 12.95, 8 + math.sin(a) * 4.9)
        leaf(m, p, 1.2, 0.4, math.degrees(a) + 70, solid("5cb84f", 0.5), 0.25)
    cols = ["ff8fb8", "fff4f8", "ffd54a", "c39bff", "ff8fb8", "fff4f8"]
    for k in range(12):
        a = 2 * math.pi * k / 12 + 0.2
        p = (8 + math.cos(a) * 4.75, 13.35, 8 + math.sin(a) * 4.75)
        flower(m, p, cols[k % 6], 5, 0.95 if k % 2 else 0.75, "ffcf3a" if cols[k % 6] != "ffd54a" else "e0781c")
    return m


@hat("chef_hat", "Chef Hat", "COMMON")
def chef_hat():
    m = hat_model("chef_hat")
    W = fabric("f6f7fb")
    m.fill(cap_shell(10.6, 14.4, 0.85, 0.9), W)
    for k in range(-4, 5):
        for d in SIDES:
            m.paint(around(box(8 + k - 0.1, 10.5, 2.0, 8 + k + 0.1, 14.5, 4.0), d), fabric("d9dce6"))
    puffs = [(8, 16.6, 8, 3.3), (5.6, 15.9, 6.4, 2.3), (10.4, 15.9, 6.4, 2.3), (5.6, 15.9, 9.6, 2.3), (10.4, 15.9, 9.6, 2.3),
             (8, 16.2, 5.2, 2.2), (8, 16.2, 10.8, 2.2), (5.0, 16.1, 8, 2.2), (11.0, 16.1, 8, 2.2)]
    for x, y, z, r in puffs:
        m.fill(sphere(x, y, z, r), solid("fafbff", 0.5, soft=1.5))
    m.carve(box(-10, 0, -10, 30, 14.0, 30) - rbox(3.1, 0, 3.1, 12.9, 15, 12.9, 0.9))
    m.fill(head_band(14.0, 14.6, 1.05, 0.3), fabric("e9ebf2"))
    m.fill(rbox(6.9, 11.4, 2.85, 9.1, 13.0, 3.2, 0.3), gold())
    m.paint(box(7.2, 11.8, 2.8, 8.8, 12.6, 3.3), solid("b3122e", 0.3))
    return m


@hat("pirate_hat", "Pirate Hat", "EPIC")
def pirate_hat():
    m = hat_model("pirate_hat")
    K = velvet("1d1b22")
    m.fill(cap_shell(10.8, 15.6, 0.8, 2.2) | dome(8, 8, 3.8, 14.6, 2.0), K)
    m.carve(box(3.5, 9, 3.5, 12.5, 12.5, 12.5))
    y0 = 12.4

    def wall(X, Y, Z):
        R = 4.3 + (Y - y0) * 0.4
        d = tri_dist(X, Z, 8, 8.3, -90)
        return (Y >= y0) & (Y < 15.6) & (d <= R) & ((d > R - 0.5) | (Y < y0 + 0.45))
    m.fill(Shape(wall, ((-6, y0, -6), (22, 15.6, 22))), K)

    def trim(X, Y, Z):
        R = 4.3 + (Y - y0) * 0.4
        d = tri_dist(X, Z, 8, 8.3, -90)
        return (Y >= 15.15) & (Y < 15.65) & (d <= R + 0.1) & (d > R - 0.6)
    m.fill(Shape(trim, ((-6, 15, -6), (22, 15.7, 22))), gold())
    # skull and bones on the front wall
    W = solid("f1ede2", 0.3)
    zf = 8.3 - (4.3 + 1.4 * 0.4) - 0.15
    m.fill(sphere(8, 14.05, zf, 0.85) & box(0, 0, zf - 0.4, 16, 20, zf + 0.5), W)
    m.fill(box(7.45, 13.05, zf - 0.3, 8.55, 13.45, zf + 0.3), W)
    for x in (7.65, 8.35):
        m.paint(sphere(x, 14.15, zf - 0.35, 0.24), solid("121212", 0.1))
    for d in (35, -35):
        m.fill(capsule((8 - 1.5, 13.0, zf), (8 + 1.5, 13.0, zf), 0.18).rot("z", d, (8, 13.0, zf)), W)
    # plume
    for i in range(7):
        p = bezier((10.6, 15.2, 8.5), (12.8, 17.6, 9.5), (13.6, 16.0, 12.2), n=6)[i]
        m.fill(ellipsoid(p[0], p[1], p[2], 0.95 - 0.08 * i, 0.5, 0.95 - 0.08 * i), solid("d6263c" if i % 2 else "ea4258", 0.4))
    return m


@hat("propeller_cap", "Propeller Cap", "RARE")
def propeller_cap():
    m = hat_model("propeller_cap")
    cols = ["d9363e", "f4c623", "3fae49", "2f7bff"]
    cap = (cap_shell(10.6, 14.8, 0.8, 2.2) | dome(8, 8, 3.6, 14.0, 1.6)) - box(3.5, 9, 3.5, 12.5, 12.5, 12.5)

    def quad(X, Y, Z):
        return (((np.arctan2(Z - 8, X - 8) + math.pi) / (math.pi / 2)).astype(int)) % 4
    m.fill(cap, by(quad, *[fabric(c) for c in cols]))
    m.fill(ellipsoid(8, 10.85, 3.3, 4.6, 0.3, 3.4) & box(2, 10, -1, 14, 12, 3.3), fabric("1f5fd6"))
    m.fill(cyl(8, 8, 0.6, 15.4, 16.0), solid("f4c623"))
    m.fill(cyl(8, 8, 0.18, 15.8, 16.8), silver())
    for d, c in ((15, "d9363e"), (195, "2f7bff")):
        b = ellipsoid(10.6, 16.9, 8, 2.6, 0.18, 0.75).rot("x", 18, (10.6, 16.9, 8))
        m.fill(b.rot("y", d, (8, 0, 8)), solid(c, 0.4))
    m.fill(sphere(8, 16.95, 8, 0.4), solid("f4c623"))
    return m


@hat("party_hat", "Party Hat", "COMMON")
def party_hat():
    m = hat_model("party_hat")

    def pat(X, Y, Z):
        a = np.arctan2(Z - 8, X - 8)
        s = (np.floor(Y * 1.0 + a * 1.27) % 3).astype(int)
        return s
    m.fill(cone(8, 8, 3.2, TOP, 7.0, r1=0.3), by(pat, solid("ff6fb0"), solid("6fc8ff"), solid("fff3fa")))
    for k in range(14):
        a = k * 2.399
        h = 0.8 + (k % 7) * 0.85
        r = 3.2 + (0.3 - 3.2) * h / 7.0
        m.paint(sphere(8 + math.cos(a) * r, TOP + h, 8 + math.sin(a) * r, 0.33), solid(["ffd54a", "7cff6b", "c39bff"][k % 3], 0.3))
    m.fill(sphere(8, TOP + 7.2, 8, 0.85), fur("ffd54a"))
    m.fill(torus(8, TOP + 0.2, 8, 3.2, 0.3), fur("fff3fa"))
    return m


# ------------------------------------------------------------- row 4

@hat("angel_halo", "Angel Halo", "RARE")
def angel_halo():
    m = hat_model("angel_halo")
    y = 16.6
    m.fill(torus(8, y, 8, 3.7, 0.55), glow("ffd54a", 15, core="fff7c8"))
    m.fill(torus(8, y + 0.35, 8, 3.7, 0.25), glow("fff7c8", 15))
    for k in range(6):
        a = 2 * math.pi * k / 6 + 0.3
        x, z = 8 + math.cos(a) * 4.9, 8 + math.sin(a) * 4.9
        m.fill(prism(star_points(0, 0, 0.55, 0.2, 4, 45), "z", -0.12, 0.12).move(x, y + (0.8 if k % 2 else -0.4), z), glow("fffbe6", 15))
    return m


@hat("void_halo", "Void Halo", "EPIC")
def void_halo():
    m = hat_model("void_halo")
    y = 16.4
    m.fill(torus(8, y, 8, 4.0, 0.6), crystal("2a1745"))
    m.fill(torus(8, y, 8, 4.0, 0.3) & half("y", y + 0.25), glow("b15cff", 15))
    for k in range(10):
        a = 2 * math.pi * k / 10
        x, z = 8 + math.cos(a) * 4.0, 8 + math.sin(a) * 4.0
        m.fill(cone(x, z, 0.45, y + 0.3, 1.6 if k % 2 else 1.0, r1=0.05), crystal("5a2a9a"))
        m.fill(sphere(x, y + (1.9 if k % 2 else 1.3), z, 0.16), glow("e0b8ff", 15))
    for k in range(4):
        a = 2 * math.pi * k / 4 + 0.4
        x, z = 8 + math.cos(a) * 5.6, 8 + math.sin(a) * 5.6
        m.fill(prism([(0, -0.7), (0.35, 0), (0, 0.7), (-0.35, 0)], "z", z - 0.3, z + 0.3).move(x, y - 0.4, 0), glow("8a3cff", 14))
    return m


@hat("royal_crown", "Royal Crown", "LEGENDARY")
def royal_crown():
    m = hat_model("royal_crown")
    G = gold()
    # ermine trim

    def ermine(X, Y, Z):
        return ((hash3(np.floor(X * 1.3), np.floor(Y * 2), np.floor(Z * 1.3), 9) > 0.86)).astype(int)
    m.fill(head_band(10.6, 12.2, 1.25, 0.7), by(ermine, fur("f6f4f0"), solid("141418", 0.2)))
    m.fill(head_band(12.0, 14.0, 0.85, 0.35), G)
    m.fill(dome(8, 8, 4.2, 12.6, 4.2), velvet("a10f33"))
    # arches over the velvet
    for d in (0, 90):
        a = torus(0, 0, 0, 4.6, 0.38).rot("x", 90, (0, 0, 0)).move(8, 13.5, 8) & half("y", 13.5)
        m.fill(around(a, d), G)
        for k in range(1, 8):
            t = math.pi * k / 8
            p = (8 + math.cos(t) * 4.6, 13.5 + math.sin(t) * 4.6, 8)
            q = around(sphere(*p, 0.3), d)
            m.fill(q, pearl())
    # orb + cross
    m.fill(sphere(8, 18.6, 8, 0.9), G)
    m.paint(torus(8, 18.6, 8, 0.9, 0.15), gem("2f7bff", facet=0.3))
    m.fill(box(7.75, 19.3, 7.75, 8.25, 21.3, 8.25) | box(7.2, 20.2, 7.75, 8.8, 20.7, 8.25), G)
    # fleurs
    fl = prism([(-1.0, 0), (1.0, 0), (0.5, 1.2), (0.85, 2.2), (0.3, 2.0), (0, 3.0), (-0.3, 2.0), (-0.85, 2.2), (-0.5, 1.2)], "z", -0.25, 0.25)
    for d in SIDES:
        m.fill(around(fl.move(8, 13.9, 3.3), d), G)
        m.fill(around(fl.move(4.0, 13.9, 3.3).rot("y", -45, (4.0, 0, 3.3)), d), G)
        set_gem(m, (8, 12.95, 3.05), "-z", 0.55, ["c0102f", "1f7bff", "1fbf5f", "c0102f"][d // 90], G)
        for t in (-2.6, 2.6):
            m.fill(around(sphere(8 + t, 12.95, 3.0, 0.3), d), gem("e8f6ff", facet=0.25))
    return m


@hat("ice_crown", "Ice Crown", "EPIC")
def ice_crown():
    m = hat_model("ice_crown")
    ice = crystal("9fe6ff")
    m.fill(head_band(11.0, 13.2, 0.8, 0.35), crystal("6cc8f0"))
    m.fill(head_band(10.8, 11.3, 1.15, 0.3), solid("f4fbff", 0.6, soft=1))
    import random
    rnd = random.Random(3)
    for p in square_points(4.85, 0.95, 13.0):
        h = rnd.uniform(1.6, 4.4)
        lean = (rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6))
        m.fill(cone(p[0], p[2], rnd.uniform(0.45, 0.7), 12.8, h, r1=0.05, lean=lean), ice)
        if h > 3.5:
            m.fill(sphere(p[0] + lean[0], 12.8 + h, p[2] + lean[1], 0.2), glow("e9fbff", 12))
    for d in SIDES:
        m.fill(around(cone(8, 3.4, 0.95, 13.0, 5.6, r1=0.05), d), crystal("c9f3ff"))
        m.fill(around(sphere(8, 12.1, 3.0, 0.5), d), glow("5fd3ff", 13))
    return m


@hat("laurel_wreath", "Laurel Wreath", "RARE")
def laurel_wreath():
    m = hat_model("laurel_wreath")
    G = gold()
    m.fill(torus(8, 12.8, 8, 4.85, 0.22), G)
    for k in range(26):
        a = 2 * math.pi * k / 26 + math.pi / 2 + 0.1
        if abs(math.sin(a) + 1) < 0.08:
            continue
        p = (8 + math.cos(a) * 4.85, 12.8, 8 + math.sin(a) * 4.85)
        for side, dy in ((-1, 0.25), (1, -0.05)):
            tang = math.degrees(a) + 90
            leaf(m, p, 1.35, 0.42, tang + side * 35 - 180 * (k % 2 == 0) * 0, gold(seed=k), 0.35 + dy)
    m.fill(sphere(8, 12.8, 3.1, 0.55), gem("2fbf6a", facet=0.3))
    m.fill(torus(0, 0, 0, 0.6, 0.12).rot("x", 90, (0, 0, 0)).move(8, 12.8, 3.15), G)
    return m


@hat("captain_hat", "Captain Hat", "RARE")
def captain_hat():
    m = hat_model("captain_hat")
    W = fabric("f4f5f8")
    m.fill(rbox(2.6, 13.4, 2.4, 13.4, 15.2, 13.8, 1.2), W)
    m.fill(cap_shell(10.6, 13.6, 0.85, 0.6), fabric("1b1d26"))
    m.paint(box(0, 12.9, 0, 16, 13.6, 16), fabric("2a2d3a"))
    m.fill(ellipsoid(8, 10.7, 3.7, 4.4, 0.32, 3.2) & box(3, 10, -1, 13, 12, 3.8), solid("101116", 0.3, soft=1))
    G = gold()
    m.fill(tube([(4.6, 11.3, 3.0), (6.2, 11.8, 2.75), (9.8, 11.8, 2.75), (11.4, 11.3, 3.0)], 0.2), G)
    for x in (4.4, 11.6):
        m.fill(sphere(x, 11.3, 3.0, 0.35), G)
    # anchor badge
    m.fill(ellipsoid(8, 13.2, 3.0, 1.35, 1.0, 0.25), G)
    m.fill(capsule((8, 12.6, 2.75), (8, 13.85, 2.75), 0.12) | capsule((7.4, 12.75, 2.75), (8.6, 12.75, 2.75), 0.12), solid("1b1d26", 0.2))
    m.fill(capsule((7.6, 13.6, 2.75), (8.4, 13.6, 2.75), 0.1), solid("1b1d26", 0.2))
    for x in (6.4, 9.6):
        m.fill(ellipsoid(x, 13.2, 3.0, 0.7, 0.28, 0.2).rot("z", -25 if x < 8 else 25, (x, 13.2, 3.0)), G)
    return m


@hat("sou_wester", "Sou'wester", "COMMON")
def sou_wester():
    m = hat_model("sou_wester")
    Y = solid("f6c823", 0.5, soft=1.2)
    m.fill((cap_shell(10.8, 15.0, 0.85, 2.4) | dome(8, 8, 3.4, 14.2, 1.6)) - box(3.5, 9, 3.5, 12.5, 12.5, 12.5), Y)
    for k in range(6):
        a = 2 * math.pi * k / 6
        m.paint(box(-0.1, 10, -7, 0.1, 17, 0).rot("y", math.degrees(a), (0, 0, 0)).move(8, 0, 8), solid("d9a514"))
    m.fill(brim(8, 8.7, 7.2, 3.0, 10.9, 0.45, 1.3) - box(3.5, 0, 3.5, 12.5, 12.5, 12.5), Y)
    m.fill(rolled_edge(8, 8.7, 7.05, 9.85, 0.28), solid("d9a514"))
    m.fill(tube([(3.5, 10.6, 8.4), (3.6, 7.0, 7.6), (5.0, 3.5, 6.8), (8, 3.0, 6.6), (11.0, 3.5, 6.8), (12.4, 7.0, 7.6), (12.5, 10.6, 8.4)], 0.16), solid("2b2b33"))
    return m


@hat("diving_helmet", "Diving Helmet", "LEGENDARY")
def diving_helmet():
    m = hat_model("diving_helmet")
    Cu = gold(tones=["4a240e", "7a3e18", "a85a26", "c97a3a", "e09a58", "f2c08a", "fff0dc"])
    Br = gold(tones=["5a3a10", "8a5a1c", "b07a2a", "c9944a", "dfb36a", "f0d39a", "fff1d0"])
    m.fill(helmet_shell(2.2, 3.2, 2.2, 13.8, 14.6, 13.8, 3.2), Cu)
    m.carve(half("y", 3.2, above=False))
    for y in (6.0, 11.0):
        m.paint(box(0, y - 0.12, 0, 16, y + 0.12, 16) - box(0, 0, 0, 16, 20, 3.0), Cu)
    m.fill(ring(8, 8, 6.4, 4.6, 2.2, 3.6), Br)
    for k in range(8):
        a = 2 * math.pi * k / 8
        m.fill(sphere(8 + math.cos(a) * 5.6, 3.6, 8 + math.sin(a) * 5.6, 0.38), silver())
    # portholes: front big, sides small
    def port(c, r, axis):
        x, y, z = c
        if axis == "z":
            m.carve(cyl_z(x, y, r, z - 1, z + 1.5))
            m.fill(torus(0, 0, 0, r + 0.25, 0.42).rot("x", 90, (0, 0, 0)).move(x, y, z), Br)
            m.fill(cyl_z(x, y, r, z + 0.4, z + 0.8), glass("4fb8c8"))
            m.fill(box(x - r, y - 0.13, z + 0.15, x + r, y + 0.13, z + 0.45) | box(x - 0.13, y - r, z + 0.15, x + 0.13, y + r, z + 0.45), Br)
            for a in range(0, 360, 60):
                m.fill(sphere(x + math.cos(math.radians(a)) * (r + 0.3), y + math.sin(math.radians(a)) * (r + 0.3), z - 0.3, 0.2), silver())
        else:
            sg = 1 if x > 8 else -1
            m.carve(cyl_x(y, z, r, min(x, x - sg * 1.5), max(x, x - sg * 1.5)))
            m.fill(torus(0, 0, 0, r + 0.25, 0.38).rot("z", 90, (0, 0, 0)).move(x, y, z), Br)
            m.fill(cyl_x(y, z, r, min(x - sg * 0.8, x - sg * 0.4), max(x - sg * 0.8, x - sg * 0.4)), glass("4fb8c8"))
            m.fill(box(x - 0.45, y - 0.12, z - r, x + 0.45, y + 0.12, z + r) & cyl_x(y, z, r, x - 1, x + 1), Br)
    port((8, 8.4, 2.0), 2.2, "z")
    port((14.0, 8.6, 8), 1.4, "x")
    port((2.0, 8.6, 8), 1.4, "x")
    m.fill(cyl(8, 8, 1.3, 14.4, 15.4), Br)
    m.fill(cyl(8, 8, 0.8, 15.4, 16.2), Cu)
    m.fill(capsule((10.6, 13.0, 12.4), (12.6, 12.2, 14.2), 0.7), Br)
    return m


# ------------------------------------------------------------- row 5

@hat("fish_hat", "Fish Hat", "RARE")
def fish_hat():
    m = hat_model("fish_hat")
    O = grad("ff9a3c", "ffd08a", "y", 12.5, 17.5)
    body = ellipsoid(8, 14.3, 8.6, 2.6, 2.1, 4.6)
    m.fill(body, O)
    m.paint(ellipsoid(8, 13.4, 8.6, 2.5, 1.2, 4.5) & half("y", 13.6, above=False), solid("fff1df", 0.4))
    # stripes
    for z in (6.6, 9.8):
        m.paint(box(0, 0, z - 0.45, 16, 20, z + 0.45), solid("f6f6f6", 0.3))
        m.paint(box(0, 0, z - 0.6, 16, 20, z - 0.45) | box(0, 0, z + 0.45, 16, 20, z + 0.6), solid("2a2a2a", 0.2))
    # tail
    m.fill(prism([(12.9, 14.3), (14.9, 16.1), (15.3, 14.9), (14.8, 14.3), (15.3, 13.7), (14.9, 12.5)], "x", 7.65, 8.35).move(0, 0, 0), solid("ff8a2a"))
    # (tail drawn in z/y: polygon coordinates are (z, y))
    m.fill(prism([(8.6, 16.2), (10.6, 17.6), (11.5, 16.4)], "x", 7.75, 8.25), solid("ff8a2a"))
    for sx in (-1, 1):
        m.fill(ellipsoid(8 + sx * 2.5, 13.6, 7.6, 0.25, 0.7, 1.1).rot("z", sx * 25, (8 + sx * 2.5, 13.6, 7.6)), solid("ff8a2a"))
        m.fill(sphere(8 + sx * 1.9, 14.9, 5.2, 0.55), solid("f8f8f8", 0.2))
        m.fill(sphere(8 + sx * 2.15, 14.95, 5.0, 0.32), solid("111111", 0.1))
        m.fill(sphere(8 + sx * 2.25, 15.1, 4.85, 0.1), flat("ffffff"))
    m.fill(ellipsoid(8, 13.7, 4.15, 0.9, 0.45, 0.35), solid("c4502a"))
    return m


@hat("drill_helmet", "Drill Helmet", "EPIC")
def drill_helmet():
    m = hat_model("drill_helmet")
    Y = solid("f3c623", 0.6, soft=1)
    m.fill(cap_shell(10.6, 14.6, 0.9, 1.8), Y)
    m.fill(ellipsoid(8, 10.8, 3.4, 4.8, 0.35, 3.0) & box(2, 10, -1, 14, 12, 3.4), solid("d9a514"))
    for p in square_points(4.9, 1.5, 11.2):
        m.fill(sphere(*p, 0.22), silver())
    m.paint(head_band(12.0, 12.6, 1.0, 0.4), stripes("1d1d22", "f3c623", 1.0, "x"))
    m.fill(rbox(5.6, 14.4, 5.6, 10.4, 15.6, 10.4, 0.4), metal("4a4f5c"))
    m.fill(cyl(8, 8, 1.7, 15.5, 16.2), silver())
    # drill bit with spiral
    m.fill(cone(8, 8, 1.6, 16.2, 5.6, r1=0.1), silver())

    def spiral(X, Y, Z):
        a = np.arctan2(Z - 8, X - 8)
        return (((a / (2 * math.pi) + (Y - 16.2) / 1.3) % 1.0) < 0.28).astype(int)
    m.paint(cone(8, 8, 1.75, 16.2, 5.6, r1=0.15), by(spiral, silver(), metal("6c7383", brushed="y")))
    for sx in (-1, 1):
        m.fill(rbox(8 + sx * 2.2 - 0.4, 14.6, 7.4, 8 + sx * 2.2 + 0.4, 15.4, 8.6, 0.15), metal("2e3038"))
    m.fill(cyl_z(8, 13.3, 0.8, 2.6, 3.2), glow("fff1a8", 14))
    return m


@hat("hard_hat", "Hard Hat", "COMMON")
def hard_hat():
    m = hat_model("hard_hat")
    O = solid("ff7a1f", 0.6, soft=1.2)
    m.fill(cap_shell(10.8, 15.2, 0.9, 2.6) | dome(8, 8, 3.6, 14.4, 1.6), O)
    m.carve(box(3.5, 9, 3.5, 12.5, 12.5, 12.5))
    m.fill(brim(8, 8, 6.9, 4.0, 10.8, 0.45, 0.25) - box(3.5, 0, 3.5, 12.5, 12.5, 12.5), solid("f26c12"))
    m.fill(ellipsoid(8, 10.95, 3.2, 4.4, 0.35, 2.8) & box(2, 10, -1, 14, 12, 3.2), solid("f26c12"))
    m.fill(capsule((8, 15.4, 3.4), (8, 15.6, 12.6), 0.55) & cap_shell(10.8, 16.2, 1.4, 2.8), solid("ffa04d"))
    for x in (6.0, 10.0):
        m.fill(capsule((x, 15.1, 3.6), (x, 15.3, 12.4), 0.3) & cap_shell(10.8, 16.0, 1.25, 2.7), solid("e05e10"))
    m.paint(head_band(12.6, 13.3, 1.0, 0.4), stripes("f4f4f4", "c9d1d8", 0.5, "x"))
    m.fill(rbox(6.6, 13.4, 2.85, 9.4, 14.6, 3.25, 0.25), solid("2a2a33"))
    m.paint(box(6.9, 13.7, 2.7, 9.1, 14.3, 3.4), solid("ffd54a", 0.3))
    return m


@hat("farmer_cap", "Farmer Cap", "COMMON")
def farmer_cap():
    m = hat_model("farmer_cap")
    R = fabric("c9213a")
    W = fabric("f2f2ee")
    m.fill(cap_shell(10.6, 14.9, 0.85, 2.4), W)
    m.paint(half("z", 6.2, above=True), by(lambda X, Y, Z: ((np.floor(X * 2) + np.floor(Y * 2) + np.floor(Z * 2)) % 2).astype(int),
                                           fabric("f2f2ee"), fabric("c9c9c2")))
    m.paint(box(0, 13.6, 0, 16, 20, 16), R)
    m.fill(ellipsoid(8, 10.8, 3.2, 4.9, 0.35, 3.6) & box(2, 10, -1, 14, 12, 3.3), R)
    m.paint(ellipsoid(8, 10.8, 3.2, 4.5, 0.6, 3.2) - ellipsoid(8, 10.8, 3.2, 4.2, 0.7, 2.9), fabric("8e1426"))
    m.fill(cyl(8, 8, 0.55, 15.0, 15.3), R)
    # patch with a wheat logo
    m.fill(rbox(5.9, 11.2, 3.0, 10.1, 13.5, 3.35, 0.3), fabric("f6e7b6"))
    for i in range(4):
        m.fill(ellipsoid(8, 11.9 + i * 0.4, 2.9, 0.22, 0.28, 0.12), solid("d49a1e"))
        for sx in (-1, 1):
            m.fill(ellipsoid(8 + sx * 0.35, 11.75 + i * 0.4, 2.9, 0.2, 0.22, 0.12), solid("e0aa2a"))
    m.fill(box(7.93, 11.4, 2.85, 8.07, 12.0, 2.95), solid("8a6a2a"))
    return m


@hat("sun_hat", "Sun Hat", "COMMON")
def sun_hat():
    m = hat_model("sun_hat")
    S = straw("f1deae")
    m.fill(brim(8, 8, 9.2, 4.0, 11.6, 0.5, 1.2), S)
    m.fill(rolled_edge(8, 8, 9.0, 10.55, 0.35), straw("dcc28a"))
    m.fill(cyl(8, 8, 4.6, 11.6, 14.0) - cyl(8, 8, 4.1, 11, 13.8), S)
    m.fill(dome(8, 8, 4.6, 13.9, 1.5), S)
    for r in (5.6, 6.6, 7.6, 8.5):
        m.paint(ring(8, 8, r + 0.12, r - 0.12, 9, 13), straw("d6bb7e"))
    m.fill(ring(8, 8, 4.85, 4.3, 11.8, 12.9), fabric("f39ab6"))
    for k, a in enumerate((200, 230, 255)):
        x, z = 8 + math.cos(math.radians(a)) * 5.0, 8 + math.sin(math.radians(a)) * 5.0
        flower(m, (x, 12.6, z), ["ff6fa0", "fff4f8", "ffc928"][k], 6, 0.95, "ffcf3a", axis="y")
        leaf(m, (x, 12.3, z), 1.2, 0.4, a + 50, solid("5cb84f", 0.5), 0.1)
    m.fill(tube([(4.2, 12.1, 9.8), (3.4, 10.8, 10.6), (3.0, 9.3, 11.2)], 0.3, 0.2), fabric("f39ab6"))
    m.fill(tube([(4.0, 12.1, 10.4), (3.6, 10.6, 11.6), (3.4, 9.0, 12.4)], 0.3, 0.2), fabric("f6b6cb"))
    return m


@hat("pumpkin_hat", "Pumpkin Hat", "EPIC")
def pumpkin_hat():
    m = hat_model("pumpkin_hat")

    def ribs(X, Y, Z):
        a = np.arctan2(Z - 8, X - 8)
        return ((np.cos(a * 8) > 0.55)).astype(int)
    shell = helmet_shell(2.6, 3.4, 2.6, 13.4, 14.4, 13.4, 2.0)
    m.fill(shell, by(ribs, solid("e8761c", 0.6, soft=1), solid("c95a12", 0.5)))
    m.carve(half("y", 3.4, above=False))
    # carved face (glowing)
    F = glow("ffb53a", 14, core="fff0a0")
    for sx in (-1, 1):
        tri = prism([(-1.4, -0.8), (1.4, -0.8), (0, 1.3)], "z", 2.4, 3.6).move(8 + sx * 2.3, 9.7, 0)
        m.carve(tri)
        m.fill(prism([(-1.4, -0.8), (1.4, -0.8), (0, 1.3)], "z", 2.9, 3.4).move(8 + sx * 2.3, 9.7, 0), F)
    nose = prism([(-0.6, -0.4), (0.6, -0.4), (0, 0.5)], "z", 2.4, 3.6).move(8, 7.9, 0)
    m.carve(nose)
    m.fill(prism([(-0.6, -0.4), (0.6, -0.4), (0, 0.5)], "z", 2.9, 3.4).move(8, 7.9, 0), F)
    mouth = prism([(-3.4, 0.6), (-2.4, -0.3), (-1.4, 0.2), (-0.5, -0.6), (0.5, -0.6), (1.4, 0.2), (2.4, -0.3), (3.4, 0.6),
                   (2.6, -1.4), (1.2, -1.8), (-1.2, -1.8), (-2.6, -1.4)], "z", 2.4, 3.6).move(8, 6.0, 0)
    m.carve(mouth)
    m.fill(prism([(-3.4, 0.6), (-2.4, -0.3), (-1.4, 0.2), (-0.5, -0.6), (0.5, -0.6), (1.4, 0.2), (2.4, -0.3), (3.4, 0.6),
                  (2.6, -1.4), (1.2, -1.8), (-1.2, -1.8), (-2.6, -1.4)], "z", 2.9, 3.4).move(8, 6.0, 0), F)
    m.fill(box(7.6, 4.0, 3.0, 8.4, 4.8, 3.6), solid("e8761c"))
    # stem + leaf + vine
    m.fill(tube([(8, 14.2, 8), (8.2, 15.6, 8.2), (8.9, 16.4, 8.6)], 0.7, 0.45), wood("5d7a2a"))
    leaf(m, (8.6, 14.6, 8.4), 2.4, 0.75, 30, solid("4f9a35", 0.5), 0.6)
    m.fill(tube([(7.6, 14.6, 7.8), (6.4, 15.2, 7.4), (5.8, 14.8, 6.4), (6.4, 14.5, 5.8)], 0.14), solid("4f9a35"))
    return m


@hat("mushroom_cap", "Mushroom Cap", "RARE")
def mushroom_cap():
    m = hat_model("mushroom_cap")
    R = velvet("d92b2b")
    m.fill(dome(8, 8, 6.6, 11.2, 5.2), R)
    m.carve(box(3.5, 9, 3.5, 12.5, 12.5, 12.5))
    m.carve(half("y", 11.6, above=False) - box(0, 0, 0, 16, 20, 16) | (half("y", 11.6, above=False) & ~box(3, 0, 3, 13, 20, 13) if False else half("y", -50, above=False)))
    m.fill(dome(8, 8, 6.4, 11.0, 0.6) - cap_shell(10, 13, 0.6, 0.4), solid("efe2c4", 0.5))
    for k in range(48):
        a = 2 * math.pi * k / 48
        m.paint(box(-0.1, 10.9, -7, 0.1, 11.4, 0).rot("y", math.degrees(a), (0, 0, 0)).move(8, 0, 8), solid("c9b48a"))
    import random
    rnd = random.Random(11)
    for k in range(15):
        a = rnd.uniform(0, 2 * math.pi)
        e = rnd.uniform(0.15, 1.2)
        x, z = 8 + math.cos(a) * 6.6 * math.cos(e), 8 + math.sin(a) * 6.6 * math.cos(e)
        y = 11.2 + 5.2 * math.sin(e)
        m.paint(sphere(x, y, z, rnd.uniform(0.6, 1.1)), solid("fbf6ee", 0.4))
    return m


@hat("fox_ears", "Fox Ears", "COMMON")
def fox_ears():
    m = hat_model("fox_ears")
    band = solid("8a4a22", 0.4)
    m.fill(rbox(3.1, 12.5, 7.6, 12.9, 12.9, 8.4, 0.18), band)
    for x0 in (3.1, 12.5):
        m.fill(rbox(x0, 9.4, 7.6, x0 + 0.4, 12.9, 8.4, 0.15), band)
    for sx in (-1, 1):
        x = 8 + sx * 2.8
        ear(m, (x, 12.6, 8.0), 4.4, 2.2, 1.0, sx * 0.9, fur("f07a26"), fur("fff1e4"))
        m.paint(cone(x, 8.0, 2.4, 16.0, 1.2, r1=0.1, lean=(sx * 0.25, 0)), fur("2a1d16"))
    return m


@hat("bear_ears", "Bear Ears", "COMMON")
def bear_ears():
    m = hat_model("bear_ears")
    band = solid("5a3a22", 0.4)
    m.fill(rbox(3.1, 12.5, 7.6, 12.9, 12.9, 8.4, 0.18), band)
    for x0 in (3.1, 12.5):
        m.fill(rbox(x0, 9.4, 7.6, x0 + 0.4, 12.9, 8.4, 0.15), band)
    for sx in (-1, 1):
        x = 8 + sx * 3.0
        m.fill(ellipsoid(x, 14.3, 8.0, 1.65, 1.65, 0.85), fur("8a5a34"))
        m.paint(ellipsoid(x, 14.2, 7.3, 1.0, 1.0, 0.4), fur("e9b9a0"))
    return m


@hat("frog_hat", "Frog Hat", "RARE")
def frog_hat():
    m = hat_model("frog_hat")
    G = solid("5fbf3c", 0.6, soft=1)
    m.fill(cap_shell(10.6, 15.0, 0.85, 2.6), G)
    m.paint(half("y", 11.4, above=False), solid("4aa32c"))
    for sx in (-1, 1):
        x = 8 + sx * 2.4
        m.fill(sphere(x, 15.3, 5.4, 1.35), G)
        m.fill(ellipsoid(x, 15.4, 4.35, 0.85, 0.95, 0.4), solid("f7f7f0", 0.3))
        m.fill(ellipsoid(x, 15.35, 4.0, 0.5, 0.62, 0.25), solid("111111", 0.1))
        m.fill(sphere(x - 0.18, 15.6, 3.85, 0.13), flat("ffffff"))
        m.fill(ellipsoid(8 + sx * 3.9, 12.6, 3.3, 0.7, 0.4, 0.2), solid("ff9fbf", 0.3))
    m.fill(tube([(6.0, 12.0, 3.15), (7.0, 11.6, 3.05), (9.0, 11.6, 3.05), (10.0, 12.0, 3.15)], 0.12), solid("2a6a1a"))
    for p in [(6.2, 14.9, 11.0), (10.4, 15.2, 9.6), (8.8, 15.4, 12.6), (5.0, 13.6, 12.2)]:
        m.paint(sphere(*p, 0.55), solid("3e9a28"))
    # little legs
    for sx in (-1, 1):
        m.fill(ellipsoid(8 + sx * 4.9, 11.6, 10.6, 0.6, 0.45, 1.3), G)
        for t in (-0.5, 0, 0.5):
            m.fill(sphere(8 + sx * 4.9 + t * 0.6, 11.3, 11.9, 0.28), solid("4aa32c"))
    return m


@hat("knight_helm", "Knight Helm", "LEGENDARY")
def knight_helm():
    m = hat_model("knight_helm")
    St = gold(tones=["3a404c", "5c6474", "848d9e", "a8b0bf", "c9cfda", "e4e8ef", "ffffff"])
    m.fill(helmet_shell(2.5, 3.2, 2.5, 13.5, 14.6, 13.5, 1.6), St)
    m.carve(half("y", 3.2, above=False))
    # crest ridge + face plate
    m.fill(rbox(7.4, 13.8, 2.3, 8.6, 15.2, 13.7, 0.5), St)
    for y in (8.6, 9.6):
        m.carve(box(4.0, y, 2.0, 12.0, y + 0.4, 3.2))
        m.fill(box(4.0, y, 3.0, 12.0, y + 0.4, 3.25), solid("101216", 0.1))
    for x in range(5, 12):
        if x == 8:
            continue
        m.carve(box(x + 0.3, 5.0, 2.0, x + 0.6, 7.6, 3.2))
        m.fill(box(x + 0.3, 5.0, 3.0, x + 0.6, 7.6, 3.25), solid("101216", 0.1))
    G = gold()
    m.fill(box(7.6, 4.2, 2.2, 8.4, 11.4, 2.6) | box(6.0, 9.95, 2.2, 10.0, 10.55, 2.6), G)
    m.paint(head_band(3.2, 3.8, 1.6, 0.4), G)
    for p in square_points(5.45, 1.4, 3.5):
        m.fill(sphere(*p, 0.22), G)
    # plume
    for i in range(9):
        p = bezier((8, 15.2, 9.5), (8, 18.8, 10.0), (8, 17.8, 14.5), n=8)[i]
        m.fill(ellipsoid(p[0], p[1], p[2], 0.55, 0.85 - i * 0.04, 0.85 - i * 0.04), velvet("c8283a" if i % 2 else "e0485a"))
    m.fill(cyl(8, 9.5, 0.45, 14.6, 15.6), G)
    return m


@hat("cowboy_hat", "Cowboy Hat", "RARE")
def cowboy_hat():
    m = hat_model("cowboy_hat")
    L = leather("8a5530")

    def brim_fn(X, Y, Z):
        d = np.sqrt((X - 8) ** 2 + ((Z - 8) / 1.12) ** 2)
        side = np.abs(X - 8) / np.maximum(d, 1e-6)
        yy = 11.6 + np.clip(d - 5.0, 0, None) ** 2 * 0.22 * side ** 2 - np.clip(d - 5.0, 0, None) * 0.35 * (1 - side ** 2)
        return (d <= 8.2) & (d > 3.2) & (Y >= yy) & (Y < yy + 0.5)
    m.fill(Shape(brim_fn, ((-1, 9, -2), (17, 17, 18))), L)
    m.fill(cap_shell(11.4, 15.8, 0.6, 1.6) | rbox(4.4, 11.4, 4.0, 11.6, 16.2, 12.0, 1.4), L)
    m.carve(box(3.5, 9, 3.5, 12.5, 12.5, 12.5))
    m.carve(capsule((8, 16.4, 4.8), (8, 16.4, 11.2), 0.9))
    m.paint(box(0, 12.0, 0, 16, 13.2, 16) & cap_shell(11.4, 14, 0.75, 1.6), leather("3e2616"))
    m.fill(rbox(7.0, 11.9, 3.0, 9.0, 13.3, 3.5, 0.35), silver())
    m.fill(prism(star_points(0, 0, 0.55, 0.22), "z", 2.85, 3.1).move(8, 12.6, 0), gold())
    for p in square_points(5.05, 1.6, 12.6):
        m.fill(sphere(*p, 0.18), silver())
    return m


@hat("witch_hat", "Witch Hat", "EPIC")
def witch_hat():
    m = hat_model("witch_hat")
    P = velvet("2e1f45")
    m.fill(brim(8, 8, 7.9, 3.9, 11.9, 0.5, 0.7), P)
    m.fill(rolled_edge(8, 8, 7.75, 11.25, 0.3), velvet("201532"))
    path = bezier((8, 12.0, 8), (7.6, 18.0, 8.4), (6.2, 21.5, 10.5), (3.6, 20.5, 12.6), n=16)
    m.fill(tube(path, 4.4, 0.3), P)
    for k in range(4):
        i = 3 + k * 3
        c = path[i]
        r = 4.4 + (0.3 - 4.4) * i / 16
        m.paint(sphere(c[0], c[1], c[2], r + 0.2) - sphere(c[0], c[1], c[2], r - 0.3), velvet("3d2a5c"))
    m.paint(cyl(8, 8, 6, 12.2, 13.5), velvet("2fae6a"))
    m.fill(rbox(6.9, 12.0, 3.2, 9.1, 13.7, 3.8, 0.25) - box(7.35, 12.45, 3.0, 8.65, 13.25, 4.2), gold())
    for p in [(5.2, 14.6, 5.8), (9.8, 16.4, 6.0), (6.6, 18.2, 7.8)]:
        m.paint(sphere(*p, 0.3), glow("b6ff6a", 13))
    m.fill(sphere(3.4, 20.3, 12.8, 0.45), glow("b6ff6a", 15))
    return m


@hat("graduation_cap", "Graduation Cap", "RARE")
def graduation_cap():
    m = hat_model("graduation_cap")
    K = fabric("1e1f26")
    m.fill(cap_shell(10.8, 13.4, 0.85, 0.8), K)
    board = box(1.4, 13.4, 1.4, 14.6, 13.95, 14.6).rot("y", 45, (8, 0, 8))
    m.fill(board, fabric("16171d"))
    m.paint(board & box(-10, 13.8, -10, 30, 14, 30) - box(2.0, 0, 2.0, 14.0, 20, 14.0).rot("y", 45, (8, 0, 8)), gold())
    m.fill(cyl(8, 8, 0.6, 13.95, 14.35), gold())
    m.fill(tube([(8, 14.2, 8), (10.4, 14.15, 5.6), (12.6, 13.9, 3.4), (13.2, 12.4, 3.0), (13.2, 11.0, 3.0)], 0.13), gold())
    m.fill(cone(13.2, 3.0, 0.2, 9.2, 1.9, r1=0.55), gold())
    m.fill(sphere(13.2, 11.1, 3.0, 0.35), gold())
    m.paint(box(0, 13.0, 0, 16, 13.4, 16) & cap_shell(10.8, 13.4, 0.9, 0.8), fabric("2b2c35"))
    return m


@hat("traffic_cone", "Traffic Cone", "COMMON")
def traffic_cone():
    m = hat_model("traffic_cone")
    O = solid("ff6a1a", 0.6, soft=1)
    m.fill(rbox(2.8, TOP, 2.8, 13.2, 13.2, 13.2, 0.4), solid("1d1d22"))
    m.fill(cone(8, 8, 3.9, 13.2, 7.4, r1=0.85), O)
    for y0, y1 in ((14.6, 15.8), (17.0, 17.9)):
        m.paint(box(0, y0, 0, 16, y1, 16), solid("f4f4f4", 0.4))
    m.carve(cyl(8, 8, 0.6, 19.6, 21))
    m.paint(cone(8, 8, 4.0, 13.2, 7.4, r1=0.95) & box(9.8, 13.6, 0, 10.2, 20, 16), solid("ffa060"))
    return m


@hat("winter_hat", "Winter Hat", "RARE")
def winter_hat():
    m = hat_model("winter_hat")
    B = knit("2f63c9")
    m.fill(cap_shell(9.8, 15.0, 0.9, 2.6) | dome(8, 8, 3.4, 14.2, 1.6), B)
    m.carve(box(3.5, 9, 3.5, 12.5, 12.5, 12.5))
    # pattern bands
    m.paint(box(0, 11.0, 0, 16, 12.4, 16), knit("f4f6fb"))
    for k in range(-4, 5):
        for d in SIDES:
            if k % 2 == 0:
                m.paint(around(prism([(-0.4, 0), (0, 0.6), (0.4, 0), (0, -0.6)], "z", 2.0, 4.0).move(8 + k, 11.7, 0), d), knit("c8213a"))
    m.paint(box(0, 13.2, 0, 16, 13.6, 16), knit("f4f6fb"))
    # ear flaps with braids
    for sx in (-1, 1):
        x = 8 + sx * 4.75
        m.fill(rbox(x - 0.45, 6.6, 6.0, x + 0.45, 10.4, 10.0, 0.4), B)
        m.fill(tube([(x, 6.8, 8), (x, 4.6, 8.1), (x, 3.0, 8.0)], 0.35), knit("f4f6fb"))
        m.fill(sphere(x, 2.7, 8.0, 0.55), fur("f4f6fb"))
    m.fill(sphere(8, 16.5, 8, 1.4), fur("f4f6fb"))
    for k in range(8):
        a = 2 * math.pi * k / 8
        m.fill(sphere(8 + math.cos(a) * 1.25, 16.5 + math.sin(a * 2) * 0.5, 8 + math.sin(a) * 1.25, 0.55), fur("e4e8f2"))
    return m


@hat("coral_crown", "Coral Crown", "EPIC")
def coral_crown():
    m = hat_model("coral_crown")
    m.fill(head_band(11.6, 12.9, 0.9, 0.5), solid("2fb5a0", 0.6, soft=1))
    for p in square_points(4.9, 0.8, 12.25):
        m.fill(sphere(*p, 0.25), solid("6fe3cf", 0.3))
    import random
    rnd = random.Random(5)
    cols = ["ff6f8f", "ff9a4a", "ffd54a", "ff5fa8", "c39bff"]
    for k, p in enumerate(square_points(4.9, 2.4, 12.8)):
        c = solid(cols[k % 5], 0.6, soft=1)
        x, y, z = p
        h = rnd.uniform(2.4, 4.4)
        m.fill(tube([(x, y, z), (x + rnd.uniform(-0.4, 0.4), y + h * 0.5, z), (x + rnd.uniform(-0.8, 0.8), y + h, z + rnd.uniform(-0.5, 0.5))], 0.42, 0.25), c)
        for j in range(2):
            bx = x + rnd.choice((-1, 1)) * rnd.uniform(0.6, 1.3)
            by_ = y + h * rnd.uniform(0.35, 0.6)
            m.fill(tube([(x, by_ - 0.6, z), (bx, by_ + 0.4, z), (bx, by_ + 1.4, z)], 0.3, 0.18), c)
    for p in [(8, 12.4, 2.95), (3.0, 12.3, 9.6), (13.0, 12.3, 6.2)]:
        m.fill(ellipsoid(p[0], p[1], p[2], 0.75, 0.6, 0.35) if p[2] < 4 else ellipsoid(p[0], p[1], p[2], 0.35, 0.6, 0.75), solid("fbe6d6", 0.4))
    m.fill(sphere(8, 12.45, 2.7, 0.3), solid("f8f8ff", 0.2))
    return m


@hat("gem_tiara", "Gem Tiara", "LEGENDARY")
def gem_tiara():
    m = hat_model("gem_tiara")
    S = silver()
    m.fill(torus(0, 0, 0, 5.0, 0.28).rot("x", 90, (0, 0, 0)).move(8, 9.6, 8) & half("y", 9.6) & half("z", 8.5, above=False), S)
    front = prism([(-4.4, 0), (4.4, 0), (3.6, 1.4), (2.0, 1.8), (0.9, 3.4), (0, 4.0), (-0.9, 3.4), (-2.0, 1.8), (-3.6, 1.4)], "z", 3.0, 3.4)
    m.fill(front.move(8, 12.4, 0), S)
    # filigree holes
    for x, y in ((5.6, 13.4), (10.4, 13.4), (7.0, 14.4), (9.0, 14.4)):
        m.carve(cyl_z(x, y, 0.35, 2.9, 3.5))
    set_gem(m, (8, 14.9, 2.95), "-z", 0.9, "a03cff", S, shape="diamond")
    for x in (5.2, 10.8):
        set_gem(m, (x, 13.0, 2.95), "-z", 0.45, "ff5fa8", S)
    for x in (6.6, 9.4):
        set_gem(m, (x, 13.9, 2.95), "-z", 0.35, "5fd3ff", S)
    for x in [4.2 + i * 0.85 for i in range(10)]:
        m.fill(sphere(x, 12.55, 2.95, 0.2), pearl())
    m.fill(sphere(8, 16.55, 3.2, 0.35), pearl())
    return m


@hat("snorkel_mask", "Snorkel Mask", "RARE")
def snorkel_mask():
    m = hat_model("snorkel_mask")
    Y = solid("f4c623", 0.5)
    m.fill(head_band(7.6, 8.8, 0.85, 0.4), solid("2a2a33"))
    m.fill(rbox(4.0, 6.4, 2.2, 12.0, 10.4, 3.6, 1.0), Y)
    m.carve(rbox(4.7, 7.0, 1.9, 11.3, 9.8, 3.0, 0.7))
    m.fill(rbox(4.7, 7.0, 2.7, 11.3, 9.8, 3.0, 0.7), glass("7fd9ff"))
    m.paint(box(5.0, 9.0, 2.5, 6.4, 9.5, 3.2), flat("e6fbff"))
    m.fill(box(7.8, 6.4, 2.2, 8.2, 10.4, 3.0), Y)
    O = solid("ff7a1f", 0.5)
    pts = [(12.4, 6.8, 3.4), (13.4, 6.0, 4.8), (13.6, 9.0, 5.6), (13.6, 14.0, 6.0), (13.4, 16.4, 6.0)]
    m.fill(tube(pts, 0.55), O)
    for y in (10.0, 12.0, 14.0):
        m.paint(box(13, y, 5, 14.5, y + 0.8, 7), solid("f4f4f4", 0.3))
    m.fill(cyl(13.4, 6.0, 0.75, 16.2, 16.8), solid("2a2a33"))
    m.fill(rbox(11.8, 5.8, 2.6, 13.2, 7.2, 3.8, 0.4), O)
    return m


@hat("antenna_band", "Antenna Band", "COMMON")
def antenna_band():
    m = hat_model("antenna_band")
    K = metal("2a2c36")
    m.fill(rbox(3.1, 12.5, 7.4, 12.9, 13.0, 8.6, 0.2), K)
    for x0 in (3.0, 12.5):
        m.fill(rbox(x0, 9.4, 7.4, x0 + 0.5, 13.0, 8.6, 0.2), K)
    for sx in (-1, 1):
        x = 8 + sx * 2.3
        m.fill(cyl(x, 8.0, 0.55, 12.9, 13.5), K)
        pts = [(x + sx * 0.4 * math.sin(i * 1.7), 13.4 + i * 0.4, 8.0 + 0.4 * math.cos(i * 1.7)) for i in range(10)]
        m.fill(tube(pts, 0.13), silver())
        top = pts[-1]
        m.fill(sphere(top[0], top[1] + 0.6, top[2], 0.75), glow("6dff8a", 15, core="e4ffe9"))
        m.fill(torus(top[0], top[1] + 0.6, top[2], 0.75, 0.12), glow("2fcf55", 12))
    return m


@hat("welding_mask", "Welding Mask", "RARE")
def welding_mask():
    m = hat_model("welding_mask")
    St = metal("5a5f6c", brushed="x")
    m.fill(head_band(10.8, 12.0, 0.9, 0.4), solid("2a2a33"))
    for sx in (-1, 1):
        m.fill(cyl_x(11.4, 8.0, 0.65, 8 + sx * 4.6 - 0.3, 8 + sx * 4.6 + 0.3), silver())
    mask = rbox(3.6, 12.6, 1.4, 12.4, 15.0, 9.6, 1.0) - rbox(4.2, 12.0, 2.0, 11.8, 14.4, 10.2, 0.6)
    m.fill(mask, St)
    m.fill(rbox(5.4, 14.6, 2.6, 10.6, 15.3, 4.8, 0.3), solid("1a1c22"))
    m.fill(rbox(5.6, 15.0, 2.8, 10.4, 15.35, 4.6, 0.25), glass("2a4a3a"))
    m.paint(box(5.8, 15.2, 2.9, 6.6, 15.5, 4.4), flat("8fd0a0"))
    m.paint(box(3.0, 12.6, 1.0, 13.0, 13.4, 3.0), stripes("f4c623", "1d1d22", 1.0, "x", 0.0, 0.5))
    return m


@hat("gear_crown", "Gear Crown", "EPIC")
def gear_crown():
    m = hat_model("gear_crown")
    Br = gold(tones=["4a2a10", "7a4a1c", "a8702c", "c48a3a", "dcaa5a", "f0cc8a", "fff0d0"])
    m.fill(head_band(11.4, 13.0, 0.9, 0.4), Br)

    def gear(cx, cy, cz, R, teeth, d, axis_rot):
        g = None
        for k in range(teeth):
            a = 2 * math.pi * k / teeth
            t = box(-0.35, R - 0.2, -d, 0.35, R + 0.6, d).rot("z", math.degrees(a), (0, 0, 0))
            g = t if g is None else g | t
        g = g | cyl_z(0, 0, R, -d, d)
        g = g - cyl_z(0, 0, R * 0.42, -1, 1)
        return g.rot("y", axis_rot, (0, 0, 0)).move(cx, cy, cz)
    for d in SIDES:
        m.fill(around(gear(8, 14.2, 3.4, 1.7, 9, 0.3, 0), d), Br)
        m.fill(around(gear(5.0, 13.6, 3.35, 1.05, 7, 0.25, 0), d), metal("8a909c"))
        m.fill(around(gear(11.0, 13.6, 3.35, 1.05, 7, 0.25, 0), d), metal("8a909c"))
        m.fill(around(cyl_z(8, 14.2, 0.55, 2.9, 3.9), d), glow("31d6ff", 14))
    for p in square_points(4.9, 1.0, 11.6):
        m.fill(sphere(*p, 0.2), silver())
    return m
