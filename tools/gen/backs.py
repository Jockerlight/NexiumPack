"""The 36 back items in HD. Body space: torso x 4..12, y 2..14, z 6..10,
the back is the z = 6 side, items live at z < 5.7 (the skin's jacket layer
reaches 5.75). The player's left is +x."""
import math

import numpy as np

from hd import (Model, Shape, box, rbox, ellipsoid, sphere, cyl, cyl_x, cyl_z, ring, torus, cone, dome, capsule,
                tube, bezier, prism, half, solid, flat, gold, silver, gem, velvet, fabric, knit, fur, wood, leather,
                straw, stone, glow, glass, metal, crystal, grad, stripes, checker, by, C, tone, mix, hash3, Mat,
                rose_gold)
from wings import (back_model, wing_pair, feather_wing, membrane_wing, insect_wing, blade_wing, shard_wing, leaf_wing,
                   outline, ROOT_Y, ROOT_Z)
from parts import rivets, stitch_line, set_gem, bow, flower, leaf, star_points, pearl

BACKS = []


def back(id, name, rarity):
    def deco(fn):
        BACKS.append((id, name, rarity, fn))
        return fn
    return deco


BRASS = ["5a3a10", "8a5a1c", "b07a2a", "c9944a", "dfb36a", "f0d39a", "fff1d0"]


def mount(m, mat, gemc=None, y=ROOT_Y):
    m.fill(rbox(6.6, y - 2.2, 3.9, 9.4, y + 1.4, 5.6, 0.6), mat)
    if gemc:
        set_gem(m, (8, y - 0.4, 3.85), "-z", 0.6, gemc, gold())


def straps(m, mat, x0=4.6, x1=11.4, y0=2.6, y1=14.2):
    """Shoulder straps running down the back and over the shoulders."""
    for x in (x0, x1 - 0.9):
        m.fill(box(x, y0, 5.35, x + 0.9, y1, 5.7), mat)
        m.fill(box(x, y1 - 0.4, 5.35, x + 0.9, y1, 10.4), mat)


def flame(m, x, y, z, s=1.0, cols=("fff3b0", "ffb12e", "ff5a1e")):
    m.fill(cone(x, z, 0.55 * s, y - 2.2 * s, 2.2 * s, r1=0.0) .move(0, 0, 0) & half("y", y - 2.2 * s), glow(cols[2], 14))
    m.fill(cone(x, z, 0.38 * s, y - 1.6 * s, 1.6 * s, r1=0.0), glow(cols[1], 15))
    m.fill(cone(x, z, 0.22 * s, y - 1.0 * s, 1.0 * s, r1=0.0), glow(cols[0], 15))


# ------------------------------------------------------------- wings

@back("crystal_wings", "Crystal Wings", "LEGENDARY")
def crystal_wings():
    m = back_model("crystal_wings")
    wing_pair(m, lambda p, r: shard_wing(p, r, n=8, L0=5.5, L1=14.0, colour="7fd3ff", core="f0ffff"), 22.5, outline_col="14304a")
    mount(m, crystal("bfe9ff"), "5fd3ff")
    return m


@back("bee_wings", "Bee Wings", "RARE")
def bee_wings():
    m = back_model("bee_wings")
    wing_pair(m, lambda p, r: insect_wing(p, r, 11, 11, "c6d4e6", "6f7c92", "4f5a6e", glassy=True), 22.5, outline_col="242833")
    m.fill(ellipsoid(8, ROOT_Y - 0.6, 4.6, 1.5, 2.2, 1.0), stripes("f2c418", "1c1c22", 1.1, "y"))
    for x in (7.3, 8.7):
        m.fill(capsule((x, ROOT_Y + 1.4, 4.4), (x + (x - 8) * 1.5, ROOT_Y + 3.0, 4.0), 0.14), solid("1c1c22"))
        m.fill(sphere(x + (x - 8) * 1.5, ROOT_Y + 3.0, 4.0, 0.3), solid("1c1c22"))
    return m


@back("angel_wings", "Angel Wings", "LEGENDARY")
def angel_wings():
    m = back_model("angel_wings")
    wing_pair(m, lambda p, r: feather_wing(p, r, 15, 15, "f4f6fa", "e6ebf3", "ffffff", "c9d0de", "9aa4b8", "f4f6fa",
                                         n=12, acc=gold()), 22.5, outline_col="1d2233")
    mount(m, gold(), "fff3b8")
    return m


@back("bat_wings", "Bat Wings", "EPIC")
def bat_wings():
    m = back_model("bat_wings")
    wing_pair(m, lambda p, r: membrane_wing(p, r, 15, 15, "3a2a4a", "5a4473", "251a32", "e6dfd0", 4), 22.5, outline_col="120c18")
    mount(m, solid("251a32"))
    return m


@back("butterfly_wings", "Butterfly Wings", "EPIC")
def butterfly_wings():
    m = back_model("butterfly_wings")

    def draw(p, r):
        pat = grad("ff8a1e", "ffc04a", "x", r[0], r[0] + 12)
        insect_wing(p, r, 12, 13, "f08a1e", "1c1c22", "1c1c22",
                    spots=((9.5, 5.0, 0.5), (11.0, 3.4, 0.45), (10.5, 1.4, 0.4), (6.0, -6.0, 0.45), (8.0, -4.6, 0.4)),
                    pattern=pat)
        for x, y in ((3.5, 3.0), (5.0, -2.5)):
            p.paint(ellipsoid(r[0] + x, r[1] + y, r[2] - 0.6, 1.0, 0.7, 2), solid("1c1c22", 0.2))
    wing_pair(m, draw, 22.5, outline_col="100c10")
    m.fill(ellipsoid(8, ROOT_Y - 0.8, 4.7, 0.8, 3.0, 0.8), solid("2a2228"))
    return m


@back("dragon_wings", "Dragon Wings", "MYTHIC")
def dragon_wings():
    m = back_model("dragon_wings")
    wing_pair(m, lambda p, r: membrane_wing(p, r, 17, 16, "2c7a35", "62c25a", "1d5222", "f2ead6", 4), 22.5, outline_col="0c1c0e")
    mount(m, solid("1d5222"))
    for i in range(4):
        m.fill(cone(8, 4.2, 0.6, ROOT_Y - 3 + i * 1.3, 1.2, r1=0.05, lean=(0, -0.6)), solid("e9dfc2", 0.3))
    return m


