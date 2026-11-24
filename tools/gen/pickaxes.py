"""The 30 pickaxe skins: a detailed 32x32 icon (menus, ground, frames) and a
3D model in the hand built from the same pixels (thicker head, raised gems,
glowing parts that shine in the dark). Item definition: select on the
display context (like vanilla's trident)."""
import math

import numpy as np
from PIL import Image

import bake
from hd import Model, C, tone, ramp, hash3, RES

N = 32
P0 = np.array([4.0, 28.0])     # handle end (bottom left)
HC = np.array([20.5, 11.5])    # head centre
U = np.array([1.0, -1.0]) / math.sqrt(2)   # along the handle, towards the head
NV = np.array([1.0, 1.0]) / math.sqrt(2)   # across (towards bottom right)

PICKS = []

Y, X = np.mgrid[0:N, 0:N] + 0.5
A = (X - HC[0]) * U[0] + (Y - HC[1]) * U[1]
B = (X - HC[0]) * NV[0] + (Y - HC[1]) * NV[1]
HN = np.hypot(X - P0[0], Y - P0[1])
HA = (X - P0[0]) * U[0] + (Y - P0[1]) * U[1]   # along the handle from its end
HB = (X - P0[0]) * NV[0] + (Y - P0[1]) * NV[1]
LEN = float(np.hypot(*(HC - P0)))
H = hash3(np.floor(X), np.floor(Y), 0, 77)


def pick(id, name, rarity, text):
    def deco(fn):
        PICKS.append((id, name, rarity, fn, text))
        return fn
    return deco


class Spr:
    def __init__(self):
        self.c = np.zeros((N, N, 3))
        self.a = np.zeros((N, N), bool)
        self.d = np.zeros((N, N))
        self.g = np.zeros((N, N), int)

    def put(self, m, col, depth, glow=0):
        col = np.asarray(col, float)
        if col.ndim == 1:
            col = np.broadcast_to(col, (N, N, 3))
        self.c[m] = col[m]
        self.a |= m
        self.d[m] = depth if np.ndim(depth) == 0 else np.asarray(depth)[m]
        self.g[m] = glow

    def outline(self, dark=(16, 14, 22), k=0.32):
        add = np.zeros((N, N), bool)
        nb = np.zeros((N, N, 3))
        cnt = np.zeros((N, N))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sa = np.roll(np.roll(self.a, dy, 0), dx, 1)
            sc = np.roll(np.roll(self.c, dy, 0), dx, 1)
            if dx == 1:
                sa[:, 0] = False
            if dx == -1:
                sa[:, -1] = False
            if dy == 1:
                sa[0, :] = False
            if dy == -1:
                sa[-1, :] = False
            m = sa & ~self.a
            add |= m
            nb[m] += sc[m]
            cnt[m] += 1
        nb[add] /= cnt[add][:, None]
        dk = np.array(dark, float)
        self.c[add] = nb[add] * k + dk * (1 - k)
        self.a |= add
        self.d[add] = 0.3
        self.g[add] = 0

    def image(self):
        out = np.zeros((N, N, 4), np.uint8)
        out[..., :3] = np.clip(np.round(self.c), 0, 255)
        out[..., 3] = self.a * 255
        return Image.fromarray(out, "RGBA")

    def model(self, name):
        """3D model: every pixel a 0.5 x 0.5 column, depth 2 x d around z = 8."""
        m = Model(name, (-1, -1, 4), (17, 17, 12))
        r = m.res
        for py in range(N):
            for px in range(N):
                if not self.a[py, px]:
                    continue
                d = self.d[py, px]
                x0 = int(round((px * 0.5 - m.lo[0]) * r))
                y1 = int(round((16 - py * 0.5 - m.lo[1]) * r))
                z0 = int(round((8 - d - m.lo[2]) * r))
                z1 = int(round((8 + d - m.lo[2]) * r))
                m.col[x0:x0 + 2, y1 - 2:y1, z0:z1] = self.c[py, px]
                m.mat[x0:x0 + 2, y1 - 2:y1, z0:z1] = 1 if not self.g[py, px] else 1 + self.g[py, px]
        return m


# ------------------------------------------------------------------ parts

