"""Pickaxe skins (32x32 sprites, item/handheld) + the Skin Crate model."""
import math
from PIL import Image
from vox import Vox, hexc, mix, shade
from shapes import C, sq_ring, noise

PICKS = []      # (id, name, rarity, image, text)
N = 32
OUT = (14, 16, 22)


def pick(id, name, rarity, text):
    def deco(fn):
        PICKS.append((id, name, rarity, fn, text))
        return fn
    return deco


class P:
    def __init__(self):
        self.px = [[None] * N for _ in range(N)]

    def set(self, x, y, c):
        if 0 <= x < N and 0 <= y < N:
            self.px[y][x] = c

    def get(self, x, y):
        return self.px[y][x] if 0 <= x < N and 0 <= y < N else None

    def image(self, out=OUT):
        o = [row[:] for row in self.px]
        for y in range(N):
            for x in range(N):
                if self.px[y][x] is None:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        if self.get(x + dx, y + dy) is not None and self.get(x + dx, y + dy) != "out":
                            o[y][x] = out
                            break
        im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
        for y in range(N):
            for x in range(N):
                if o[y][x] is not None:
                    im.putpixel((x, y), tuple(o[y][x]) + (255,))
        return im


def handle(p, c1, c2, band=None, x0=4.5, y0=27.5, x1=18.5, y1=13.5, w=1.25):
    dx, dy = x1 - x0, y1 - y0
    for y in range(N):
        for x in range(N):
            cx, cy = x + 0.5, y + 0.5
            t = ((cx - x0) * dx + (cy - y0) * dy) / (dx * dx + dy * dy)
            if 0 <= t <= 1:
                qx, qy = x0 + t * dx, y0 + t * dy
                if math.hypot(cx - qx, cy - qy) <= w:
                    c = c1 if int(t * 14) % 2 == 0 else c2
                    if band and 0.78 <= t <= 0.9:
                        c = band
                    p.set(x, y, c)


def arc_head(p, c1, c2, hi, span=62, thick=4.2, R=13.0, cx=21.0, cy=11.0, facet=True, tips=None):
    """Crescent head round the end of the handle, bulging up-right."""
    ux, uy = 1 / math.sqrt(2), -1 / math.sqrt(2)
    ccx, ccy = cx - ux * R, cy - uy * R
    sp = math.radians(span)
    for y in range(N):
        for x in range(N):
            vx, vy = x + 0.5 - ccx, y + 0.5 - ccy
            r = math.hypot(vx, vy)
            ang = math.atan2(vy, vx) - math.atan2(uy, ux)
            ang = (ang + math.pi) % (2 * math.pi) - math.pi
            if abs(ang) > sp:
                continue
            k = abs(ang) / sp
            th = thick * (1 - k ** 1.6) + 0.6
            inner, outer = R - th * 0.45, R + th * 0.55
            if inner <= r <= outer:
                light = (r - inner) / max(0.01, outer - inner)
                t = (ang / sp + 1) / 2
                col = mix(c1, c2, t)
                if light > 0.7:
                    col = mix(col, hi, 0.6)
                elif light < 0.3:
                    col = shade(col, 0.7)
                if facet and abs(r - R) < 0.35 and k < 0.75:
                    col = shade(col, 0.6)
                if tips and k > 0.82:
                    col = tips
                p.set(x, y, col)


def cleaver_head(p, c1, c2, hi, edge):
    """A big half-moon axe blade on the upper left of the handle end + a spike."""
    ux, uy = 1 / math.sqrt(2), -1 / math.sqrt(2)     # along the handle, to the head
    nx, ny = -1 / math.sqrt(2), -1 / math.sqrt(2)    # across it, to the upper left
    for y in range(N):
        for x in range(N):
            rx, ry = x + 0.5 - 18.5, y + 0.5 - 13.5
            a = rx * ux + ry * uy
            b = rx * nx + ry * ny
            if b >= 0.5:
                e = (a / 6.8) ** 2 + ((b - 1.0) / 9.5) ** 2
                if e <= 1:
                    col = mix(c1, c2, min(1, b / 9))
                    if e > 0.72:
                        col = edge
                    elif abs(a) < 0.8 and b < 6:
                        col = shade(col, 0.8)
                    p.set(x, y, col)
            elif -5 <= b < 0.5 and abs(a) <= 1.2 + (b + 5) * 0.25:
                p.set(x, y, hi if b < -3.5 else c2)


def hammer_head(p, c1, c2, hi):
    for y in range(N):
        for x in range(N):
            # a block centred on the handle end, turned 45 degrees
            # u across the handle (the long side of the head), v along it
            u = ((x + 0.5 - 20.5) + (y + 0.5 - 11.5)) / math.sqrt(2)
            v = ((x + 0.5 - 20.5) - (y + 0.5 - 11.5)) / math.sqrt(2)
            if abs(u) <= 7.0 and abs(v) <= 3.6:
                col = mix(c1, c2, (u + 7) / 14)
                if abs(v) > 2.8:
                    col = shade(col, 0.75)
                if abs(u) > 6.0:
                    col = hi
                p.set(x, y, col)