@back("phoenix_wings", "Phoenix Wings", "MYTHIC")
def phoenix_wings():
    m = back_model("phoenix_wings")

    def draw(p, r):
        feather_wing(p, r, 16, 15, "ffb02e", "ff5a1e", "ffd84a", "b8261e", "8a1a14", "ff8a2e", n=12,
                     cov_base="ffd24a", cov_tip="ff8a2e")
        for k in range(6):
            x = r[0] + 4 + k * 2.0
            y = r[1] - 3 - (k % 3) * 1.6
            p.paint(sphere(x, y, r[2] - 1.0, 0.35), glow("ffe27a", 15))
    wing_pair(m, draw, 22.5, outline_col="3a0c08")
    mount(m, gold(), "ff5a1e")
    return m


@back("mech_wings", "Mech Wings", "LEGENDARY")
def mech_wings():
    m = back_model("mech_wings")
    wing_pair(m, lambda p, r: blade_wing(p, r, 6, 7.5, 14.0, 2.0, "b8c0cc", "4a5160", "39d4ff"), 22.5, outline_col="11151c")
    m.fill(rbox(6.0, ROOT_Y - 3.6, 3.6, 10.0, ROOT_Y + 1.4, 5.6, 0.6), metal("4a5160"))
    m.fill(cyl_z(8, ROOT_Y - 1.1, 1.1, 3.3, 3.7), glow("39d4ff", 15, core="e0fbff"))
    rivets(m, [(6.5, ROOT_Y + 0.9, 3.55), (9.5, ROOT_Y + 0.9, 3.55), (6.5, ROOT_Y - 3.1, 3.55), (9.5, ROOT_Y - 3.1, 3.55)])
    return m


@back("frost_wings", "Frost Wings", "LEGENDARY")
def frost_wings():
    m = back_model("frost_wings")

    def draw(p, r):
        feather_wing(p, r, 15, 15, "dff6ff", "9fdcff", "ffffff", "5aa8d8", "3a86c0", "e9f9ff", n=12)
        for k in range(5):
            x = r[0] + 4 + k * 2.3
            y = r[1] - 3 - (k % 2) * 3.5
            p.paint(prism(star_points(0, 0, 0.75, 0.25, 6, 90), "z", r[2] - 1.4, r[2] - 0.9).move(x, y, 0), glow("f4fdff", 12))
    wing_pair(m, draw, 22.5, outline_col="0e2a40")
    mount(m, crystal("bfe9ff"), "9fe6ff")
    return m


@back("leaf_wings", "Leaf Wings", "RARE")
def leaf_wings():
    m = back_model("leaf_wings")
    wing_pair(m, lambda p, r: leaf_wing(p, r, 5, 7.0, 12.5), 22.5, outline_col="0f2410")
    m.fill(tube([(8, ROOT_Y - 3, 4.6), (8, ROOT_Y + 1.5, 4.6)], 0.8, 0.6), wood("6b4a2a"))
    return m


# ------------------------------------------------------------- capes

def cape(m, cloth, trim, lining=None, emblem=None, y0=1.6, y1=14.2, rod=None, folds=6):
    """Hanging cape with soft folds, trim at the edges and the bottom."""
    def fn(X, Y, Z):
        t = np.clip((y1 - Y) / (y1 - y0), 0, 1)
        half_w = 4.2 + 1.6 * t
        zf = 5.0 - 0.35 * np.sin((X - 8) * math.pi * folds / 10) * (0.3 + t) - t * 0.9
        return (np.abs(X - 8) <= half_w) & (Y >= y0) & (Y < y1) & (Z >= zf - 0.55) & (Z < zf)
    sh = Shape(fn, ((1, y0, 2), (15, y1, 5.6)))
    m.fill(sh, cloth)

    def edge(X, Y, Z):
        t = np.clip((y1 - Y) / (y1 - y0), 0, 1)
        half_w = 4.2 + 1.6 * t
        return (np.abs(X - 8) > half_w - 0.55) | (Y < y0 + 0.7)
    m.paint(sh & Shape(edge, sh.bbox), trim)
    if lining:
        m.paint(sh & half("z", 4.2, above=True) & Shape(lambda X, Y, Z: Z > 4.9, sh.bbox), lining)
    if rod:
        m.fill(cyl_x(y1 - 0.2, 5.0, 0.42, 3.0, 13.0), rod)
        for x in (3.0, 13.0):
            m.fill(sphere(x, y1 - 0.2, 5.0, 0.62), rod)
    return sh


@back("royal_cape", "Royal Cape", "LEGENDARY")
def royal_cape():
    m = back_model("royal_cape")
    cape(m, velvet("8c0f2e"), gold(), rod=gold())
    # ermine collar
    m.fill(rbox(3.0, 12.8, 4.2, 13.0, 14.6, 5.7, 0.6), by(lambda X, Y, Z: (hash3(np.floor(X * 1.4), np.floor(Y * 2), np.floor(Z), 9) > 0.86).astype(int),
                                                       fur("f6f4f0"), solid("141418", 0.2)))
    # crest: crown + lion-ish shield
    m.fill(prism([(-1.6, 1.6), (1.6, 1.6), (1.6, -0.4), (0, -2.0), (-1.6, -0.4)], "z", 3.6, 4.0).move(8, 7.6, 0), gold())
    m.fill(prism([(-1.2, 1.25), (1.2, 1.25), (1.2, -0.3), (0, -1.55), (-1.2, -0.3)], "z", 3.45, 3.7).move(8, 7.6, 0), velvet("1f3f9e"))
    m.fill(prism(star_points(0, 0, 0.8, 0.32), "z", 3.3, 3.5).move(8, 7.7, 0), gold())
    for x in (6.2, 8.0, 9.8):
        m.fill(cone(x, 3.8, 0.35, 9.6, 0.9, r1=0.05), gold())
    return m