def handle(s, c1, c2, wrap=None, collar=None, pommel=None, w=1.25, grain=True, pommel_glow=0):
    m = (np.abs(HB) <= w) & (HA >= 0) & (HA <= LEN - 1.0)
    t = HA / LEN
    base = np.where(((np.floor(HA * 0.9 + HB * 0.4)) % 2 == 0)[..., None], C(c1), C(c2)) if grain else np.broadcast_to(C(c1), (N, N, 3))
    edge = HB > w * 0.35
    col = np.where(edge[..., None], np.asarray(base) * 0.78, base)
    col = np.where((HB < -w * 0.45)[..., None], np.minimum(255, np.asarray(base) * 1.15), col)
    s.put(m, col, 0.5)
    if wrap is not None:
        wm = m & (t > 0.08) & (t < 0.42)
        band = (np.floor((HA - HB) * 0.75) % 2 == 0)
        wc = np.where(band[..., None], C(wrap), tone(wrap, 0.7))
        s.put(wm, wc, 0.6)
    if collar is not None:
        cm = (np.abs(HB) <= w + 0.6) & (HA >= LEN - 4.6) & (HA <= LEN - 2.8)
        s.put(cm, np.where((HB < 0)[..., None], tone(collar, 1.25), C(collar)), 0.7)
    if pommel is not None:
        pm = np.hypot(X - (P0[0] + 0.4), Y - (P0[1] - 0.4)) <= 1.9
        s.put(pm, np.where(((X - P0[0]) + (Y - P0[1]) < -0.5)[..., None], tone(pommel, 1.35), C(pommel)), 0.75, pommel_glow)


def crescent_mask(A0=1.2, K=0.034, T0=2.7, Bmax=12.4, p=1.7, tip=0.55, skew=0.0):
    ac = A0 - K * B * B + skew * B
    t = T0 * (1 - np.clip(np.abs(B) / Bmax, 0, 1) ** p) + tip
    s = (A - ac) / np.maximum(t, 1e-6)
    m = (np.abs(B) <= Bmax) & (np.abs(s) <= 1.0)
    return m, s


def shade_head(base_col, s, m, hi=1.3, lo=0.72, ridge=0.88):
    """Bevelled head: light outer edge, dark inner edge, a ridge in the middle,
    the upper left a bit brighter (light from the top left)."""
    col = np.asarray(base_col, float)
    f = np.ones((N, N))
    f = np.where(s > 0.55, hi, f)
    f = np.where(s < -0.6, lo, f)
    f = np.where(np.abs(s) < 0.12, ridge, f)
    f = f * (1 + 0.08 * (-B / 12.0))
    out = col * f[..., None]
    light = f > 1.0
    out = np.where(light[..., None], col + (255 - col) * (f[..., None] - 1) * 0.8, out)
    return np.clip(out, 0, 255)


def mat_ramp(c, mode="metal", seed=1):
    r = ramp(c, 7, 0.55, 1.45)
    n = hash3(np.floor(X), np.floor(Y), seed, 5)
    if mode == "stone":
        idx = 3 + (n > 0.82).astype(int) - (n < 0.2).astype(int) - (n < 0.06).astype(int)
    elif mode == "gem":
        f = np.floor((X - Y * 0.6) / 2.2) % 3
        idx = np.where(f == 0, 4, np.where(f == 1, 3, 2)) + (n > 0.94).astype(int) * 2
    elif mode == "wood":
        g = np.floor(B * 0.9 + 0.3 * np.sin(A)) % 3
        idx = np.where(g == 0, 2, 3) + (n > 0.9).astype(int)
    else:
        idx = 3 + (n > 0.9).astype(int) - (n < 0.1).astype(int)
    return r[np.clip(idx, 0, 6)]


def standard(s, head_c, mode="metal", handle_c=("8a5a34", "6e4428"), wrap=None, collar="9aa1ae", pommel=None,
             shape=None, glow=0, depth=0.8, gemc=None, gem_glow=0):
    handle(s, *handle_c, wrap=wrap, collar=collar, pommel=pommel)
    m, sv = crescent_mask(**(shape or {}))
    col = shade_head(mat_ramp(head_c, mode), sv, m)
    s.put(m, col, depth + 0.25 * (1 - np.abs(sv)), glow)
    if gemc:
        g = np.hypot(X - HC[0] + 0.3, Y - HC[1] - 0.3) <= 1.75
        gc = np.where(((X - HC[0]) + (Y - HC[1]) < 0)[..., None], tone(gemc, 1.45), C(gemc))
        gc = np.where((np.abs(X - HC[0] + 0.8) < 0.5)[..., None] & (np.abs(Y - HC[1] + 0.2) < 0.5)[..., None], np.array([255.0, 255, 255]), gc)
        s.put(g, gc, 1.15, gem_glow)
    return m, sv


def tip_paint(s, m, sv, col, frac=0.78, glow=0):
    t = m & (np.abs(B) > 12.4 * frac)
    s.put(t, np.broadcast_to(C(col), (N, N, 3)), s.d, glow)


def blob(cx, cy, r):
    return np.hypot(X - cx, Y - cy) <= r