def crystal_head(p, c1, c2, hi):
    arc_head(p, c1, c2, hi, facet=False)
    for (x, y, h) in ((9, 9, 4), (14, 5, 5), (20, 4, 4), (25, 8, 4), (27, 14, 3)):
        for i in range(h):
            p.set(x, y - i, mix(c2, hi, i / h))
            if i < h - 1:
                p.set(x + 1, y - i, c1)


def trident_head(p, c1, c2, hi):
    for k, (ex, ey) in enumerate(((28, 2), (21, 1), (29, 9))):
        sx, sy = 19, 13
        n = 14
        for i in range(n + 1):
            t = i / n
            x, y = round(sx + (ex - sx) * t), round(sy + (ey - sy) * t)
            p.set(x, y, mix(c1, c2, t))
            if t < 0.85:
                p.set(x + 1, y, c1)
        p.set(ex, ey, hi)
    for i in range(5):
        p.set(16 + i, 14 - i, c2)
        p.set(17 + i, 15 - i, c1)


def scythe_head(p, c1, c2, hi, edge):
    for y in range(N):
        for x in range(N):
            vx, vy = x + 0.5 - 22, y + 0.5 - 16
            r = math.hypot(vx, vy)
            a = math.atan2(vy, vx)
            if 9.5 <= r <= 13 and -math.pi * 0.98 <= a <= -math.pi * 0.42:
                k = (r - 9.5) / 3.5
                p.set(x, y, edge if k > 0.75 else mix(c1, c2, k))
    for i in range(4):
        p.set(18 + i, 13 - i, c1)


def gem(p, x, y, c, hi=(255, 255, 255)):
    for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        p.set(x + dx, y + dy, c)
    p.set(x, y, hi)


def sparkle(p, pts, c=(255, 255, 240)):
    for x, y in pts:
        p.set(x, y, c)


def zigzag(p, pts, c):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0))
        for i in range(n + 1):
            p.set(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), c)


WOOD = (C("8a5a32"), C("6b4423"))
DARK = (C("3a3040"), C("261e2c"))
GOLDH = (C("e8b830"), C("b8861a"))
BONE = (C("e8e0c8"), C("bfb49a"))


def basic(c1, c2, hi, hnd=WOOD, band=None, **kw):
    p = P()
    handle(p, hnd[0], hnd[1], band)
    arc_head(p, c1, c2, hi, **kw)
    return p


# ---------------------------------------------------------------- COMMON (9)
@pick("stone_breaker", "Stone Breaker", "COMMON", "Rough, heavy, honest.")
def _():
    return basic(C("8a8a90"), C("6a6a72"), C("b0b0b8"))


@pick("copper_pick", "Copper Pick", "COMMON", "Shines until it doesn't.")
def _():
    return basic(C("d87a3a"), C("b8582a"), C("f2b07a"))


@pick("iron_digger", "Iron Digger", "COMMON", "The miner's old friend.")
def _():
    return basic(C("d8dce4"), C("a8b0bc"), C("ffffff"), band=C("6a6a72"))


@pick("oak_splitter", "Oak Splitter", "COMMON", "Carved from one old oak.")
def _():
    return basic(C("b8864a"), C("8a5a32"), C("e0b07a"), hnd=(C("6b4423"), C("4a2e18")))


@pick("coal_crusher", "Coal Crusher", "COMMON", "Black dust in every crack.")
def _():
    p = basic(C("3a3a42"), C("26262c"), C("6a6a78"))
    sparkle(p, [(12, 8), (22, 6)], C("8a8a96"))
    return p


@pick("sandstone_pick", "Sandstone Pick", "COMMON", "Warm from the desert sun.")
def _():
    return basic(C("e8d29a"), C("c8b070"), C("fff0c0"))


@pick("clay_chipper", "Clay Chipper", "COMMON", "Fired twice, cracks once.")
def _():
    return basic(C("b87a5a"), C("945a42"), C("d8a080"), band=C("3a7ab8"))


@pick("flint_pick", "Flint Pick", "COMMON", "Sharp edges, sharper sparks.")
def _():
    p = basic(C("4a4a52"), C("6a6a74"), C("a0a0aa"), hnd=BONE)
    sparkle(p, [(25, 7)], C("ffb040"))
    return p


@pick("granite_pick", "Granite Pick", "COMMON", "Speckled and stubborn.")
def _():
    p = basic(C("b07a62"), C("8a5a48"), C("d8a890"))
    sparkle(p, [(11, 9), (16, 6), (23, 7), (26, 12)], C("f0e0d8"))
    return p