@back("frost_cape", "Frost Cape", "EPIC")
def frost_cape():
    m = back_model("frost_cape")
    cape(m, grad("2f7fd6", "9fdcff", "y", 1.6, 14.2), solid("f4fbff", 0.4), rod=silver())
    for y in range(3, 13, 3):
        for x in (6.0, 10.0) if y % 2 else (8.0,):
            m.paint(prism(star_points(0, 0, 0.75, 0.28, 6, 90), "z", 2.0, 6.0).move(x, y, 0), glow("e9fbff", 11))
    for k in range(9):
        x = 3.0 + k * 1.25
        m.fill(cone(x, 4.4, 0.32, 0.4, 1.4, r1=0.04).move(0, 0, 0), crystal("bfe9ff"))
    m.fill(rbox(6.8, 13.0, 4.1, 9.2, 14.8, 4.7, 0.3), silver())
    m.fill(sphere(8, 13.9, 4.0, 0.5), glow("7fdcff", 14))
    return m


@back("cape_banner", "Cape Banner", "RARE")
def cape_banner():
    m = back_model("cape_banner")
    def fn(X, Y, Z):
        zf = 4.9 - 0.2 * np.sin(Y * 0.9)
        return (X >= 4.4) & (X < 11.6) & (Y >= 1.8) & (Y < 13.6) & (Z >= zf - 0.45) & (Z < zf)
    sh = Shape(fn, ((4, 1.8, 3.8), (12, 13.6, 5.2)))
    m.fill(sh, fabric("16233d"))
    m.paint(sh & (box(4.4, 1.8, 0, 5.0, 14, 9) | box(11.0, 1.8, 0, 11.6, 14, 9) | box(4, 1.8, 0, 12, 2.4, 9)), glow("39d4ff", 12))
    # zig-zag bottom
    for k in range(4):
        m.carve(prism([(0, 0), (0.9, 1.2), (1.8, 0)], "z", 3, 6).move(4.4 + k * 1.8, 1.79, 0))
    m.fill(cyl_x(13.8, 4.6, 0.38, 3.6, 12.4), silver())
    for x in (3.6, 12.4):
        m.fill(sphere(x, 13.8, 4.6, 0.55), silver())
    # emblem: diamond with an N
    m.fill(prism([(0, 2.0), (1.6, 0), (0, -2.0), (-1.6, 0)], "z", 3.95, 4.3).move(8, 8.6, 0), glow("39d4ff", 13))
    m.fill(prism([(0, 1.4), (1.05, 0), (0, -1.4), (-1.05, 0)], "z", 3.8, 4.0).move(8, 8.6, 0), fabric("16233d"))
    for y in (11.6, 5.4):
        m.paint(box(6.0, y, 0, 10.0, y + 0.25, 9) & sh, solid("8fb6d6", 0.3))
    return m


# ------------------------------------------------------------- packs

@back("compact_jetpack", "Compact Jetpack", "RARE")
def compact_jetpack():
    m = back_model("compact_jetpack")
    straps(m, solid("2a2c34"))
    m.fill(rbox(6.4, 6.4, 3.4, 9.6, 12.6, 5.6, 0.6), metal("5a606e"))
    for x in (5.4, 10.6):
        m.fill(cyl(x, 4.0, 1.45, 5.0, 12.4), silver())
        m.fill(dome(x, 4.0, 1.45, 12.4, 0.8), silver())
        for y in (6.0, 10.8):
            m.paint(cyl(x, 4.0, 1.6, y, y + 0.6), solid("ff7a1f", 0.3))
        m.fill(cone(x, 4.0, 0.9, 3.6, 1.4, r1=1.25), metal("3a3e48"))
        flame(m, x, 3.6, 4.0, 1.1)
    m.fill(rbox(7.0, 9.4, 3.2, 9.0, 11.6, 3.5, 0.2), metal("2e3038"))
    for y in (9.9, 10.5, 11.1):
        m.fill(box(7.3, y, 3.05, 8.7, y + 0.25, 3.25), glow("7cff6b" if y < 10 else "ffd54a" if y < 11 else "ff4f4f", 13))
    return m


@back("tool_backpack", "Tool Backpack", "COMMON")
def tool_backpack():
    m = back_model("tool_backpack")
    L = leather("8a5a34")
    straps(m, leather("5a3a22"))
    m.fill(rbox(4.8, 3.6, 2.6, 11.2, 12.4, 5.6, 0.9), L)
    m.fill(rbox(5.4, 4.2, 1.9, 10.6, 8.2, 2.9, 0.6), leather("7a4c2a"))
    m.fill(rbox(4.8, 10.6, 2.5, 11.2, 12.6, 5.7, 0.7), leather("6b4226"))
    for x in (6.6, 9.4):
        m.fill(box(x - 0.3, 8.2, 1.95, x + 0.3, 11.2, 2.6), leather("3e2616"))
        m.fill(rbox(x - 0.45, 8.4, 1.8, x + 0.45, 9.1, 2.1, 0.1), gold(tones=BRASS))
    stitch_line(m, (5.6, 4.6, 1.85), (10.4, 4.6, 1.85), solid("d8b88a", 0.2))
    # tools sticking out: hammer + wrench + pickaxe handle
    m.fill(cyl(6.2, 4.2, 0.28, 11.8, 16.0), wood("8a6a3a"))
    m.fill(rbox(5.0, 15.6, 3.6, 7.4, 16.6, 4.8, 0.2), metal("8a909c"))
    m.fill(capsule((9.6, 12.0, 4.2), (10.6, 16.2, 4.2), 0.3), silver())
    m.fill(torus(0, 0, 0, 0.55, 0.22).rot("x", 90, (0, 0, 0)).move(10.75, 16.6, 4.2) - box(10.4, 16.6, 3, 11.1, 17.5, 5.5), silver())
    return m