def line_mask(p, q, w=0.6):
    p, q = np.array(p, float), np.array(q, float)
    d = q - p
    L2 = float(d @ d) or 1e-9
    t = np.clip(((X - p[0]) * d[0] + (Y - p[1]) * d[1]) / L2, 0, 1)
    return np.hypot(X - p[0] - d[0] * t, Y - p[1] - d[1] * t) <= w


def at(a, b):
    """Canvas point of local head coords (a along the handle, b across)."""
    p = HC + U * a + NV * b
    return (float(p[0]), float(p[1]))


# ------------------------------------------------------------------ commons

@pick("stone_breaker", "Stone Breaker", "COMMON", "Rough, heavy, honest.")
def stone_breaker():
    s = Spr()
    m, sv = standard(s, "8a8a8f", "stone", collar="6a6a70", shape={"T0": 3.0})
    for k in range(5):
        cx, cy = at(1.2 - 0.034 * (k * 5 - 10) ** 2, k * 5 - 10)
        s.put(blob(cx, cy, 0.55) & m, tone("5a5a60", 1.0) * np.ones((N, N, 3)), 0.9)
    s.outline()
    return s


@pick("copper_pick", "Copper Pick", "COMMON", "Shines until it doesn't.")
def copper_pick():
    s = Spr()
    m, sv = standard(s, "d47a3a", collar="b06030", pommel="d47a3a")
    pat = m & (hash3(np.floor(X / 2), np.floor(Y / 2), 3, 9) > 0.78) & (sv < 0.4)
    s.put(pat, np.broadcast_to(C("4fb89a"), (N, N, 3)), 0.9)
    s.outline()
    return s


@pick("iron_digger", "Iron Digger", "COMMON", "The miner's old friend.")
def iron_digger():
    s = Spr()
    m, sv = standard(s, "c9ced8", collar="5a606e", wrap="4a3324")
    for b in (-8, -3, 3, 8):
        cx, cy = at(1.2 - 0.034 * b * b - 0.4, b)
        s.put(blob(cx, cy, 0.5) & m, np.broadcast_to(C("6c7383"), (N, N, 3)), 1.0)
    s.outline()
    return s


@pick("oak_splitter", "Oak Splitter", "COMMON", "Carved from one old oak.")
def oak_splitter():
    s = Spr()
    m, sv = standard(s, "a8784a", "wood", handle_c=("6b4a2a", "5a3a22"), collar="3e7a2a", shape={"T0": 2.9})
    s.put(m & (sv > 0.7), np.broadcast_to(C("5a3a22"), (N, N, 3)), 0.9)
    for b in (-6, 5):
        cx, cy = at(2.8 - 0.034 * b * b, b)
        s.put(blob(cx, cy, 0.9), np.broadcast_to(C("4fae45"), (N, N, 3)), 0.8)
    s.outline()
    return s


@pick("coal_crusher", "Coal Crusher", "COMMON", "Black dust in every crack.")
def coal_crusher():
    s = Spr()
    m, sv = standard(s, "2c2c33", "stone", collar="4a4a52", shape={"T0": 3.1})
    emb = m & (hash3(np.floor(X), np.floor(Y), 9, 4) > 0.9)
    s.put(emb, np.broadcast_to(C("ff7a2a"), (N, N, 3)), 0.95, 9)
    s.outline()
    return s


@pick("sandstone_pick", "Sandstone Pick", "COMMON", "Warm from the desert sun.")
def sandstone_pick():
    s = Spr()
    m, sv = standard(s, "e2c98a", "stone", collar="b8964a")
    bands = m & (np.floor(sv * 3.5) % 2 == 0)
    s.put(bands, shade_head(mat_ramp("cfb070", "stone"), sv, m), s.d)
    s.outline()
    return s


@pick("clay_chipper", "Clay Chipper", "COMMON", "Fired twice, cracks once.")
def clay_chipper():
    s = Spr()
    m, sv = standard(s, "c26a48", "stone", collar="8a4a32")
    crack = m & (line_mask(at(0.5, -6), at(-0.5, -2), 0.35) | line_mask(at(-0.5, -2), at(0.6, 1.5), 0.35))
    s.put(crack, np.broadcast_to(C("5a2a1a"), (N, N, 3)), 0.8)
    s.outline()
    return s


@pick("flint_pick", "Flint Pick", "COMMON", "Sharp edges, sharper sparks.")
def flint_pick():
    s = Spr()
    m, sv = standard(s, "4a4a58", "gem", handle_c=("9a7040", "7a5530"), wrap="c9b48a", collar="c9b48a")
    chips = m & (sv > 0.45) & (np.floor(B) % 3 == 0)
    s.put(chips, np.broadcast_to(C("9a9aaa"), (N, N, 3)), 0.9)
    for b in (-11, 11):
        cx, cy = at(1.2 - 0.034 * b * b + 1.4, b)
        s.put(blob(cx, cy, 0.5), np.broadcast_to(C("fff1a8"), (N, N, 3)), 0.6, 12)
    s.outline()
    return s


