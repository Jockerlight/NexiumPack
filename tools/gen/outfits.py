"""The 8 outfits: a head piece (worn like a hat), armor textures for the
chestplate / leggings / boots (equipment asset nexium:<id>) and a back piece
(wings or a cape)."""
import math
from PIL import Image
from vox import Vox, shade, mix
from shapes import C, sq_ring, slab, dome, cone, circle_pts, noise
import sprite as S
from backs import wings, cape_plane

OUTFITS = []
ARMOR = {}  # id -> (humanoid image, humanoid_leggings image)


def outfit(id, name, rarity):
    def deco(fn):
        OUTFITS.append((id, name, rarity, fn))
        return fn
    return deco


# ---------------------------------------------------------------- armor painting
# 64x32 armor layout: (x, y, w, h) of each face
BODY = {"top": (20, 16, 8, 4), "bottom": (28, 16, 8, 4), "right": (16, 20, 4, 12),
        "front": (20, 20, 8, 12), "left": (28, 20, 4, 12), "back": (32, 20, 8, 12)}
ARM = {"top": (44, 16, 4, 4), "bottom": (48, 16, 4, 4), "right": (40, 20, 4, 12),
       "front": (44, 20, 4, 12), "left": (48, 20, 4, 12), "back": (52, 20, 4, 12)}
LEG = {"top": (4, 16, 4, 4), "bottom": (8, 16, 4, 4), "right": (0, 20, 4, 12),
       "front": (4, 20, 4, 12), "left": (8, 20, 4, 12), "back": (12, 20, 4, 12)}


def paint(im, region, fn):
    for face, (x0, y0, w, h) in region.items():
        for v in range(h):
            for u in range(w):
                c = fn(face, u, v, w, h)
                if c is not None:
                    im.putpixel((x0 + u, y0 + v), tuple(c[:3]) + (255,))


def armor(id, body, arm, legs, boots, legs_body=None):
    """body/arm/legs/boots: fn(face, u, v, w, h) -> colour or None."""
    hum = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    leg = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    paint(hum, BODY, body)
    paint(hum, ARM, arm)
    paint(hum, LEG, boots)
    paint(leg, LEG, legs)
    if legs_body:
        paint(leg, BODY, legs_body)
    ARMOR[id] = (hum, leg)