@back("fish_tank", "Fish Tank", "EPIC")
def fish_tank():
    m = back_model("fish_tank")
    straps(m, solid("2a2c34"))
    fr = metal("3a3e48")
    m.fill(rbox(4.4, 3.6, 1.6, 11.6, 12.8, 5.6, 0.3) - box(4.8, 4.0, 1.0, 11.2, 12.4, 5.2), fr)
    m.fill(box(4.8, 4.0, 1.95, 11.2, 11.2, 2.2), glass("4fb8e8"))
    m.fill(box(4.8, 11.2, 1.95, 11.2, 12.4, 2.2), glass("cfefff"))
    m.fill(box(4.8, 4.0, 2.2, 11.2, 11.2, 5.2), solid("1f6fb0", 0.6, soft=1))
    m.fill(box(4.8, 4.0, 2.2, 11.2, 4.8, 5.2), stone("c9b48a"))
    # fish seen through the glass (front plane)
    for (x, y, c, d) in ((6.6, 8.6, "ff8a2e", 1), (9.4, 6.2, "ffd54a", -1), (9.0, 9.8, "ff5fa8", -1)):
        m.fill(ellipsoid(x, y, 1.92, 0.9, 0.55, 0.1), solid(c, 0.3))
        m.fill(prism([(0, 0), (0.6 * d, 0.45), (0.6 * d, -0.45)], "z", 1.85, 1.95).move(x + 0.8 * d, y, 0), solid(c, 0.3))
        m.fill(sphere(x - 0.45 * d, y + 0.12, 1.85, 0.1), solid("101010"))
    for x in (5.6, 10.4):
        m.fill(tube([(x, 4.8, 3), (x + 0.4, 6.6, 3), (x - 0.2, 8.4, 3)], 0.22), solid("3fae49"))
        m.paint(tube([(x, 4.8, 1.9), (x + 0.4, 6.6, 1.9), (x - 0.2, 8.4, 1.9)], 0.22) & box(0, 0, 1.8, 16, 20, 2.0), solid("3fae49"))
    for k in range(5):
        m.paint(sphere(7.4 + (k % 2) * 0.4, 7.0 + k * 0.9, 1.95, 0.14), flat("e6fbff"))
    m.fill(rbox(6.8, 12.8, 3.0, 9.2, 13.6, 4.8, 0.3), fr)
    return m


@back("tractor_toolcase", "Tractor Toolcase", "RARE")
def tractor_toolcase():
    m = back_model("tractor_toolcase")
    straps(m, solid("2a2c34"))
    R = solid("c9213a", 0.5, soft=1)
    m.fill(rbox(4.6, 4.0, 2.2, 11.4, 11.6, 5.6, 0.5), R)
    m.fill(rbox(4.4, 9.4, 2.0, 11.6, 10.0, 5.7, 0.2), solid("8e1426"))
    m.paint(box(4, 5.0, 0, 12, 6.0, 9), stripes("f4c623", "1d1d22", 0.8, "x"))
    m.fill(capsule((6.4, 12.4, 3.9), (9.6, 12.4, 3.9), 0.3) | capsule((6.4, 11.4, 3.9), (6.4, 12.4, 3.9), 0.3) | capsule((9.6, 11.4, 3.9), (9.6, 12.4, 3.9), 0.3), metal("2e3038"))
    for x in (5.6, 10.4):
        m.fill(rbox(x - 0.5, 8.6, 1.8, x + 0.5, 9.8, 2.3, 0.15), silver())
    m.fill(rbox(6.8, 6.6, 1.95, 9.2, 8.4, 2.3, 0.2), solid("f4f4f4", 0.3))
    m.fill(cyl_z(8, 7.5, 0.6, 1.8, 2.0), solid("3fae49"))
    return m


@back("dragon_spines", "Dragon Spines", "EPIC")
def dragon_spines():
    m = back_model("dragon_spines")
    for i in range(6):
        y = 2.8 + i * 2.0
        h = 1.6 + 1.2 * math.sin(math.pi * (i + 0.5) / 6)
        m.fill(cone(8, 4.8, 0.95, y - 0.6, h + 0.6, r1=0.06, lean=(0, -h * 0.4), rz_scale=1.0).rot("x", -60, (8, y, 5.4)),
               crystal("7a46e6", seed=i))
        m.fill(sphere(8, y, 5.2, 0.8), solid("3c1a78", 0.5))
    m.fill(tube([(8, 2.4, 5.3), (8, 14.0, 5.3)], 0.55), solid("3c1a78", 0.5))
    for i in range(6):
        y = 2.8 + i * 2.0
        m.fill(sphere(8, y + 0.4, 3.4, 0.22), glow("c39bff", 13))
    return m


@back("energy_cell", "Energy Cell", "RARE")
def energy_cell():
    m = back_model("energy_cell")
    straps(m, solid("2a2c34"))
    m.fill(cyl(8, 3.8, 2.0, 4.6, 12.0), glass("8fe8ff"))
    m.fill(cyl(8, 3.8, 1.1, 4.6, 12.0), glow("39d4ff", 15, core="e8fdff"))
    for y0 in (3.6, 11.6):
        m.fill(cyl(8, 3.8, 2.35, y0, y0 + 1.1), metal("4a5160"))
        rivets(m, [(8 + 2.3 * math.cos(a), y0 + 0.55, 3.8 + 2.3 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 9)[:-1]], silver(), 0.18)
    for y in (6.6, 9.4):
        m.fill(torus(8, y, 3.8, 2.05, 0.2), metal("4a5160"))
    m.fill(tube([(6.2, 12.6, 3.8), (5.0, 13.4, 4.8), (4.8, 12.0, 5.4)], 0.18), solid("ff4f4f"))
    m.fill(tube([(9.8, 12.6, 3.8), (11.0, 13.4, 4.8), (11.2, 12.0, 5.4)], 0.18), solid("2a2a2a"))
    return m