@pick("granite_pick", "Granite Pick", "COMMON", "Speckled and stubborn.")
def granite_pick():
    s = Spr()
    m, sv = standard(s, "a86a5a", "stone", collar="7a4a3e", pommel="a86a5a")
    sp = m & (hash3(np.floor(X), np.floor(Y), 4, 2) > 0.8)
    s.put(sp, np.broadcast_to(C("e8d0c8"), (N, N, 3)), 0.9)
    s.outline()
    return s


# ------------------------------------------------------------------ rares

def gem_pick(s, c, fitting="f2c230", glow=0, handle_c=("3a2a20", "2a1e18"), wrap="5a3a22"):
    m, sv = standard(s, c, "gem", handle_c=handle_c, wrap=wrap, collar=fitting, pommel=fitting, gemc=c, gem_glow=glow)
    band = m & (np.abs(B) < 1.6) & (sv < 0.8)
    s.put(band, shade_head(np.broadcast_to(C(fitting), (N, N, 3)), sv, m), 0.95)
    for b in (-12.4 * 0.85, 12.4 * 0.85):
        tm = m & (np.abs(B - b) < 1.4)
        s.put(tm, shade_head(np.broadcast_to(tone(c, 1.35), (N, N, 3)), sv, m), s.d)
    return m, sv


@pick("emerald_edge", "Emerald Edge", "RARE", "Cut from a single green vein.")
def emerald_edge():
    s = Spr()
    gem_pick(s, "1fbf5f", "f2c230")
    s.outline()
    return s


@pick("sapphire_pick", "Sapphire Pick", "RARE", "Deep blue and very cold.")
def sapphire_pick():
    s = Spr()
    gem_pick(s, "2f6bff", "c9ced8")
    s.outline()
    return s


@pick("ruby_pick", "Ruby Pick", "RARE", "Burns red in the dark.")
def ruby_pick():
    s = Spr()
    gem_pick(s, "d4183a", "f2c230", glow=10)
    s.outline()
    return s


@pick("frostbite", "Frostbite", "RARE", "Leaves ice on every block.")
def frostbite():
    s = Spr()
    m, sv = standard(s, "9fe6ff", "gem", handle_c=("dff6ff", "b8e4f8"), wrap="5aa8d8", collar="f4fbff", gemc="e9fbff", gem_glow=12)
    for b in (-9, -5, -1, 4, 8):
        a0 = 1.2 - 0.034 * b * b - 2.7 * (1 - (abs(b) / 12.4) ** 1.7) - 0.4
        p = at(a0, b)
        q = at(a0 - 2.4 + abs(b) * 0.06, b + 0.6)
        s.put(line_mask(p, q, 0.55), np.broadcast_to(C("dff6ff"), (N, N, 3)), 0.5)
    s.outline(dark=(14, 40, 64))
    return s


@pick("toxic_pick", "Toxic Pick", "RARE", "Don't lick it.")
def toxic_pick():
    s = Spr()
    m, sv = standard(s, "6dff4a", "gem", handle_c=("2a2a33", "1c1c22"), wrap="6dff4a", collar="3a3a44", glow=8)
    for b in (-7, -2, 5):
        a0 = 1.2 - 0.034 * b * b - 2.7 * (1 - (abs(b) / 12.4) ** 1.7)
        s.put(line_mask(at(a0, b), at(a0 - 2.0, b), 0.45) | blob(*at(a0 - 2.4, b), 0.7), np.broadcast_to(C("b6ff6a"), (N, N, 3)), 0.5, 13)
    s.outline(dark=(10, 30, 10))
    return s


@pick("rose_gold", "Rose Gold Pick", "RARE", "Polished every single night.")
def rose_gold():
    s = Spr()
    m, sv = standard(s, "e9a88e", handle_c=("f6e7d8", "e8d4c0"), wrap="cf8770", collar="cf8770", pommel="ffd2c2", gemc="ff9fbf")
    eng = m & (np.abs(sv + 0.2) < 0.12) & (np.abs(B) < 9)
    s.put(eng, np.broadcast_to(C("a65a4c"), (N, N, 3)), 0.95)
    s.outline(dark=(60, 24, 24))
    return s