# ---------------------------------------------------------------- RARE (8)
@pick("emerald_edge", "Emerald Edge", "RARE", "Cut from a single green vein.")
def _():
    p = basic(C("3ee07f"), C("1e9e5a"), C("b0ffd0"), band=C("e8b830"))
    gem(p, 18, 9, C("1e9e5a"))
    return p


@pick("sapphire_pick", "Sapphire Pick", "RARE", "Deep blue and very cold.")
def _():
    p = basic(C("3a7be8"), C("1e4aa8"), C("a0c8ff"), band=C("dfe3ea"))
    gem(p, 18, 9, C("1e4aa8"))
    return p


@pick("ruby_pick", "Ruby Pick", "RARE", "Burns red in the dark.")
def _():
    p = basic(C("e8304a"), C("a01830"), C("ffa0b0"), band=C("e8b830"))
    gem(p, 18, 9, C("a01830"))
    return p


@pick("frostbite", "Frostbite", "RARE", "Leaves ice on every block.")
def _():
    p = basic(C("bfe9ff"), C("5ab8ee"), C("ffffff"), hnd=(C("dfe8f0"), C("a8c0d8")), tips=C("ffffff"))
    sparkle(p, [(10, 6), (27, 15)], C("ffffff"))
    return p


@pick("toxic_pick", "Toxic Pick", "RARE", "Don't lick it.")
def _():
    p = basic(C("b8f040"), C("5ac81e"), C("eaffb0"), hnd=DARK, band=C("b8f040"))
    sparkle(p, [(12, 10), (24, 9), (20, 4)], C("eaffb0"))
    return p


@pick("rose_gold", "Rose Gold Pick", "RARE", "Polished every single night.")
def _():
    return basic(C("f2b0a0"), C("d8807a"), C("fff0ea"), hnd=(C("f2d0c0"), C("d8a898")))


@pick("ocean_pick", "Ocean Pick", "RARE", "Smells a little like salt.")
def _():
    p = basic(C("41c8e0"), C("1e7ab8"), C("c0f4ff"), hnd=(C("e8e0c8"), C("bfb49a")))
    sparkle(p, [(14, 6), (23, 10)], C("ffffff"))
    return p


@pick("amethyst_pick", "Amethyst Pick", "RARE", "Hums when you swing it.")
def _():
    p = P()
    handle(p, WOOD[0], WOOD[1], C("e8b830"))
    crystal_head(p, C("8a55e8"), C("b58cff"), C("f0e2ff"))
    return p


# ---------------------------------------------------------------- EPIC (6)
@pick("shadow_reaper", "Shadow Reaper", "EPIC", "Mines in the shadows.")
def _():
    p = P()
    handle(p, DARK[0], DARK[1], C("8a55e8"))
    scythe_head(p, C("2a2232"), C("4a3a5a"), C("b58cff"), C("b58cff"))
    return p


@pick("inferno_pick", "Inferno Pick", "EPIC", "Too hot to hold. Hold it anyway.")
def _():
    p = basic(C("ff8a1e"), C("d8201e"), C("ffe066"), hnd=DARK, band=C("ff8a1e"), tips=C("ffe066"))
    for x, y in ((12, 4), (13, 3), (19, 2), (20, 1), (26, 6), (27, 5)):
        p.set(x, y, C("ffd24a"))
    return p


@pick("storm_hammer", "Storm Hammer", "EPIC", "Every swing a thunderclap.")
def _():
    p = P()
    handle(p, C("5c6678"), C("3a4250"), C("41e0ff"))
    hammer_head(p, C("8a96aa"), C("5c667a"), C("dfe6f0"))
    zigzag(p, [(24, 2), (21, 6), (24, 7), (20, 12)], C("fff066"))
    return p


@pick("crystal_shard", "Crystal Shard", "EPIC", "Grown, not forged.")
def _():
    p = P()
    handle(p, C("dfe8f0"), C("a8c0d8"), C("41e0ff"))
    crystal_head(p, C("41c8e0"), C("9cf2ff"), C("ffffff"))
    return p


@pick("venom_fang", "Venom Fang", "EPIC", "Two fangs, one bite.")
def _():
    p = basic(C("5cc84a"), C("2a6a26"), C("d8ff80"), hnd=DARK, band=C("b8f040"), thick=5.4, tips=C("f4f4e8"))
    return p


@pick("nebula_pick", "Nebula Pick", "EPIC", "A small galaxy on a stick.")
def _():
    p = basic(C("6a3ab8"), C("ff6fd8"), C("c8a0ff"), hnd=DARK, band=C("ff6fd8"))
    sparkle(p, [(11, 8), (15, 4), (21, 5), (25, 10), (18, 7)])
    return p


