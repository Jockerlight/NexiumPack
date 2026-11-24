"""The 8 outfits in HD: a head piece (hat space), a back piece (back space)
and armour textures at 4x (256x128, Minecraft scales them onto the normal
armour model): chestplate + boots on the humanoid layer, leggings on the
humanoid_leggings layer (equipment asset nexium:<id>)."""
import math

import numpy as np
from PIL import Image

from parts import *  # noqa: F401,F403
from hd import Shape
from wings import (back_model, wing_pair, feather_wing, membrane_wing, blade_wing, shard_wing, leaf_wing, ROOT_Y,
                   ROOT_Z)
from backs import cape, mount

OUTFITS = []
ARMOR = {}   # id -> (humanoid image, humanoid_leggings image)
S = 4        # texture scale (4 = 256x128)


def outfit(id, name, rarity):
    def deco(fn):
        OUTFITS.append((id, name, rarity, fn))
        return fn
    return deco


# ------------------------------------------------------------ armour painting
BODY = {"top": (20, 16, 8, 4), "bottom": (28, 16, 8, 4), "right": (16, 20, 4, 12),
        "front": (20, 20, 8, 12), "left": (28, 20, 4, 12), "back": (32, 20, 8, 12)}
ARM = {"top": (44, 16, 4, 4), "bottom": (48, 16, 4, 4), "right": (40, 20, 4, 12),
       "front": (44, 20, 4, 12), "left": (48, 20, 4, 12), "back": (52, 20, 4, 12)}
LEG = {"top": (4, 16, 4, 4), "bottom": (8, 16, 4, 4), "right": (0, 20, 4, 12),
       "front": (4, 20, 4, 12), "left": (8, 20, 4, 12), "back": (12, 20, 4, 12)}


def _c(h):
    return np.array(C(h), float)


class Theme:
    """A plate armour look; deco(part, face, U, V, w, h, col) can add motifs."""

    def __init__(self, base, dark, light, trim, glow=None, band=3.0, rivet=None, noise=0.05, seam_glow=False,
                 emblem=None, cracks=None, sparkle=None, deco=None, boot=None, boot_dark=None):
        self.base, self.dark, self.light, self.trim = _c(base), _c(dark), _c(light), _c(trim)
        self.glow = _c(glow) if glow else None
        self.band = band
        self.rivet = _c(rivet) if rivet else None
        self.noise = noise
        self.seam_glow = seam_glow
        self.emblem = emblem
        self.cracks = _c(cracks) if cracks else None
        self.sparkle = _c(sparkle) if sparkle else None
        self.deco = deco
        self.boot = _c(boot) if boot else self.dark
        self.boot_dark = _c(boot_dark) if boot_dark else self.dark * 0.7

    def plates(self, part, face, U, V, w, h):
        if face in ("top", "bottom"):
            col = np.broadcast_to(self.dark * (0.9 if face == "top" else 0.7), U.shape + (3,)).copy()
            return col
        t = (V / self.band) % 1.0
        col = self.base[None, None] * np.ones(U.shape + (1,))
        col = np.where((t < 0.14)[..., None], self.light, col)
        col = np.where((t > 0.78)[..., None], self.base * 0.78 + self.dark * 0.22, col)
        col = np.where((t > 0.92)[..., None], self.dark, col)
        # bevel at the face edges
        edge = (U < 0.26) | (U > w - 0.26)
        col = np.where(edge[..., None], self.dark, col)
        if face in ("left", "right"):
            col = col * 0.86
        # trim: shoulders / cuffs
        if part == "body":
            col = np.where((V < 0.5)[..., None], self.trim, col)
        if part == "arm":
            col = np.where(((V > h - 1.0) & (V < h - 0.25))[..., None], self.trim, col)
            col = np.where((V < 0.75)[..., None], self.trim, col)
        if part == "legs":
            col = np.where((V < 0.6)[..., None], self.trim, col)
        if self.rivet is not None:
            ru = (U % 2.0) - 1.0
            rv = (V % self.band) - 0.55
            col = np.where((ru * ru + rv * rv < 0.07)[..., None] & ~edge[..., None], self.rivet, col)
        if self.glow is not None and self.seam_glow and face in ("front", "back") and w >= 8:
            col = np.where((np.abs(U - w / 2) < 0.22)[..., None] & (t > 0.18)[..., None], self.glow, col)
        if self.cracks is not None:
            n = _vn(U * 0.9 + (0 if part == "body" else 7), V * 0.6 + len(face), 3)
            col = np.where((np.abs(n - 0.5) < 0.035)[..., None], self.cracks, col)
        if self.sparkle is not None:
            hsh = _hash(np.floor(U * S), np.floor(V * S), len(face) + 13 * len(part))
            col = np.where((hsh > 0.985)[..., None], self.sparkle, col)
        n = _hash(np.floor(U * S), np.floor(V * S), 5 + len(face))
        col = col * (1 - self.noise / 2 + self.noise * n[..., None])
        if part == "body" and face == "front" and self.emblem is not None:
            col = self.emblem(U, V, col)
        if self.deco is not None:
            col = self.deco(part, face, U, V, w, h, col)
        return col

    def boots(self, face, U, V, w, h, rows=4.5):
        if face == "top":
            return None
        if face == "bottom":
            return np.broadcast_to(self.boot_dark, U.shape + (3,)).copy(), np.ones(U.shape, bool)
        m = V >= h - rows
        col = self.boot[None, None] * np.ones(U.shape + (1,))
        t = V - (h - rows)
        col = np.where((t < 0.5)[..., None], self.trim, col)
        col = np.where((V > h - 0.55)[..., None], self.boot_dark, col)
        if face == "front":
            col = np.where(((V > h - 1.9) & (V < h - 0.55))[..., None], self.light * 0.8 + self.boot * 0.2, col)
        if self.glow is not None:
            col = np.where(((V > h - 0.9) & (V < h - 0.6) & ((U % 1.0) < 0.5))[..., None], self.glow, col)
        n = _hash(np.floor(U * S), np.floor(V * S), 9 + len(face))
        col = col * (1 - self.noise / 2 + self.noise * n[..., None])
        return col, m