@pick("ocean_pick", "Ocean Pick", "RARE", "Smells a little like salt.")
def ocean_pick():
    s = Spr()
    m, sv = standard(s, "2fa8c8", "gem", handle_c=("e8dcc0", "d0c0a0"), wrap="2f7a9e", collar="f4f0e0", gemc="9fe6ff")
    wave = m & (np.abs(sv - 0.25 * np.sin(B * 1.2)) < 0.14)
    s.put(wave, np.broadcast_to(C("dff6ff"), (N, N, 3)), 1.0)
    s.put(blob(*at(3.6, -7), 0.9), np.broadcast_to(C("ff8fa8"), (N, N, 3)), 0.9)
    s.outline(dark=(10, 30, 50))
    return s


@pick("amethyst_pick", "Amethyst Pick", "RARE", "Hums when you swing it.")
def amethyst_pick():
    s = Spr()
    m, sv = standard(s, "9b6bff", "gem", handle_c=("3a2a4a", "2a1e36"), wrap="c39bff", collar="c9ced8", gemc="e0c8ff", gem_glow=11)
    for b, h in ((-7, 3.2), (-3, 4.2), (2, 3.6), (7, 2.8)):
        a0 = 1.2 - 0.034 * b * b + 2.4
        s.put(line_mask(at(a0, b), at(a0 + h, b + 0.4), 0.75), shade_head(mat_ramp("c39bff", "gem"), sv * 0, m | True), 0.8)
    s.outline(dark=(30, 14, 50))
    return s


# ------------------------------------------------------------------ epics

@pick("shadow_reaper", "Shadow Reaper", "EPIC", "Mines in the shadows.")
def shadow_reaper():
    s = Spr()
    handle(s, "2a2a33", "1c1c22", wrap="6a3aaa", collar="4a3a6a", pommel="8a3cff", pommel_glow=12)
    m, sv = crescent_mask(A0=0.6, K=0.05, T0=3.2, Bmax=13.5, p=1.4, skew=-0.18)
    m &= ~((B > 4.5) & (A < -1.5))
    s.put(m, shade_head(mat_ramp("2e2440", "metal"), sv, m), 0.85)
    edge = m & (sv > 0.62)
    s.put(edge, np.broadcast_to(C("b48cff"), (N, N, 3)), 0.9, 12)
    s.outline(dark=(8, 4, 14))
    return s


@pick("inferno_pick", "Inferno Pick", "EPIC", "Too hot to hold. Hold it anyway.")
def inferno_pick():
    s = Spr()
    m, sv = standard(s, "c8321e", "metal", handle_c=("2a1c18", "1c1210"), wrap="ff7a2a", collar="3a2a24", gemc="ffb12e", gem_glow=14)
    lava = m & (np.abs(sv - 0.1 * np.sin(B)) < 0.16)
    s.put(lava, np.broadcast_to(C("ffb12e"), (N, N, 3)), 1.0, 13)
    for b in (-10, -6, -2, 2, 6, 10):
        a0 = 1.2 - 0.034 * b * b + 2.6 * (1 - (abs(b) / 12.4) ** 1.7) + 0.4
        fl = line_mask(at(a0, b), at(a0 + 1.8, b - 0.6), 0.55)
        s.put(fl & ~s.a, np.broadcast_to(C("ffd24a"), (N, N, 3)), 0.4, 15)
    s.outline(dark=(40, 8, 4))
    return s


@pick("storm_hammer", "Storm Hammer", "EPIC", "Every swing a thunderclap.")
def storm_hammer():
    s = Spr()
    handle(s, "3a3e48", "2a2c34", wrap="41e0ff", collar="c9ced8", pommel="41e0ff", pommel_glow=12)
    m = (np.abs(B) <= 6.0) & (A >= -2.8) & (A <= 3.4)
    sv = (A - 0.3) / 3.1
    s.put(m, shade_head(mat_ramp("8a93a6", "metal"), sv, m), 1.0)
    rim = m & ((np.abs(B) > 5.0) | (A > 2.5) | (A < -1.9))
    s.put(rim, shade_head(mat_ramp("c9ced8", "metal"), sv, m), 1.05)
    bolt = (line_mask(at(2.6, -1.5), at(0.2, 0.6), 0.5) | line_mask(at(0.2, 0.6), at(0.6, -0.6), 0.5)
            | line_mask(at(0.6, -0.6), at(-2.0, 1.5), 0.5))
    s.put(bolt & m, np.broadcast_to(C("bff7ff"), (N, N, 3)), 1.15, 15)
    s.outline(dark=(10, 14, 22))
    return s