@back("neon_battery", "Neon Battery", "RARE")
def neon_battery():
    m = back_model("neon_battery")
    straps(m, solid("1c1c22"))
    m.fill(rbox(5.0, 3.6, 2.4, 11.0, 12.0, 5.6, 0.9), metal("1f1d2a"))
    m.fill(rbox(7.0, 12.0, 3.2, 9.0, 12.8, 4.8, 0.3), silver())
    m.fill(rbox(5.6, 4.4, 2.15, 10.4, 11.2, 2.5, 0.5), glow("ff4fd8", 13, core="ffd2f6"))
    for k in range(4):
        y = 5.2 + k * 1.5
        m.fill(box(6.4, y, 1.95, 9.6, y + 1.0, 2.2), glow("ffe6fa" if k < 3 else "5a1a4a", 15 if k < 3 else 0) if k < 3 else solid("3a1030"))
    m.fill(prism([(0.4, 1.0), (-0.5, -0.1), (0.1, -0.1), (-0.4, -1.0), (0.6, 0.2), (0, 0.2)], "z", 1.8, 2.0).move(8, 10.4, 0), flat("ffffff"))
    for x in (5.0, 11.0):
        m.fill(box(x - 0.15, 4.4, 2.2, x + 0.15, 11.2, 5.6), glow("39e1ff", 12))
    return m


@back("hiking_bag", "Hiking Bag", "COMMON")
def hiking_bag():
    m = back_model("hiking_bag")
    G = fabric("4f7a32")
    straps(m, fabric("2f4a1e"))
    m.fill(rbox(4.8, 3.0, 2.4, 11.2, 12.4, 5.6, 1.0), G)
    m.fill(rbox(5.4, 3.6, 1.7, 10.6, 7.6, 2.8, 0.7), fabric("3f6a26"))
    m.fill(rbox(4.6, 10.2, 2.2, 11.4, 12.6, 5.7, 0.8), fabric("3a5f24"))
    for x in (4.3, 11.7):
        m.fill(rbox(x - 0.5, 4.0, 3.0, x + 0.5, 8.4, 5.2, 0.4), fabric("3f6a26"))
    m.fill(cyl_x(13.4, 4.2, 1.15, 4.4, 11.6), stripes("c9a46a", "a8834a", 0.6, "x"))
    for x in (5.4, 10.6):
        m.fill(cyl_x(13.4, 4.2, 1.25, x - 0.2, x + 0.2), leather("3e2616"))
    for x in (6.6, 9.4):
        m.fill(box(x - 0.3, 10.0, 2.05, x + 0.3, 12.6, 2.3), leather("3e2616"))
        m.fill(rbox(x - 0.45, 10.2, 1.9, x + 0.45, 10.9, 2.15, 0.1), silver())
    stitch_line(m, (5.8, 4.0, 1.65), (10.2, 4.0, 1.65), solid("c9d8b0", 0.2))
    m.fill(capsule((10.8, 5.0, 2.0), (11.2, 2.6, 2.4), 0.15), solid("ff7a1f"))
    return m


@back("quiver", "Quiver", "COMMON")
def quiver():
    m = back_model("quiver")
    L = leather("8a5530")
    axis_a, axis_b = (5.0, 3.0, 4.0), (11.0, 12.0, 4.0)
    m.fill(capsule(axis_a, axis_b, 1.35, 1.5), L)
    m.fill(tube([(4.2, 14.4, 5.4), (4.4, 13.0, 5.5), (12.2, 2.4, 5.5), (12.0, 1.6, 5.4)], 0.32), leather("5a3a22"))
    for t in (0.2, 0.75):
        p = [axis_a[k] + (axis_b[k] - axis_a[k]) * t for k in range(3)]
        m.paint(sphere(p[0], p[1], p[2], 1.65) - sphere(p[0], p[1], p[2], 1.3), gold(tones=BRASS))
    for k, (dx, dz) in enumerate(((-0.6, -0.3), (0.4, -0.4), (0.0, 0.5), (-0.5, 0.6))):
        a = (11.0 + dx, 12.0, 4.0 + dz)
        b = (12.4 + dx, 14.6, 4.0 + dz)
        m.fill(capsule(a, b, 0.12), wood("c9a46a"))
        m.fill(prism([(0, 0), (0.45, -0.9), (0, -0.6), (-0.45, -0.9)], "z", b[2] - 0.08, b[2] + 0.08).move(b[0], b[1] + 0.2, 0).rot("z", -28, (b[0], b[1], b[2])),
               solid(["f4f4f4", "d6263c", "f4f4f4", "2f7bff"][k], 0.3))
    return m


@back("shield_emblem", "Shield Emblem", "EPIC")
def shield_emblem():
    m = back_model("shield_emblem")
    straps(m, leather("4a3324"))
    m.fill(cyl_z(8, 8.4, 4.4, 4.2, 5.6), gold(tones=BRASS))
    m.fill(cyl_z(8, 8.4, 3.8, 3.8, 4.4), velvet("1f3f9e"))
    import random
    rnd = random.Random(4)
    for a in range(0, 360, 30):
        r = math.radians(a)
        m.fill(sphere(8 + math.cos(r) * 4.1, 8.4 + math.sin(r) * 4.1, 4.0, 0.3), silver())
    m.fill(prism([(-1.8, 1.8), (1.8, 1.8), (1.8, -0.4), (0, -2.4), (-1.8, -0.4)], "z", 3.5, 3.8).move(8, 8.4, 0), gold())
    m.fill(prism([(-1.4, 1.45), (1.4, 1.45), (1.4, -0.3), (0, -1.95), (-1.4, -0.3)], "z", 3.35, 3.55).move(8, 8.4, 0), velvet("c8283a"))
    m.fill(prism(star_points(0, 0, 0.9, 0.36), "z", 3.2, 3.4).move(8, 8.6, 0), gold())
    for x in range(-3, 4):
        m.paint(box(8 + x - 0.08, 4.2, 3.7, 8 + x + 0.08, 12.6, 3.85) - cyl_z(8, 8.4, 2.6, 0, 9), velvet("2a52b8"))
    return m