# ---------------------------------------------------------------- LEGENDARY (5)
@pick("solar_cleaver", "Solar Cleaver", "LEGENDARY", "Burns like the sun.")
def _():
    p = P()
    handle(p, GOLDH[0], GOLDH[1], C("ff6a1e"))
    cleaver_head(p, C("ffd24a"), C("ff8a1e"), C("fff4c0"), C("fff4c0"))
    sparkle(p, [(6, 5), (12, 2)], C("ffffff"))
    return p


@pick("comet_pick", "Comet Pick", "LEGENDARY", "Fell from the sky last night.")
def _():
    p = basic(C("2a3a8a"), C("1a2050"), C("8fb8ff"), hnd=(C("3a4a8a"), C("26306a")), band=C("ffe066"), tips=C("ffe066"))
    sparkle(p, [(10, 7), (15, 4), (22, 5), (26, 11), (19, 8)], C("fff4a0"))
    return p


@pick("dragonbone", "Dragonbone Pick", "LEGENDARY", "From a dragon nobody misses.")
def _():
    p = basic(C("f4ecd8"), C("c8bb97"), C("ffffff"), hnd=BONE, band=C("c8323a"), thick=5.0)
    gem(p, 18, 9, C("c8323a"))
    return p


@pick("abyssal_trident", "Abyssal Trident", "LEGENDARY", "Pulled up from the deep.")
def _():
    p = P()
    handle(p, C("1e4a6a"), C("12304a"), C("41e0ff"))
    trident_head(p, C("2fb8a0"), C("9cf2e8"), C("ffffff"))
    return p


@pick("prism_pick", "Prism Pick", "LEGENDARY", "Splits the light in seven.")
def _():
    p = P()
    handle(p, C("f4f4f8"), C("c8c8d8"), C("ff6fd8"))
    cols = [C("ff4a4a"), C("ff9a2a"), C("ffe02a"), C("4ae04a"), C("2ab8ff"), C("6a5aff"), C("c84aff")]
    arc_head(p, cols[0], cols[-1], C("ffffff"), facet=False)
    for y in range(N):
        for x in range(N):
            c = p.get(x, y)
            if c is not None and c not in (C("f4f4f8"), C("c8c8d8"), C("ff6fd8")):
                p.set(x, y, cols[min(6, max(0, (x - y + 4) // 3 % 7))])
    return p


# ---------------------------------------------------------------- MYTHIC (2)
@pick("thunder_god", "Thunder God Pick", "MYTHIC", "The king of the storm's own pick.")
def _():
    p = basic(C("fff4c0"), C("e8b830"), C("ffffff"), hnd=GOLDH, band=C("41e0ff"), thick=5.6, tips=C("41e0ff"))
    zigzag(p, [(27, 1), (24, 5), (27, 6), (23, 11)], C("41e0ff"))
    zigzag(p, [(9, 2), (12, 5), (9, 6)], C("41e0ff"))
    gem(p, 18, 9, C("41e0ff"))
    return p


@pick("nexium_core", "Nexium Core Pick", "MYTHIC", "Mined out of the core itself.")
def _():
    p = P()
    handle(p, C("1e2a2a"), C("12201e"), C("3ee07f"))
    crystal_head(p, C("3ee07f"), C("27e7e7"), C("eafff4"))
    gem(p, 18, 9, C("27e7e7"))
    sparkle(p, [(7, 3), (13, 1), (28, 3), (29, 16)], C("eafff4"))
    return p


# ---------------------------------------------------------------- the crate
def skin_crate():
    """A golden chest (block size) for the Skin Crate station + its lid."""
    gold, gold2, red, red2, black, gem = C("f2c230"), C("b8861a"), C("a3123a"), C("7a0e2c"), C("1c1c22"), C("41e0ff")
    base = Vox("skin_crate")
    base.box(1, 0, 2, 15, 9, 14, red)
    sq_ring(base, 1, 2, 15, 14, 0, 9, lambda x, y, z: gold if (x in (1, 14) and z in (2, 13)) else None)
    for x in (1, 14):
        for z in (2, 13):
            base.box(x, 0, z, x + 1, 9, z + 1, gold)
    base.box(1, 0, 2, 15, 1, 14, gold2)
    base.box(1, 8, 2, 15, 9, 14, gold)
    base.box(6, 3, 1, 10, 8, 2, gold)
    base.box(7, 4, 0, 9, 6, 1, black)
    lid = Vox("skin_crate_lid")
    lid.box(1, 9, 2, 15, 14, 14, red2)
    lid.box(1, 9, 2, 15, 10, 14, gold)
    lid.box(1, 13, 2, 15, 14, 14, gold)
    for x in (1, 7, 14):
        lid.box(x, 9, 2, x + 2 if x == 7 else x + 1, 14, 14, gold)
    lid.box(7, 14, 7, 9, 15, 9, gem)
    return base, lid