@pick("crystal_shard", "Crystal Shard", "EPIC", "Grown, not forged.")
def crystal_shard():
    s = Spr()
    m, sv = standard(s, "5fd3ff", "gem", handle_c=("c9f3ff", "9fe6ff"), wrap="2f7bff", collar="f4fbff", gemc="e9fbff", gem_glow=13)
    for b, h, w in ((-9, 3.5, 0.8), (-4, 5.2, 1.0), (1, 4.2, 0.9), (6, 3.0, 0.7), (10, 2.2, 0.6)):
        a0 = 1.2 - 0.034 * b * b + 2.0
        sh = line_mask(at(a0, b), at(a0 + h, b - 0.8), w)
        s.put(sh, shade_head(mat_ramp("9fe6ff", "gem"), np.full((N, N), 0.6), sh), 0.75)
        s.put(blob(*at(a0 + h * 0.8, b - 0.6), 0.45), np.broadcast_to(C("ffffff"), (N, N, 3)), 0.8, 12)
    s.outline(dark=(10, 30, 60))
    return s


@pick("venom_fang", "Venom Fang", "EPIC", "Two fangs, one bite.")
def venom_fang():
    s = Spr()
    handle(s, "2a3a22", "1e2a18", wrap="6dff4a", collar="d8d0b8", pommel="6dff4a", pommel_glow=12)
    m, sv = crescent_mask(A0=1.0, K=0.06, T0=3.0, Bmax=11.5, p=1.1, tip=0.25)
    s.put(m, shade_head(mat_ramp("ece4cc", "stone"), sv, m), 0.85)
    tips = m & (np.abs(B) > 7.5)
    s.put(tips, shade_head(np.broadcast_to(C("6dff4a"), (N, N, 3)), sv, m), 0.85, 10)
    s.put(blob(*at(0.8, 0), 1.7), np.broadcast_to(C("2a6a1a"), (N, N, 3)), 1.0)
    s.put(blob(*at(0.8, 0), 0.8), np.broadcast_to(C("b6ff6a"), (N, N, 3)), 1.1, 14)
    s.outline(dark=(8, 20, 6))
    return s


@pick("nebula_pick", "Nebula Pick", "EPIC", "A small galaxy on a stick.")
def nebula_pick():
    s = Spr()
    m, sv = standard(s, "3a1f6e", "gem", handle_c=("1c1430", "120c20"), wrap="c39bff", collar="8a3cff", gemc="ff6fd8", gem_glow=13)
    cloud = m & (hash3(np.floor(X / 3), np.floor(Y / 3), 1, 6) > 0.55)
    s.put(cloud, shade_head(np.broadcast_to(C("8a3cff"), (N, N, 3)), sv, m), s.d)
    stars = m & (hash3(np.floor(X), np.floor(Y), 7, 8) > 0.9)
    s.put(stars, np.broadcast_to(C("ffffff"), (N, N, 3)), 1.0, 13)
    s.outline(dark=(10, 4, 20))
    return s


# ------------------------------------------------------------------ legendaries

@pick("solar_cleaver", "Solar Cleaver", "LEGENDARY", "Burns like the sun.")
def solar_cleaver():
    s = Spr()
    handle(s, "f2c230", "c99312", wrap="d22d2d", collar="ffe066", pommel="ff8a1e", pommel_glow=13)
    bl = ((A / 7.2) ** 2 + ((-B - 1.0) / 10.0) ** 2 <= 1) & (-B >= 0.3)
    sv = np.clip(-B / 8.0, -1, 1) * 2 - 1
    s.put(bl, shade_head(mat_ramp("ffb12e", "metal"), sv, bl), 0.9, 6)
    s.put(bl & ((A / 7.2) ** 2 + ((-B - 1.0) / 10.0) ** 2 > 0.72), np.broadcast_to(C("fff3b0"), (N, N, 3)), 0.95, 14)
    sp = (B > 0) & (B < 6.5) & (np.abs(A) <= 1.4 - B * 0.2)
    s.put(sp, shade_head(mat_ramp("f2c230", "metal"), A / 1.4, sp), 0.8)
    s.put(blob(*at(0.2, -0.6), 1.6), np.broadcast_to(C("ffe066"), (N, N, 3)), 1.1, 15)
    s.outline(dark=(50, 20, 4))
    return s


@pick("comet_pick", "Comet Pick", "LEGENDARY", "Fell from the sky last night.")
def comet_pick():
    s = Spr()
    m, sv = standard(s, "2a3a6e", "gem", handle_c=("1c2440", "141a30"), wrap="7fb8ff", collar="c9d6ff")
    trail = m & (B < 5)
    tc = np.clip((B + 12) / 17, 0, 1)
    col = (C("1f2a5a")[None, None] * (1 - tc[..., None]) + C("9fd0ff")[None, None] * tc[..., None])
    s.put(trail, shade_head(col, sv, m), s.d)
    s.put(blob(*at(-0.6 - 0.034 * 64, 8.6), 2.0), np.broadcast_to(C("fff7d0"), (N, N, 3)), 1.15, 15)
    s.put(blob(*at(-0.6 - 0.034 * 64, 8.6), 1.1), np.broadcast_to(C("ffffff"), (N, N, 3)), 1.2, 15)
    stars = m & (hash3(np.floor(X), np.floor(Y), 3, 3) > 0.9)
    s.put(stars, np.broadcast_to(C("ffffff"), (N, N, 3)), 1.0, 12)
    s.outline(dark=(6, 10, 30))
    return s