@back("gear_wheel", "Gear Wheel", "RARE")
def gear_wheel():
    m = back_model("gear_wheel")
    Br = gold(tones=["4a2a10", "7a4a1c", "a8702c", "c48a3a", "dcaa5a", "f0cc8a", "fff0d0"])

    def gear(cx, cy, R, teeth, z0, z1, hole):
        g = cyl_z(cx, cy, R, z0, z1)
        for k in range(teeth):
            a = 360 * k / teeth
            g = g | box(cx - 0.5, cy + R - 0.3, z0, cx + 0.5, cy + R + 0.8, z1).rot("z", a, (cx, cy, 0))
        g = g - cyl_z(cx, cy, hole, z0 - 1, z1 + 1)
        for k in range(5):
            a = math.radians(72 * k + 36)
            g = g - cyl_z(cx + math.cos(a) * R * 0.6, cy + math.sin(a) * R * 0.6, R * 0.2, z0 - 1, z1 + 1)
        return g
    m.fill(gear(8, 8.6, 3.8, 14, 4.4, 5.6, 0.9), Br)
    m.fill(gear(11.2, 4.6, 1.9, 9, 3.6, 4.4, 0.5), metal("8a909c"))
    m.fill(cyl_z(8, 8.6, 0.9, 3.8, 5.6), metal("3a3e48"))
    m.fill(cyl_z(8, 8.6, 0.45, 3.6, 3.8), glow("ffb53a", 14))
    m.fill(cyl_z(11.2, 4.6, 0.5, 3.4, 3.6), glow("ffb53a", 13))
    return m


@back("solar_panel", "Solar Panel", "EPIC")
def solar_panel():
    m = back_model("solar_panel")
    straps(m, solid("2a2c34"))
    m.fill(rbox(6.4, 7.6, 3.6, 9.6, 12.6, 5.6, 0.5), metal("5a606e"))

    def draw(p, r):
        rx, ry, rz = r
        p.fill(box(rx, ry - 3.0, rz - 0.6, rx + 9.0, ry + 2.0, rz - 0.15), metal("b8c0cc"))
        for i in range(4):
            for j in range(3):
                x0 = rx + 0.35 + i * 2.15
                y0 = ry - 2.7 + j * 1.55
                p.fill(box(x0, y0, rz - 0.75, x0 + 1.95, y0 + 1.35, rz - 0.5), glass("2a5fd6"))
        p.fill(cyl_x(ry - 0.5, rz - 0.4, 0.3, rx - 1.0, rx + 0.4), silver())
    wing_pair(m, draw, 22.5, root=(10.0, 10.6, 4.4), outline_col=None)
    m.fill(sphere(8, 12.0, 3.5, 0.35), glow("7cff6b", 14))
    return m


@back("void_orb", "Void Orb", "LEGENDARY")
def void_orb():
    m = back_model("void_orb")
    m.fill(sphere(8, 9.4, 2.6, 2.1), crystal("2a1745"))
    m.fill(sphere(8, 9.4, 2.6, 1.3), glow("8a3cff", 15, core="f0e0ff"))
    m.carve(box(4, 9.0, 0, 12, 9.8, 2.2))
    m.fill(torus(0, 0, 0, 3.1, 0.25).rot("x", 70, (0, 0, 0)).rot("z", 20, (0, 0, 0)).move(8, 9.4, 2.6), glow("c39bff", 14))
    m.fill(torus(0, 0, 0, 3.6, 0.18).rot("x", 110, (0, 0, 0)).rot("z", -25, (0, 0, 0)).move(8, 9.4, 2.6), glow("8a3cff", 12))
    for k in range(5):
        a = 2 * math.pi * k / 5
        m.fill(prism([(0, -0.5), (0.28, 0), (0, 0.5), (-0.28, 0)], "z", 2.4, 2.8).move(8 + math.cos(a) * 4.2, 9.4 + math.sin(a) * 4.2, 0),
               glow("b48cff", 13))
    return m


@back("rocket_pack", "Rocket Pack", "EPIC")
def rocket_pack():
    m = back_model("rocket_pack")
    straps(m, solid("2a2c34"))
    m.fill(cyl(8, 3.6, 1.9, 5.0, 11.4), solid("f4f4f4", 0.4))
    m.fill(cone(8, 3.6, 1.9, 11.4, 3.4, r1=0.1), solid("d22d2d", 0.4))
    for y in (6.2, 9.6):
        m.paint(cyl(8, 3.6, 2.1, y, y + 0.7), solid("d22d2d", 0.4))
    m.fill(cyl_z(8, 8.8, 0.75, 1.55, 1.8), glass("7fd9ff"))
    m.fill(torus(0, 0, 0, 0.8, 0.18).rot("x", 90, (0, 0, 0)).move(8, 8.8, 1.7), silver())
    fin = prism([(0, 6.6), (1.6, 5.0), (1.6, 3.8), (0, 4.6)], "z", -0.18, 0.18).move(9.7, 0, 3.6)
    for a in (0, 180, 270):
        m.fill(fin.rot("y", a, (8, 0, 3.6)), solid("d22d2d", 0.4))
    m.fill(cone(8, 3.6, 1.2, 3.8, 1.2, r1=1.6), metal("3a3e48"))
    flame(m, 8, 3.8, 3.6, 1.6)
    return m


@back("retro_jetpack", "Retro Jetpack", "RARE")
def retro_jetpack():
    m = back_model("retro_jetpack")
    B = gold(tones=BRASS)
    straps(m, leather("4a3324"))
    for x in (5.6, 10.4):
        m.fill(cyl(x, 3.8, 1.75, 4.8, 12.0), B)
        m.fill(dome(x, 3.8, 1.75, 12.0, 1.0), B)
        for y in (5.8, 8.4, 11.0):
            m.paint(cyl(x, 3.8, 1.9, y, y + 0.35), gold(tones=["3a240a", "5a3a10", "7a5020", "8a5a1c", "a8702c", "c99a5a", "e8c89a"]))
            rivets(m, [(x + 1.8 * math.cos(a), y + 0.17, 3.8 + 1.8 * math.sin(a)) for a in np.linspace(-math.pi, 0, 6)], silver(), 0.15)
        m.fill(cone(x, 3.8, 1.0, 3.4, 1.4, r1=1.4), metal("3a3e48"))
        flame(m, x, 3.4, 3.8, 1.2)
    m.fill(cyl_z(8, 9.8, 1.0, 2.3, 3.2), B)
    m.fill(cyl_z(8, 9.8, 0.75, 2.1, 2.3), flat("f4efe0"))
    m.fill(box(7.95, 9.7, 2.0, 8.05, 10.4, 2.1), solid("d22d2d"))
    return m