def plated(base, dark, light, accent=None, glow=None, band=3, seam=True, sparkle=None, belt=None):
    """A generic plate armour: bands of plates with a light top edge, darker
    sides, an optional glowing seam down the middle and sparkles."""
    def fn(face, u, v, w, h):
        if face in ("top", "bottom"):
            return dark
        c = base
        if v % band == 0:
            c = light
        elif v % band == band - 1:
            c = dark
        if face in ("right", "left"):
            c = shade(c, 0.85)
        if u in (0, w - 1) and face in ("front", "back"):
            c = dark
        if glow and seam and face in ("front", "back") and w >= 8 and u in (w // 2 - 1, w // 2) and v % band != 0:
            c = glow
        if accent and face == "front" and w >= 8 and 2 <= v <= 4 and 2 <= u <= w - 3 and (u + v) % 2 == 0:
            c = accent
        if belt and face in ("front", "back", "left", "right") and v in (h - 2, h - 1) and h == 12 and w >= 4:
            c = belt
        if sparkle and (u * 7 + v * 13 + len(face)) % 11 == 0:
            c = sparkle
        return c
    return fn


def boots_of(base, dark, glow=None, rows=4):
    def fn(face, u, v, w, h):
        if face == "top":
            return None
        if face == "bottom":
            return dark
        if v < h - rows:
            return None
        c = base if v > h - rows else dark
        if glow and v == h - 1 and u % 2 == 0:
            c = glow
        return c
    return fn


def outfit_head_shell(v, base, dark, front=None):
    """A helmet around the whole head (3..13), open at the bottom."""
    v.frame(3, 3, 3, 13, 13, 13, base)
    v.box(4, 3, 4, 12, 4, 12, None)
    sq_ring(v, 3, 3, 13, 13, 3, 4, dark)
    if front:
        for j, row in enumerate(front):
            for i, ch in enumerate(row):
                c = front_legend.get(ch)
                if c:
                    v.set(3 + i, 12 - j, 3, c)


front_legend = {}


def face(rows, legend):
    front_legend.clear()
    front_legend.update(legend)
    return rows


# ---------------------------------------------------------------- the outfits
@outfit("demon_lord", "Demon Lord", "MYTHIC")
def demon_lord():
    red, dark, black, lava, yel, horn, tipc = C("6a1218"), C("3a0a0e"), C("1c1012"), C("ff6a1e"), C("ffd24a"), C("2a1e22"), C("c8323a")
    head = Vox("demon_lord_head")
    rows = face(["..........",
                 "..........",
                 ".BBBBBBBB.",
                 ".BOO..OOB.",
                 ".BBBBBBBB.",
                 "....LL....",
                 "..B.LL.B..",
                 "..BBBBBB..",
                 "..........",
                 ".........."], {"B": black, "O": lava, "L": lava})
    outfit_head_shell(head, red, black, rows)
    for s in (-1, 1):
        x = 3 if s < 0 else 12
        pts = [(x, 12, 6), (x + s * 2, 14, 6), (x + s * 3, 17, 6), (x + s * 2, 20, 6), (x + s * 0.5, 22, 6)]
        for i in range(len(pts) - 1):
            head.line(pts[i], pts[i + 1], horn if i < 2 else tipc, r=max(0.0, 1.1 - i * 0.3))
    back = Vox("demon_lord_back")
    tex = S.membrane_wing("wing_demon", C("8a1a1e"), C("b8281e"), C("2a1012"), claw=C("ff8a1e"))
    wings(back, tex, W=16, H=17)
    back.box(7, 9, 4, 9, 13, 6, black)
    armor("demon_lord",
          plated(red, black, shade(red, 1.25), glow=lava, belt=black),
          plated(red, black, shade(red, 1.2), glow=None),
          plated(dark, black, red, glow=lava, seam=False),
          boots_of(black, dark, glow=lava))
    return head, back


@outfit("shadow_knight", "Shadow Knight", "LEGENDARY")
def shadow_knight():
    base, dark, steel, glow = C("22262e"), C("14161c"), C("3a404c"), C("41e0ff")
    head = Vox("shadow_knight_head")
    rows = face(["..........",
                 "..........",
                 "..........",
                 ".GGGGGGGG.",
                 "..........",
                 "....G.....",
                 "....G.....",
                 "..........",
                 "..........",
                 ".........."], {"G": glow})
    outfit_head_shell(head, steel, dark, rows)
    head.box(7, 13, 4, 9, 16, 12, dark)
    head.box(7, 16, 6, 9, 17, 11, steel)
    head.set(8, 15, 3, glow)
    back = Vox("shadow_knight_back")
    tex = S.feather_wing("wing_shadow", C("1c1e26"), C("101218"), C("2a2e38"), accent=glow, line=glow)
    wings(back, tex, W=16, H=16)
    back.box(7, 9, 4, 9, 13, 6, steel)
    armor("shadow_knight",
          plated(base, dark, steel, glow=glow, belt=dark),
          plated(base, dark, steel),
          plated(base, dark, steel, glow=glow, seam=False),
          boots_of(steel, dark, glow=glow))
    return head, back


@outfit("seraph", "Seraph", "MYTHIC")
def seraph():
    w1, w2, gold, gem, skin = C("f4f2ea"), C("d6d6de"), C("f2c230"), C("4fa8ff"), C("f0d8b8")
    head = Vox("seraph_head")
    rows = face(["..........",
                 "GGGGGGGGGG",
                 "....GG....",
                 "....GG....",
                 ".GGGGGGGG.",
                 "....GG....",
                 "....GG....",
                 "..........",
                 "..........",
                 ".........."], {"G": gold})
    outfit_head_shell(head, w1, gold, rows)
    head.disc(8, 8, 4.8, 16, gold, r_in=3.4)
    head.box(6, 13, 3, 10, 14, 4, gold)
    back = Vox("seraph_back")
    tex = S.feather_wing("wing_seraph", C("f4f6fa"), C("d0d4de"), C("ffffff"), accent=gold, line=C("e0b13a"))
    wings(back, tex, W=16, H=17)
    back.box(7, 9, 4, 9, 13, 6, gold)
    armor("seraph",
          plated(w1, w2, C("ffffff"), accent=gem, glow=gold, belt=gold),
          plated(w1, w2, C("ffffff"), glow=None, belt=gold),
          plated(w1, w2, C("ffffff"), glow=gold, seam=False),
          boots_of(gold, C("b8861a")))
    return head, back


@outfit("frost_warden", "Frost Warden", "LEGENDARY")
def frost_warden():
    i1, i2, i3, white = C("8fd3f5"), C("3a8fd8"), C("2f5ea8"), C("f0fbff")
    head = Vox("frost_warden_head")
    rows = face(["..........",
                 "..........",
                 ".DDDDDDDD.",
                 ".DWD..DWD.",
                 ".DDDDDDDD.",
                 "..........",
                 "...DDDD...",
                 "..........",
                 "..........",
                 ".........."], {"D": i3, "W": white})
    outfit_head_shell(head, i1, i3, rows)
    for x in range(3, 13):
        for z in range(3, 13):
            if (x in (3, 12) or z in (3, 12)) and (x + z) % 2 == 0:
                h = 2 + (x * 3 + z * 5) % 4
                head.box(x, 13, z, x + 1, 13 + h, z + 1, i1)
                head.set(x, 13 + h - 1, z, white)
    back = Vox("frost_warden_back")
    tex = S.spike_wing("wing_warden", C("5ab8ee"), C("bfe9ff"), C("ffffff"), n=9, length=(16, 30))
    wings(back, tex, W=16, H=16)
    back.box(7, 9, 4, 9, 13, 6, i2)
    armor("frost_warden",
          plated(i1, i3, white, accent=white, glow=white),
          plated(i1, i3, white),
          plated(i2, i3, i1, glow=white, seam=False),
          boots_of(white, i3, glow=i1))
    return head, back


@outfit("void_walker", "Void Walker", "MYTHIC")
def void_walker():
    d1, d2, p1, pink, star = C("2a1a4a"), C("160e2a"), C("6a3ab8"), C("ff6fd8"), C("f0e2ff")
    head = Vox("void_walker_head")
    rows = face(["..........",
                 "..........",
                 "..........",
                 "..P....P..",
                 "..........",
                 "..........",
                 "....SS....",
                 "..........",
                 "..........",
                 ".........."], {"P": pink, "S": star})
    outfit_head_shell(head, d1, d2, rows)
    head.box(3, 12, 3, 13, 14, 13, p1)
    head.box(4, 14, 4, 12, 15, 12, p1)
    # the ring behind the head (upright)
    for x in range(1, 16):
        for y in range(2, 18):
            d = math.hypot(x + 0.5 - 8, y + 0.5 - 10)
            if 5.4 < d <= 6.6:
                head.set(x, y, 14, star if (x + y) % 5 == 0 else C("b58cff"))
    back = Vox("void_walker_back")
    spots = [(5, 6), (9, 4), (3, 12), (13, 9), (20, 22), (24, 26), (17, 27)]
    tex = S.insect_wing("wing_void", C("8a4ae0"), C("2a1a4a"), C("ff6fd8"), spots=spots)
    wings(back, tex, W=14, H=15)
    back.box(7, 9, 4, 9, 13, 6, d2)
    armor("void_walker",
          plated(d1, d2, p1, glow=pink, sparkle=star),
          plated(d1, d2, p1, sparkle=star),
          plated(d2, d2, p1, glow=pink, seam=False, sparkle=star),
          boots_of(p1, d2, glow=pink))
    return head, back


@outfit("jungle_spirit", "Jungle Spirit", "LEGENDARY")
def jungle_spirit():
    g1, g2, g3, bark, bark2, pink, yel = C("5cc84a"), C("3f8a3a"), C("2a5a26"), C("6b4423"), C("4a2e18"), C("f78fb8"), C("ffe066")
    head = Vox("jungle_spirit_head")
    rows = face(["..........",
                 "..........",
                 ".BBBBBBBB.",
                 ".BY.BB.YB.",
                 ".BBBBBBBB.",
                 "..BBBBBB..",
                 "..B.BB.B..",
                 "..........",
                 "..........",
                 ".........."], {"B": bark, "Y": yel})
    outfit_head_shell(head, g2, g3, rows)
    head.box(3, 11, 3, 13, 13, 13, noise(g1, 0.08, 3))
    for s in (-1, 1):
        x = 5 if s < 0 else 10
        head.line((x, 13, 7), (x + s * 2, 18, 7), bark, r=0.5)
        head.line((x + s * 2, 18, 7), (x + s * 4, 20, 7), bark)
        head.line((x + s * 1, 16, 7), (x - s * 0.5, 19, 7), bark)
        head.set(x + s * 4, 21, 7, pink); head.set(round(x - s * 0.5), 20, 7, pink); head.set(x + s * 2, 19, 7, pink)
    head.set(8, 12, 2, pink)
    back = Vox("jungle_spirit_back")
    spots = [(6, 8), (12, 6), (22, 24), (18, 27)]
    tex = S.insect_wing("wing_jungle", C("7ad04a"), C("2a5a26"), C("3f8a3a"), spots=spots,
                        lobes=((14, 11, 13, 9, -0.35), (20, 24, 8, 6, 0.4)))
    wings(back, tex, W=15, H=16)
    back.box(7, 9, 4, 9, 13, 6, bark)

    def moss(face, u, v, w, h):
        if face in ("top", "bottom"):
            return g3
        c = g1 if (u * 3 + v * 5) % 7 > 2 else g2
        if face == "front" and w >= 8 and 3 <= u <= 4 and 4 <= v <= 5:
            return pink
        if v >= h - 2 and w >= 8:
            return bark
        return c

    def barky(face, u, v, w, h):
        if face in ("top", "bottom"):
            return bark2
        return bark if (u + v // 2) % 3 else bark2
    armor("jungle_spirit", moss, moss, barky, boots_of(bark2, C("2a1a10"), glow=None))
    return head, back


@outfit("neon_mech", "Neon Mech", "LEGENDARY")
def neon_mech():
    w1, w2, dark, pink, cyan = C("dfe3ea"), C("aeb4c0"), C("5c6678"), C("ff5ccf"), C("41e0ff")
    head = Vox("neon_mech_head")
    rows = face(["..........",
                 "..........",
                 ".DDDDDDDD.",
                 ".DCCCCCCD.",
                 ".DDDDDDDD.",
                 "..........",
                 "...PPPP...",
                 "..........",
                 "..........",
                 ".........."], {"D": dark, "C": cyan, "P": pink})
    outfit_head_shell(head, w1, dark, rows)
    head.box(3, 12, 3, 13, 13, 13, w2)
    for y in range(13, 22):
        head.set(11, y, 10, dark)
    head.set(11, 22, 10, pink)
    head.box(12, 8, 6, 14, 10, 10, pink)
    back = Vox("neon_mech_back")
    tex = S.blade_wing("wing_neon", C("c4cad6"), C("5c6678"), C("ffffff"), C("ff5ccf"))
    wings(back, tex, W=14, H=13)
    back.box(5, 5, 3, 11, 13, 6, w2)
    for x in (5, 10):
        back.box(x, 4, 3, x + 1, 5, 5, cyan)
    armor("neon_mech",
          plated(w1, dark, C("ffffff"), accent=cyan, glow=pink),
          plated(w1, dark, C("ffffff"), glow=None),
          plated(w2, dark, w1, glow=cyan, seam=False),
          boots_of(dark, C("2e3440"), glow=pink))
    return head, back


@outfit("golden_emperor", "Golden Emperor", "MYTHIC")
def golden_emperor():
    gold, gold2, purple, purple2, ermine, spot, red, gem = C("e8b830"), C("b8861a"), C("5b2fb5"), C("3e1f86"), C("f4f1e8"), C("1c1c22"), C("c8324a"), C("4fa8ff")
    head = Vox("golden_emperor_head")
    rows = face(["..........",
                 "..........",
                 "..........",
                 ".DD....DD.",
                 "..........",
                 "....DD....",
                 "..D....D..",
                 "...DDDD...",
                 "..........",
                 ".........."], {"D": gold2})
    outfit_head_shell(head, gold, gold2, rows)
    sq_ring(head, 2, 2, 14, 14, 13, 14, lambda x, y, z: spot if (x + z) % 3 == 0 else ermine)
    sq_ring(head, 3, 3, 13, 13, 14, 16, gold)
    head.box(4, 13, 4, 12, 17, 12, purple)
    for x, z in ((3, 3), (12, 3), (3, 12), (12, 12), (8, 3), (3, 8), (12, 8), (8, 12)):
        head.box(x, 16, z, x + 1, 18, z + 1, gold)
    head.box(8, 17, 8, 9, 21, 9, gold)
    head.set(7, 20, 8, gold); head.set(9, 20, 8, gold)
    head.set(5, 15, 2, red); head.set(8, 15, 2, gem); head.set(10, 15, 2, red)
    back = Vox("golden_emperor_back")

    def crosses(im):
        for (x, y) in ((4, 10), (11, 10), (7, 17), (4, 24), (11, 24)):
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                im.putpixel((x + dx, y + dy), (232, 184, 48, 255))
        for x in range(1, 15):
            im.putpixel((x, 3), (244, 241, 232, 255) if x % 3 else (28, 28, 34, 255))
            im.putpixel((x, 4), (244, 241, 232, 255))
    tex = S.cape("cape_emperor", purple, purple2, gold, gold, emblem=crosses, stripes=False)
    cape_plane(back, tex, y_top=15, H=24, x0=2, x1=14)
    armor("golden_emperor",
          plated(gold, gold2, C("ffe680"), accent=red, glow=None, belt=purple),
          plated(purple, purple2, gold, glow=None),
          plated(gold, gold2, C("ffe680"), seam=False),
          boots_of(gold, gold2))
    return head, back