@pick("dragonbone", "Dragonbone Pick", "LEGENDARY", "From a dragon nobody misses.")
def dragonbone():
    s = Spr()
    handle(s, "e8dcc0", "c9b896", wrap="6a1a1e", collar="3a2a20", pommel="d4183a", pommel_glow=10)
    m, sv = crescent_mask(A0=1.4, K=0.036, T0=2.8, Bmax=12.6, p=1.5, tip=0.3)
    s.put(m, shade_head(mat_ramp("ece4cc", "stone"), sv, m), 0.85)
    for b in (-9, -5, 5, 9):
        a0 = 1.4 - 0.036 * b * b + 2.6 * (1 - (abs(b) / 12.6) ** 1.5)
        s.put(line_mask(at(a0, b), at(a0 + 1.6, b), 0.45), np.broadcast_to(C("f6eee0"), (N, N, 3)), 0.7)
    sk = blob(*at(1.0, 0), 2.6)
    s.put(sk, shade_head(mat_ramp("ece4cc", "stone"), (A - 1.0) / 2.6, sk), 1.1)
    for b in (-1.1, 1.1):
        s.put(blob(*at(1.6, b), 0.6), np.broadcast_to(C("d4183a"), (N, N, 3)), 1.15, 14)
    s.outline(dark=(30, 20, 14))
    return s


@pick("abyssal_trident", "Abyssal Trident", "LEGENDARY", "Pulled up from the deep.")
def abyssal_trident():
    s = Spr()
    handle(s, "1f4a5a", "153a48", wrap="2fe0c8", collar="c9d6e0", pommel="2fe0c8", pommel_glow=12)
    col = mat_ramp("2fb5a0", "gem")
    prongs = (line_mask(at(-1.5, 0), at(8.5, 0), 0.85) |
              line_mask(at(-1.5, -4.0), at(-1.5, 4.0), 0.8) |
              line_mask(at(-1.5, -4.0), at(5.5, -4.2), 0.7) | line_mask(at(-1.5, 4.0), at(5.5, 4.2), 0.7))
    s.put(prongs, shade_head(col, np.clip(-B / 4, -1, 1) * 0.8, prongs), 0.8)
    for b, a in ((0, 8.5), (-4.2, 5.5), (4.2, 5.5)):
        tip = line_mask(at(a, b), at(a + 1.8, b), 0.55)
        s.put(tip, np.broadcast_to(C("9ffff0"), (N, N, 3)), 0.85, 12)
    s.put(blob(*at(-1.2, 0), 1.3), np.broadcast_to(C("2fe0c8"), (N, N, 3)), 1.05, 14)
    s.outline(dark=(4, 20, 24))
    return s


@pick("prism_pick", "Prism Pick", "LEGENDARY", "Splits the light in seven.")
def prism_pick():
    s = Spr()
    handle(s, "f4f6fa", "d8dce6", wrap="8a3cff", collar="ffffff", pommel="ff5fa8", pommel_glow=12)
    m, sv = crescent_mask()
    hue = np.clip((B + 12.4) / 24.8, 0, 1)
    cols = [C(c) for c in ("ff4f4f", "ff9a2a", "ffe14a", "4fe36b", "39c6ff", "4f6bff", "b14fff")]
    k = np.clip((hue * 6.999).astype(int), 0, 6)
    col = np.stack([c for c in cols])[k]
    s.put(m, shade_head(col, sv, m), 0.85 + 0.25 * (1 - np.abs(sv)), 8)
    s.put(blob(*at(0.6, 0), 1.6), np.broadcast_to(C("ffffff"), (N, N, 3)), 1.15, 15)
    s.outline(dark=(14, 14, 22))
    return s


# ------------------------------------------------------------------ mythics