@back("rod_on_back", "Fishing Rod", "COMMON")
def rod_on_back():
    m = back_model("rod_on_back")
    m.fill(tube([(4.4, 1.6, 4.6), (11.8, 17.0, 4.6)], 0.32, 0.14), wood("9a7040"))
    m.paint(capsule((4.4, 1.6, 4.6), (5.6, 4.2, 4.6), 0.42), leather("2a2a33"))
    m.fill(cyl_z(6.4, 5.2, 0.75, 3.4, 4.2), silver())
    m.fill(capsule((6.4, 5.2, 3.3), (7.0, 5.2, 3.1), 0.12), solid("2a2a33"))
    m.fill(tube([(6.4, 5.9, 4.0), (11.8, 17.0, 4.4), (12.6, 15.0, 4.2), (12.6, 13.4, 4.2)], 0.06), solid("f4f4f4"))
    m.fill(sphere(12.6, 13.0, 4.2, 0.4), solid("f4f4f4"))
    m.fill(sphere(12.6, 13.0, 4.2, 0.4) & half("y", 13.0), solid("d22d2d"))
    # bait bag
    m.fill(rbox(8.6, 4.4, 3.4, 11.4, 7.2, 5.6, 0.4), leather("b08a5a"))
    m.fill(rbox(8.4, 6.6, 3.2, 11.6, 7.4, 5.7, 0.3), leather("8a6a3a"))
    m.fill(tube([(4.4, 14.4, 5.5), (9.0, 7.2, 5.5)], 0.2), leather("5a3a22"))
    return m


@back("crossed_picks", "Crossed Picks", "EPIC")
def crossed_picks():
    m = back_model("crossed_picks")

    def pick(a, b, head_c):
        m.fill(capsule(a, b, 0.32), wood("6b4a2a"))
        hx, hy = b[0], b[1]
        d = np.array(b) - np.array(a)
        d = d / np.linalg.norm(d)
        perp = np.array([-d[1], d[0], 0])
        p1 = np.array(b) + perp * 2.6 - d * 0.9
        p2 = np.array(b) - perp * 2.6 - d * 0.9
        m.fill(tube([tuple(p1), tuple(np.array(b) + d * 0.2), tuple(p2)], 0.55, 0.55), crystal(head_c))
        m.fill(sphere(*b, 0.55), metal("5a606e"))
        m.paint(capsule(tuple(np.array(a) + d * 0.6), tuple(np.array(a) + d * 2.4), 0.36), leather("3a2a20"))
    pick((4.0, 3.0, 4.3), (11.2, 12.4, 4.3), "5fe0e8")
    pick((12.0, 3.0, 4.9), (4.8, 12.4, 4.9), "5fe0e8")
    m.fill(sphere(8, 7.8, 4.0, 0.6), gold())
    return m


@back("harvest_basket", "Harvest Basket", "COMMON")
def harvest_basket():
    m = back_model("harvest_basket")
    straps(m, leather("5a3a22"))
    m.fill(rbox(4.8, 3.6, 2.0, 11.2, 10.6, 5.6, 0.8) - rbox(5.4, 4.2, 2.6, 10.6, 12, 5.0, 0.5), straw("c9944a"))
    m.paint(box(0, 10.0, 0, 16, 10.6, 9), straw("a8702c"))
    # produce
    m.fill(sphere(6.4, 10.6, 3.2, 1.05), solid("d22d2d", 0.5))
    m.fill(capsule((6.4, 11.5, 3.2), (6.5, 12.0, 3.1), 0.1), wood("5a3a22"))
    m.fill(sphere(9.4, 10.4, 3.6, 1.1), solid("ff9a2a", 0.5))
    m.fill(tube([(8.0, 9.8, 4.4), (8.2, 13.6, 4.0)], 0.5, 0.15), solid("ff7a1f", 0.5))
    for dx in (-0.4, 0, 0.4):
        m.fill(capsule((8.2, 13.4, 4.0), (8.2 + dx * 2, 14.8, 4.0), 0.14), solid("3fae49"))
    for k in range(5):
        m.fill(capsule((10.4 + k * 0.15, 10.0, 4.6), (10.8 + k * 0.3, 14.2, 4.6), 0.1), solid("d8b04a"))
        m.fill(ellipsoid(10.8 + k * 0.3, 14.4, 4.6, 0.22, 0.6, 0.22), solid("e8c060", 0.4))
    m.fill(sphere(7.8, 10.8, 2.4, 0.8), solid("7cc84a", 0.5))
    return m


@back("scuba_tank", "Scuba Tank", "RARE")
def scuba_tank():
    m = back_model("scuba_tank")
    straps(m, solid("1c1c22"))
    Y = solid("f4c623", 0.5, soft=1)
    for x in (6.0, 10.0):
        m.fill(cyl(x, 4.0, 1.8, 3.2, 12.0), Y)
        m.fill(dome(x, 4.0, 1.8, 12.0, 1.2), Y)
        m.fill(cyl(x, 4.0, 0.5, 13.0, 14.0), silver())
    m.fill(box(4.0, 6.4, 2.0, 12.0, 7.2, 4.2), solid("1c1c22"))
    m.fill(box(4.0, 9.6, 2.0, 12.0, 10.4, 4.2), solid("1c1c22"))
    for y in (6.8, 10.0):
        m.fill(rbox(7.4, y - 0.5, 1.8, 8.6, y + 0.5, 2.1, 0.15), silver())
    m.fill(capsule((6.0, 14.0, 4.0), (10.0, 14.0, 4.0), 0.35), silver())
    m.fill(cyl_z(8, 14.0, 0.6, 3.0, 3.6), metal("2a2c34"))
    m.fill(tube([(10.0, 14.0, 4.0), (12.4, 13.0, 4.6), (12.8, 10.0, 5.4)], 0.22), solid("2a2c34"))
    m.paint(box(4, 4.0, 0, 16, 4.6, 9), solid("d22d2d", 0.3))
    return m