def _hash(i, j, seed):
    h = (np.asarray(i, np.int64) * 73856093) ^ (np.asarray(j, np.int64) * 19349663) ^ (seed * 83492791)
    h = h & 0xFFFFFFFF
    h = (h ^ (h >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65536.0


def _vn(x, y, seed):
    xi, yi = np.floor(x), np.floor(y)
    xf, yf = x - xi, y - yi
    u, v = xf * xf * (3 - 2 * xf), yf * yf * (3 - 2 * yf)
    a = _hash(xi, yi, seed)
    b = _hash(xi + 1, yi, seed)
    c = _hash(xi, yi + 1, seed)
    d = _hash(xi + 1, yi + 1, seed)
    return a * (1 - u) * (1 - v) + b * u * (1 - v) + c * (1 - u) * v + d * u * v


def _paint(img, region, fn):
    for face, (x0, y0, w, h) in region.items():
        j, i = np.meshgrid(np.arange(h * S), np.arange(w * S), indexing="ij")
        U = (i + 0.5) / S
        V = (j + 0.5) / S
        out = fn(face, U, V, w, h)
        if out is None:
            continue
        if isinstance(out, tuple):
            col, mask = out
        else:
            col, mask = out, np.ones(U.shape, bool)
        sub = img[y0 * S:(y0 + h) * S, x0 * S:(x0 + w) * S]
        sub[mask, :3] = np.clip(col[mask], 0, 255)
        sub[mask, 3] = 255


def armor(id, theme, legs_theme=None):
    hum = np.zeros((32 * S, 64 * S, 4), np.float64)
    leg = np.zeros((32 * S, 64 * S, 4), np.float64)
    lt = legs_theme or theme
    _paint(hum, BODY, lambda f, U, V, w, h: theme.plates("body", f, U, V, w, h))
    _paint(hum, ARM, lambda f, U, V, w, h: theme.plates("arm", f, U, V, w, h))
    _paint(hum, LEG, lambda f, U, V, w, h: theme.boots(f, U, V, w, h))
    _paint(leg, LEG, lambda f, U, V, w, h: lt.plates("legs", f, U, V, w, h))
    ARMOR[id] = (Image.fromarray(hum.astype(np.uint8), "RGBA"), Image.fromarray(leg.astype(np.uint8), "RGBA"))


def emblem_mask(fn_mask, colour, outline=None, cx=4.0, cy=4.2):
    """Chest emblem: fn_mask(x, y) with (0, 0) at the emblem centre."""
    c = _c(colour)
    o = _c(outline) if outline else None

    def em(U, V, col):
        x, y = U - cx, V - cy
        m = fn_mask(x, y)
        if o is not None:
            mo = fn_mask(x * 0.85, y * 0.85) | fn_mask(x - 0.25, y) | fn_mask(x + 0.25, y) | fn_mask(x, y - 0.25) | fn_mask(x, y + 0.25)
            col = np.where((mo & ~m)[..., None], o, col)
        return np.where(m[..., None], c, col)
    return em


def diamond(r):
    return lambda x, y: np.abs(x) + np.abs(y) < r


def circle(r, r_in=0.0):
    return lambda x, y: (x * x + y * y < r * r) & (x * x + y * y >= r_in * r_in)


def chain(*ems):
    def em(U, V, col):
        for e in ems:
            col = e(U, V, col)
        return col
    return em


# ------------------------------------------------------------ head / back helpers

def helm(m, base, dark, top=14.6, r=1.6):
    m.fill(helmet_shell(2.5, 3.2, 2.5, 13.5, top, 13.5, r), base)
    m.paint(box(0, 3.2, 0, 16, 3.9, 16), dark)


def visor_slit(m, y, colour, w=7.0, h=0.7, lvl=15):
    m.carve(box(8 - w / 2, y, 2.0, 8 + w / 2, y + h, 3.2))
    m.fill(box(8 - w / 2, y, 2.9, 8 + w / 2, y + h, 3.2), glow(colour, lvl))


# ------------------------------------------------------------ the outfits

@outfit("demon_lord", "Demon Lord", "MYTHIC")
def demon_lord():
    head = hat_model("demon_lord_head")
    R = metal("6a1218", brushed="y")
    helm(head, R, solid("1c1012"))
    head.paint(box(7.4, 3, 0, 8.6, 16, 16), solid("1c1012"))
    for sx in (-1, 1):
        head.carve(prism([(-1.3, -0.4), (1.3, -0.4), (0.9, 0.5), (-1.1, 0.4)], "z", 2.0, 3.2).move(8 + sx * 2.2, 9.6, 0))
        head.fill(prism([(-1.3, -0.4), (1.3, -0.4), (0.9, 0.5), (-1.1, 0.4)], "z", 2.9, 3.2).move(8 + sx * 2.2, 9.6, 0), glow("ff6a1e", 15))
        pts = bezier((8 + sx * 5.4, 12.0, 7.5), (8 + sx * 8.4, 13.0, 7.5), (8 + sx * 8.4, 17.5, 6.5), (8 + sx * 6.0, 20.0, 5.0), n=14)
        horn(head, pts, 1.3, 0.2, solid("1c1012", 0.4), solid("3a1a1e"), 1.1)
        head.paint(tube(pts[10:], 0.6, 0.25), solid("c8323a", 0.4))
    for x in (5.8, 8.0, 10.2):
        head.fill(cone(x, 4.0, 0.5, 14.2, 1.6 if x == 8 else 1.1, r1=0.05), solid("1c1012", 0.4))
    head.fill(prism([(-1.5, 0), (1.5, 0), (0, -2.0)], "z", 2.3, 2.6).move(8, 7.2, 0), solid("1c1012"))
    for k in range(6):
        head.fill(box(5.6 + k * 0.8, 4.0, 2.25, 5.9 + k * 0.8, 5.6, 2.6), solid("e6dfd0", 0.3))
    back = back_model("demon_lord_back")
    wing_pair(back, lambda p, r: membrane_wing(p, r, 17, 17, "7a1418", "c8323a", "1c1012", "ff8a1e", 4, glow_vein="ff6a1e"),
              22.5, outline_col="12060a")
    mount(back, solid("1c1012"), "ff6a1e")
    armor("demon_lord", Theme("7a1a20", "2a0a0e", "b8323a", "1c1012", glow="ff6a1e", cracks="ff7a2a", rivet="3a1a1e",
                              emblem=emblem_mask(lambda x, y: (np.abs(x) < 1.6) & (np.abs(y + 0.2) < 1.2) & ~((np.abs(x) - 0.75) ** 2 + (y + 0.2) ** 2 < 0.12)
                                                 | ((np.abs(x) - 1.3) ** 2 + (y + 1.6) ** 2 < 0.2), "1c1012", "ff6a1e"),
                              boot="2a0a0e", boot_dark="12060a"))
    return head, back


@outfit("shadow_knight", "Shadow Knight", "LEGENDARY")
def shadow_knight():
    head = hat_model("shadow_knight_head")
    St = gold(tones=["0e1014", "181b22", "22262e", "2e333d", "3e4450", "5a6474", "8a94a8"])
    helm(head, St, metal("14161c"), 14.8, 1.4)
    head.fill(rbox(7.3, 13.6, 2.3, 8.7, 16.8, 13.7, 0.5), St)
    visor_slit(head, 9.4, "41e0ff", 7.4, 0.6)
    head.carve(box(7.75, 5.0, 2.0, 8.25, 9.4, 3.2))
    head.fill(box(7.75, 5.0, 2.9, 8.25, 9.4, 3.2), glow("41e0ff", 13))
    for y in (6.0, 7.2):
        for x in (5.2, 10.4):
            head.carve(box(x, y, 2.0, x + 0.5, y + 0.25, 3.2))
    for sx in (-1, 1):
        head.fill(cone(8 + sx * 5.4, 8.0, 0.55, 12.0, 3.0, r1=0.05, lean=(sx * 1.6, 0)), St)
    head.paint(head_band(12.8, 13.1, 1.6, 0.4), glow("41e0ff", 12))
    back = back_model("shadow_knight_back")
    wing_pair(back, lambda p, r: feather_wing(p, r, 16, 16, "1c1e26", "2a2e38", "3a4050", "41e0ff", "101218", "22262e", n=12),
              22.5, outline_col="05060a")
    mount(back, St, "41e0ff")
    armor("shadow_knight", Theme("22262e", "101218", "3a404c", "5a6474", glow="41e0ff", seam_glow=True, rivet="6a7488",
                                 emblem=emblem_mask(diamond(1.7), "41e0ff", "101218"), boot="1a1d24", boot_dark="0a0b0e"))
    return head, back


@outfit("seraph", "Seraph", "MYTHIC")
def seraph():
    head = hat_model("seraph_head")
    Wt = solid("f4f2ea", 0.5, soft=1)
    G = gold()
    helm(head, Wt, G, 14.4, 1.8)
    head.paint(box(7.4, 3, 0, 8.6, 15, 3.0) | box(3.0, 11.4, 0, 13.0, 12.1, 3.0), G)
    visor_slit(head, 9.0, "fff7c8", 6.0, 0.55, 13)
    set_gem(head, (8, 12.9, 2.3), "-z", 0.55, "4fa8ff", G)
    head.fill(torus(8, 17.0, 8, 3.6, 0.45), glow("ffd54a", 15, core="fff7c8"))
    for sx in (-1, 1):
        for k in range(3):
            y = 9.5 + k * 1.3
            head.fill(ellipsoid(8 + sx * (5.9 + k * 0.5), y, 8.6 + k * 0.4, 0.35, 0.45, 1.6 - k * 0.2).rot("x", 20, (8, y, 8)), solid("ffffff", 0.3))
    back = back_model("seraph_back")
    wing_pair(back, lambda p, r: feather_wing(p, r, 17, 17, "f4f6fa", "e6ebf3", "ffffff", "e0b13a", "c9a040", "f4f6fa", n=13,
                                            acc=gold()), 22.5, outline_col="2a2416")
    mount(back, gold(), "4fa8ff")
    armor("seraph", Theme("f2efe4", "b9b2a0", "ffffff", "f2c230", glow="4fa8ff", rivet="f2c230",
                          emblem=chain(emblem_mask(lambda x, y: (np.abs(x) < 0.35) | (np.abs(y + 0.4) < 0.35) & (np.abs(x) < 1.6), "f2c230", "a87a14"),
                                       emblem_mask(circle(0.55), "4fa8ff", None, 4.0, 3.8)),
                          boot="e6e1d2", boot_dark="a89e84"))
    return head, back


@outfit("frost_warden", "Frost Warden", "LEGENDARY")
def frost_warden():
    head = hat_model("frost_warden_head")
    ice = crystal("8fd3ff")
    helm(head, crystal("6cc0f0"), solid("f4fbff", 0.4), 14.2, 1.6)
    visor_slit(head, 9.2, "e9fbff", 7.0, 0.6, 12)
    import random
    rnd = random.Random(8)
    for p in square_points(5.3, 1.4, 14.0):
        h = rnd.uniform(1.4, 3.6)
        head.fill(cone(p[0], p[2], 0.55, 14.0, h, r1=0.05), ice)
    for d in SIDES:
        head.fill(around(cone(8, 2.6, 0.9, 14.0, 4.8, r1=0.05), d), crystal("c9f3ff"))
    head.fill(sphere(8, 12.6, 2.4, 0.55), glow("5fd3ff", 14))
    back = back_model("frost_warden_back")
    wing_pair(back, lambda p, r: shard_wing(p, r, 9, 6.0, 15.0, "9fe6ff", "f4fdff"), 22.5, outline_col="0e2a40")
    mount(back, crystal("bfe9ff"), "9fe6ff")

    def flake(x, y):
        r = np.hypot(x, y)
        a = np.arctan2(y, x)
        arms = np.abs(np.sin(3 * a)) < 0.18
        return (r < 1.9) & (arms | (r < 0.4))
    armor("frost_warden", Theme("8fd3ff", "3a86c0", "dff6ff", "f4fbff", glow="e9fbff", sparkle="ffffff", rivet="f4fbff",
                                emblem=emblem_mask(flake, "f4fdff", "3a86c0"), boot="5aa8d8", boot_dark="2a5f8a"))
    return head, back


@outfit("void_walker", "Void Walker", "MYTHIC")
def void_walker():
    head = hat_model("void_walker_head")
    V = velvet("1a1226")
    hood = helmet_shell(2.3, 2.8, 2.3, 13.7, 15.0, 13.7, 3.0)
    head.fill(hood, V)
    head.fill(cone(8, 11.0, 2.4, 14.4, 3.0, r1=0.3, lean=(0, 2.5)), V)
    head.carve(rbox(3.6, 4.0, 1.5, 12.4, 11.6, 3.4, 1.4))
    head.fill(rbox(3.6, 4.0, 3.2, 12.4, 11.6, 3.45, 1.4), solid("06040a", 0.1))
    for sx in (-1, 1):
        head.fill(ellipsoid(8 + sx * 1.6, 8.6, 3.15, 0.75, 0.42, 0.15), glow("b15cff", 15, core="f0e0ff"))
    head.paint(helmet_shell(2.2, 2.8, 2.2, 13.8, 15.1, 13.8, 3.0) & box(0, 2.8, 0, 16, 3.5, 16), glow("8a3cff", 12))
    head.fill(torus(8, 16.8, 8, 3.2, 0.25), glow("8a3cff", 14))
    back = back_model("void_walker_back")
    cape(back, velvet("150e20"), glow("8a3cff", 12), rod=crystal("2a1745"))
    for k in range(14):
        x = 4.0 + (k * 37 % 80) / 10.0
        y = 2.5 + (k * 53 % 110) / 10.0
        back.paint(sphere(x, y, 4.0, 0.22), glow("f0e0ff", 13))
    armor("void_walker", Theme("1a1226", "0c0814", "3a2a5a", "8a3cff", glow="b15cff", seam_glow=True, sparkle="f0e0ff",
                               emblem=emblem_mask(lambda x, y: (x * x / 2.6 + y * y / 0.9 < 1) & ~(x * x + y * y < 0.3) | (x * x + y * y < 0.12),
                                                  "b15cff", "0c0814"), boot="120c1c", boot_dark="06040a"))
    return head, back


@outfit("jungle_spirit", "Jungle Spirit", "LEGENDARY")
def jungle_spirit():
    head = hat_model("jungle_spirit_head")
    Wd = wood("8a5a34")
    head.fill(rbox(3.0, 3.6, 2.4, 13.0, 13.4, 3.6, 1.4), Wd)
    head.fill(head_band(10.4, 12.8, 1.0, 0.5), solid("3f8a3a", 0.6, soft=1))
    for sx in (-1, 1):
        head.fill(prism([(-1.2, -0.5), (1.2, -0.5), (0.8, 0.5), (-0.8, 0.5)], "z", 2.2, 2.5).move(8 + sx * 2.2, 9.2, 0), glow("b6ff6a", 14))
        pts = bezier((8 + sx * 3.4, 13.2, 6.5), (8 + sx * 5.4, 16.0, 6.5), (8 + sx * 6.2, 18.8, 7.5), n=10)
        head.fill(tube(pts, 0.42, 0.18), wood("c9a46a"))
        for t in (0.45, 0.75):
            q = pts[int(t * 10)]
            head.fill(tube([q, (q[0] + sx * 1.5, q[1] + 1.4, q[2])], 0.25, 0.1), wood("c9a46a"))
    for k in range(12):
        a = 2 * math.pi * k / 12
        leaf(head, (8 + math.cos(a) * 5.2, 12.2, 8 + math.sin(a) * 5.2), 1.6, 0.5, math.degrees(a), solid("4fae45", 0.5), 0.6)
    for x in (5.2, 10.8):
        flower(head, (x, 12.5, 3.0), "ff6fa0", 5, 0.8, "ffd54a", axis="z")
    head.fill(prism([(-0.4, 0.6), (0.4, 0.6), (0, -1.4)], "z", 2.2, 2.6).move(8, 6.4, 0), Wd)
    back = back_model("jungle_spirit_back")
    wing_pair(back, lambda p, r: leaf_wing(p, r, 6, 8.0, 14.0), 22.5, outline_col="0f2410")
    back.fill(tube([(8, ROOT_Y - 3, 4.6), (8, ROOT_Y + 1.5, 4.6)], 0.9, 0.7), wood("6b4a2a"))

    def deco(part, face, U, V, w, h, col):
        n = _vn(U * 1.3 + len(face), V * 0.7, 21)
        vine = np.abs(n - 0.5) < 0.06
        return np.where(vine[..., None], np.array([70.0, 150.0, 60.0]), col)
    armor("jungle_spirit", Theme("7a5232", "3e2616", "a8784a", "4fae45", glow="b6ff6a", rivet="c9a46a", deco=deco,
                                 emblem=emblem_mask(lambda x, y: (x * x / 0.8 + (y + 0.2) ** 2 / 3.2 < 1), "4fae45", "2a5a1e"),
                                 boot="5a3a22", boot_dark="2a1a10"))
    return head, back


@outfit("neon_mech", "Neon Mech", "LEGENDARY")
def neon_mech():
    head = hat_model("neon_mech_head")
    K = metal("2a2c36", brushed="x")
    helm(head, K, metal("15161c"), 14.2, 1.2)
    head.carve(rbox(3.4, 7.8, 1.8, 12.6, 10.8, 3.2, 0.5))
    head.fill(rbox(3.4, 7.8, 2.85, 12.6, 10.8, 3.2, 0.5), glow("ff4fd8", 15, core="ffd2f6"))
    head.paint(box(3, 9.15, 2, 13, 9.45, 3.3), glow("ffffff", 15))
    for sx in (-1, 1):
        head.fill(cyl_x(8.6, 8, 1.6, min(8 + sx * 5.5, 8 + sx * 6.3), max(8 + sx * 5.5, 8 + sx * 6.3)), metal("4a4f5c"))
        head.fill(cyl_x(8.6, 8, 1.0, min(8 + sx * 6.3, 8 + sx * 6.5), max(8 + sx * 6.3, 8 + sx * 6.5)), glow("39e1ff", 15))
    head.fill(cyl(10.6, 9.0, 0.18, 14.0, 17.2), silver())
    head.fill(sphere(10.6, 17.4, 9.0, 0.45), glow("39e1ff", 15))
    head.paint(box(7.6, 11.6, 0, 8.4, 16, 16), glow("39e1ff", 11))
    back = back_model("neon_mech_back")
    wing_pair(back, lambda p, r: blade_wing(p, r, 6, 7.5, 14.0, 2.0, "4a4f5c", "1f2028", "ff4fd8"), 22.5, outline_col="0a0a10")
    back.fill(rbox(6.0, ROOT_Y - 4.0, 3.4, 10.0, ROOT_Y + 1.6, 5.6, 0.6), metal("2a2c36"))
    back.fill(cyl_z(8, ROOT_Y - 1.2, 1.2, 3.1, 3.5), glow("39e1ff", 15, core="e0fbff"))

    def circuits(part, face, U, V, w, h, col):
        a = (np.abs((U * 2 + np.floor(V)) % 3 - 1.5) < 0.12) & ((np.floor(V * 2) % 5) == 1)
        b = (np.abs(U - (np.floor(U) + 0.5)) < 0.1) & ((np.floor(U) % 3) == 1) & ((V % 6) < 3)
        col = np.where(a[..., None], np.array([255.0, 79, 216]), col)
        return np.where(b[..., None], np.array([57.0, 225, 255]), col)
    armor("neon_mech", Theme("2a2c36", "15161c", "4a4f5c", "8a909c", glow="ff4fd8", deco=circuits, rivet="8a909c",
                             emblem=emblem_mask(circle(1.6, 1.0), "39e1ff", "15161c"), boot="22232c", boot_dark="0c0c10"))
    return head, back


@outfit("golden_emperor", "Golden Emperor", "MYTHIC")
def golden_emperor():
    head = hat_model("golden_emperor_head")
    G = gold()
    helm(head, G, gold(tones=["5a3008", "8a5010", "b8741a", "dc9b22", "f2bb2e", "ffd54a", "ffec94"]), 14.2, 1.4)
    visor_slit(head, 9.2, "fff1a8", 6.6, 0.5, 12)
    head.paint(box(3, 3.2, 0, 13, 3.9, 16), velvet("8c0f2e"))
    head.fill(head_band(14.0, 15.6, 0.9, 0.3), G)
    fl = prism([(-0.9, 0), (0.9, 0), (0.45, 1.1), (0.8, 2.0), (0.25, 1.85), (0, 2.8), (-0.25, 1.85), (-0.8, 2.0), (-0.45, 1.1)], "z", -0.25, 0.25)
    for d in SIDES:
        head.fill(around(fl.move(8, 15.5, 2.8), d), G)
        head.fill(around(fl.move(4.6, 15.5, 2.8), d), G)
        set_gem(head, (8, 14.8, 2.55), "-z", 0.5, ["c0102f", "1f7bff", "1fbf5f", "a03cff"][d // 90], G)
    head.fill(dome(8, 8, 4.2, 14.4, 2.6), velvet("8c0f2e"))
    head.fill(sphere(8, 17.4, 8, 0.7), G)
    for sx in (-1, 1):
        for k in range(5):
            y = 6.0 + k * 1.2
            leaf(head, (8 + sx * 5.7, y, 3.6 + k * 0.4), 1.2, 0.42, 90 + sx * 60, gold(seed=k), 0.5)
    back = back_model("golden_emperor_back")
    cape(back, velvet("8c0f2e"), gold(), rod=gold())
    back.fill(prism([(-1.8, 1.6), (1.8, 1.6), (1.8, -0.4), (0, -2.2), (-1.8, -0.4)], "z", 3.4, 3.8).move(8, 8.2, 0), gold())
    back.fill(prism(star_points(0, 0, 1.0, 0.4), "z", 3.2, 3.45).move(8, 8.3, 0), velvet("1f3f9e"))
    for x in (3.6, 12.4):
        back.fill(rbox(x - 1.4, 13.2, 3.8, x + 1.4, 14.6, 5.7, 0.6), G)
        for k in range(5):
            back.fill(capsule((x - 1.1 + k * 0.55, 13.2, 4.4), (x - 1.1 + k * 0.55, 11.6, 4.4), 0.14), G)
    armor("golden_emperor", Theme("f2bb2e", "a8640f", "ffec94", "8c0f2e", glow="ff4f6d", rivet="fff3b8", sparkle="ffffff",
                                  emblem=chain(emblem_mask(lambda x, y: (np.abs(y + 0.3) < 1.0) & (np.abs(x) < 1.7) & ~((np.abs(x) < 1.1) & (y < -0.4)),
                                                          "8c0f2e", "5a3008"),
                                               emblem_mask(circle(0.5), "1f7bff", None, 4.0, 4.0)),
                                  boot="c48a1c", boot_dark="6e3d0a"),
          Theme("8c0f2e", "4a0818", "c8283a", "f2bb2e", rivet="f2bb2e"))
    return head, back