@pick("thunder_god", "Thunder God Pick", "MYTHIC", "The king of the storm's own pick.")
def thunder_god():
    s = Spr()
    handle(s, "f2c230", "c99312", wrap="2f6bff", collar="fff3b8", pommel="41e0ff", pommel_glow=14)
    m, sv = crescent_mask(T0=2.9)
    s.put(m, shade_head(mat_ramp("f4f6fa", "metal"), sv, m), 0.9)
    s.put(m & (sv > 0.55), np.broadcast_to(C("f2c230"), (N, N, 3)), 0.95)
    for sgn in (-1, 1):
        for k in range(3):
            b = sgn * (8.5 + k * 1.3)
            a0 = 1.2 - 0.034 * b * b + 2.0
            fe = line_mask(at(a0, b), at(a0 + 2.6 - k * 0.5, b + sgn * 1.6), 0.55)
            s.put(fe & ~m, np.broadcast_to(C("fff3b8" if k % 2 else "f2c230"), (N, N, 3)), 0.55)
    bolt = (line_mask(at(3.4, -1.6), at(0.6, 0.8), 0.55) | line_mask(at(0.6, 0.8), at(1.2, -0.6), 0.55)
            | line_mask(at(1.2, -0.6), at(-2.2, 1.6), 0.55))
    s.put(bolt, np.broadcast_to(C("bff7ff"), (N, N, 3)), 1.2, 15)
    s.outline(dark=(20, 16, 4))
    return s


@pick("nexium_core", "Nexium Core Pick", "MYTHIC", "Mined out of the core itself.")
def nexium_core():
    s = Spr()
    handle(s, "1c2a2a", "142020", wrap="2fe0c8", collar="9ffff0", pommel="2fe0c8", pommel_glow=14)
    m, sv = crescent_mask(T0=2.8)
    s.put(m, shade_head(mat_ramp("1f8a7a", "gem"), sv, m), 0.9, 6)
    s.put(m & (np.abs(sv) < 0.18), np.broadcast_to(C("7fffe8"), (N, N, 3)), 1.0, 15)
    ring_ = np.abs(np.hypot((X - HC[0]) * 1.0, (Y - HC[1]) * 1.0) - 3.2) < 0.5
    s.put(ring_, np.broadcast_to(C("e0fffa"), (N, N, 3)), 1.05, 14)
    s.put(blob(HC[0], HC[1], 1.8), np.broadcast_to(C("2fe0c8"), (N, N, 3)), 1.25, 15)
    s.put(blob(HC[0] - 0.4, HC[1] - 0.4, 0.8), np.broadcast_to(C("ffffff"), (N, N, 3)), 1.3, 15)
    for b in (-11, 11):
        a0 = 1.2 - 0.034 * b * b + 1.5
        s.put(blob(*at(a0, b), 0.6), np.broadcast_to(C("9ffff0"), (N, N, 3)), 0.6, 13)
    s.outline(dark=(4, 20, 18))
    return s


# ------------------------------------------------------------------ build

HANDHELD = {
    "thirdperson_righthand": {"rotation": [0, -90, 55], "translation": [0, 4.0, 0.5], "scale": [0.85, 0.85, 0.85]},
    "thirdperson_lefthand": {"rotation": [0, 90, -55], "translation": [0, 4.0, 0.5], "scale": [0.85, 0.85, 0.85]},
    "firstperson_righthand": {"rotation": [0, -90, 25], "translation": [1.13, 3.2, 1.13], "scale": [0.68, 0.68, 0.68]},
    "firstperson_lefthand": {"rotation": [0, 90, -25], "translation": [1.13, 3.2, 1.13], "scale": [0.68, 0.68, 0.68]},
}


def build(pack, write_json, manifest):
    """Writes icons, 3D models and item definitions; returns [(name, icon)]."""
    out = []
    (pack / "textures/item/pick").mkdir(parents=True, exist_ok=True)
    for id, name, rarity, fn, text in PICKS:
        s = fn()
        icon = s.image()
        icon.save(pack / "textures/item/pick" / (id + ".png"), optimize=True)
        write_json(pack / "models/item/pick" / (id + "_icon.json"),
                   {"parent": "minecraft:item/handheld", "textures": {"layer0": "nexium:item/pick/" + id}})
        tid = "nexium:item/cos/pick/" + id
        m3, img = bake.export(s.model(id), tid)
        m3["display"] = HANDHELD
        tp = pack / "textures/item/cos/pick" / (id + ".png")
        tp.parent.mkdir(parents=True, exist_ok=True)
        img.save(tp, optimize=True)
        write_json(pack / "models/item/pick" / (id + ".json"), m3)
        write_json(pack / "items/pick" / (id + ".json"), {"model": {
            "type": "minecraft:select", "property": "minecraft:display_context",
            "cases": [{"when": ["gui", "ground", "fixed"],
                       "model": {"type": "minecraft:model", "model": "nexium:item/pick/%s_icon" % id}}],
            "fallback": {"type": "minecraft:model", "model": "nexium:item/pick/" + id}}})
        manifest.append({"kind": "pick", "id": id, "name": name, "rarity": rarity, "text": text})
        out.append((name, icon))
    return out