@back("turtle_shell", "Turtle Shell", "RARE")
def turtle_shell():
    m = back_model("turtle_shell")
    m.fill(ellipsoid(8, 8.2, 5.6, 4.4, 5.6, 2.8) & half("z", 5.6, above=False), solid("4f8a32", 0.5))

    def hexes(X, Y, Z):
        u = X / 1.9
        v = Y / 1.65 + 0.5 * (np.floor(u) % 2)
        fu, fv = u - np.floor(u), v - np.floor(v)
        edge = (fu < 0.14) | (fv < 0.14)
        return edge.astype(int)
    m.paint(half("z", 5.6, above=False), by(hexes, solid("5fa83a", 0.4, soft=1), solid("2f5a1e", 0.2)))
    m.fill(torus(0, 0, 0, 4.4, 0.32).rot("x", 90, (0, 0, 0)).move(8, 8.2, 5.2) | ellipsoid(8, 8.2, 5.3, 4.65, 5.85, 0.3), solid("c9b48a", 0.4))
    m.carve(ellipsoid(8, 8.2, 5.4, 4.3, 5.5, 0.5) - ellipsoid(8, 8.2, 5.4, 4.3, 5.5, 0.3))
    return m


@back("guitar", "Guitar", "EPIC")
def guitar():
    m = back_model("guitar")
    body_c = (6.4, 5.4, 4.4)
    R = solid("c8213a", 0.5, soft=1)
    m.fill((ellipsoid(6.2, 4.6, 4.4, 2.6, 2.2, 0.6) | ellipsoid(7.4, 6.8, 4.4, 1.9, 1.7, 0.6)).rot("z", -32, body_c), R)
    m.paint((ellipsoid(6.2, 4.6, 3.75, 2.7, 2.3, 0.2) | ellipsoid(7.4, 6.8, 3.75, 2.0, 1.8, 0.2)).rot("z", -32, body_c)
            - (ellipsoid(6.2, 4.6, 3.6, 2.3, 1.9, 0.5) | ellipsoid(7.4, 6.8, 3.6, 1.6, 1.4, 0.5)).rot("z", -32, body_c), solid("f4f4f4", 0.3))
    m.fill(capsule((7.4, 6.6, 3.7), (12.6, 15.2, 3.7), 0.42), wood("5a3418"))
    m.fill(rbox(12.2, 15.0, 3.3, 14.0, 17.4, 4.1, 0.3).rot("z", -32, (13.1, 16.2, 3.7)), solid("1c1c22"))
    for k in range(3):
        m.fill(sphere(12.6 + k * 0.4, 15.8 + k * 0.6, 3.25, 0.18), silver())
    for dx in (-0.15, 0.05, 0.25):
        m.fill(capsule((6.4 + dx, 5.6, 3.65), (12.4 + dx, 15.0, 3.65), 0.05), silver())
    m.fill(rbox(5.4, 4.6, 3.55, 7.2, 5.4, 3.8, 0.1).rot("z", -32, body_c), solid("1c1c22"))
    m.fill(tube([(5.4, 3.0, 5.5), (4.4, 6.0, 5.5), (5.0, 12.0, 5.5), (6.0, 14.6, 5.5)], 0.25), leather("2a2a33"))
    return m


@back("crystal_quiver", "Crystal Quiver", "EPIC")
def crystal_quiver():
    m = back_model("crystal_quiver")
    axis_a, axis_b = (5.0, 3.0, 4.0), (11.0, 12.0, 4.0)
    m.fill(capsule(axis_a, axis_b, 1.35, 1.5), crystal("6a3fc8"))
    for t in (0.15, 0.5, 0.85):
        p = [axis_a[k] + (axis_b[k] - axis_a[k]) * t for k in range(3)]
        m.paint(sphere(p[0], p[1], p[2], 1.7) - sphere(p[0], p[1], p[2], 1.3), silver())
    m.paint(capsule(axis_a, axis_b, 0.5, 0.6) & half("z", 2.9, above=False), glow("c39bff", 13))
    m.fill(tube([(4.2, 14.4, 5.4), (4.4, 13.0, 5.5), (12.2, 2.4, 5.5), (12.0, 1.6, 5.4)], 0.3), solid("2a2240"))
    for k, (dx, dz) in enumerate(((-0.6, -0.3), (0.4, -0.4), (0.0, 0.5))):
        a = (11.0 + dx, 12.0, 4.0 + dz)
        b = (12.2 + dx, 14.4, 4.0 + dz)
        m.fill(capsule(a, b, 0.12), silver())
        m.fill(cone(b[0], b[2], 0.4, b[1], 1.3, r1=0.02, lean=(0.5, 0)), crystal("c39bff"))
    return m


@back("propeller_pack", "Propeller Pack", "LEGENDARY")
def propeller_pack():
    m = back_model("propeller_pack")
    straps(m, solid("2a2c34"))
    m.fill(rbox(5.4, 4.6, 3.6, 10.6, 12.2, 5.6, 0.8), solid("c8213a", 0.5, soft=1))
    m.fill(torus(0, 0, 0, 4.2, 0.45).rot("x", 90, (0, 0, 0)).move(8, 8.4, 2.6), gold())
    for a in range(0, 360, 45):
        r = math.radians(a)
        m.fill(capsule((8 + math.cos(r) * 4.2, 8.4 + math.sin(r) * 4.2, 2.6), (8 + math.cos(r) * 2.6, 8.4 + math.sin(r) * 2.6, 3.6), 0.12), metal("5a606e"))
    for a in (20, 140, 260):
        blade = ellipsoid(10.2, 8.4, 2.4, 2.1, 0.55, 0.16).rot("x", 15, (10.2, 8.4, 2.4)).rot("z", a, (8, 8.4, 2.4))
        m.fill(blade, solid("31b6ff", 0.4))
    m.fill(cyl_z(8, 8.4, 0.6, 1.9, 3.6), metal("3a3e48"))
    m.fill(sphere(8, 8.4, 1.9, 0.35), gold())
    return m


# the winged back items are lifted from the reference sheet (tools/art/backs/<id>/)
def _from_art():
    from outfits import back_from_art, ART_BACKS
    for i, (id, name, rarity, fn) in enumerate(BACKS):
        d = ART_BACKS / id
        if (d / "art.json").exists():
            BACKS[i] = (id, name, rarity, (lambda d, id: lambda: back_from_art(d, id))(d, id))


_from_art()
