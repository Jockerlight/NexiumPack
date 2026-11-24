"""The 54 hats. Head = x/y/z 4..12 (front = north, z = 4), top at y = 12."""
import math
from vox import Vox, shade, mix
from shapes import C, sq_ring, slab, dome, cone, circle_pts, ear, stripes, noise

HATS = []


def hat(id, name, rarity):
    def deco(fn):
        HATS.append((id, name, rarity, fn))
        return fn
    return deco


@hat("cyber_halo", "Cyber Halo", "EPIC")
def cyber_halo():
    v = Vox("cyber_halo")
    cyan, lite, white = C("3fd8ff"), C("9cf2ff"), C("f0ffff")
    v.disc(8, 8, 4.6, 16, cyan, r_in=3.4)
    for i, (x, z) in enumerate(circle_pts(8, 8, 4.0, 8, 0.4)):
        v.set(math.floor(x), 17, math.floor(z), white if i % 2 == 0 else lite)
    for x, z, y in ((3, 6, 19), (12, 10, 18), (8, 2, 20)):
        v.set(x, y, z, lite)
    return v


@hat("crown", "Crown", "RARE")
def crown():
    v = Vox("crown")
    gold, dark, red, pearl = C("f2c230"), C("b8861a"), C("a3123a"), C("f4f1e8")
    gems = [C("2fa8ff"), C("e8304a"), C("34d27a")]
    sq_ring(v, 3, 3, 13, 13, 11, 14, lambda x, y, z: dark if y == 11 else gold)
    slab(v, 4, 4, 12, 12, 12, red, 14)
    slab(v, 5, 5, 11, 11, 14, red)
    for x in (3, 5, 8, 10, 12):
        for z in (3, 12):
            v.box(x, 14, z, x + 1, 16, z + 1, gold)
            v.set(x, 16, z, pearl)
    for z in (5, 8, 10):
        for x in (3, 12):
            v.box(x, 14, z, x + 1, 16, z + 1, gold)
            v.set(x, 16, z, pearl)
    for i, x in enumerate((5, 8, 10)):
        v.set(x, 12, 2, gems[i % 3])
        v.set(x, 12, 13, gems[(i + 1) % 3])
    return v


@hat("fishing_cap", "Fishing Cap", "COMMON")
def fishing_cap():
    v = Vox("fishing_cap")
    blue, dark, lite = C("3d6fb0"), C("2a4f86"), C("5a8fd0")
    slab(v, 2, 2, 14, 14, 11, lite)
    v.box(3, 12, 3, 13, 15, 13, blue)
    slab(v, 4, 4, 12, 12, 15, dark)
    sq_ring(v, 3, 3, 13, 13, 12, 13, dark)
    # lure on the side
    v.set(13, 13, 6, C("e03a3a"))
    v.set(13, 13, 7, C("f4f4f4"))
    v.set(13, 14, 6, C("c8c8c8"))
    return v


@hat("straw_hat", "Straw Hat", "COMMON")
def straw_hat():
    v = Vox("straw_hat")
    s1, s2, band = C("e6c164"), C("c9a046"), C("c03a3a")
    v.disc(8, 8, 7.6, 11, lambda x, y, z: s1 if (round(math.hypot(x + .5 - 8, z + .5 - 8)) % 2) else s2)
    v.disc(8, 8, 4.6, 12, s1, y1=15)
    v.disc(8, 8, 4.6, 12, band, r_in=3.6)
    v.disc(8, 8, 3.6, 15, s2)
    return v


@hat("miner_lamp", "Miner Lamp", "COMMON")
def miner_lamp():
    v = Vox("miner_lamp")
    y1, y2, strap, glass, rim = C("f2c418"), C("cf9e12"), C("3a3a42"), C("fff6b0"), C("6b6b75")
    v.box(3, 10, 3, 13, 11, 14, y2)
    dome(v, 8, 8.5, 5.4, 11, 4, y1)
    for x in range(4, 12, 2):
        v.box(x, 12, 3, x + 1, 15, 13, y2)
    v.box(5, 11, 1, 11, 15, 3, rim)
    v.box(6, 12, 0, 10, 14, 1, glass)
    v.box(3, 10, 13, 13, 11, 14, strap)
    return v


@hat("space_helmet", "Space Helmet", "LEGENDARY")
def space_helmet():
    v = Vox("space_helmet")
    w1, w2, dark, glass, red, blue = C("d8dce4"), C("aeb4c0"), C("3b4250"), C("2a3550"), C("e23b3b"), C("4fc4ff")
    v.frame(2, 3, 2, 14, 15, 14, noise(w1, 0.05, 3))
    v.box(3, 3, 3, 13, 4, 13, None)
    # visor
    v.box(4, 5, 2, 12, 12, 3, glass)
    sq_ring(v, 3, 2, 13, 3, 4, 13, dark)
    v.box(3, 4, 2, 13, 5, 3, dark)
    v.box(3, 12, 2, 13, 13, 3, dark)
    # side panel + stripe
    v.box(14, 6, 6, 15, 10, 10, w2)
    v.box(14, 7, 7, 15, 9, 9, blue)
    v.box(2, 14, 2, 14, 15, 14, w2)
    v.box(6, 14, 2, 10, 15, 14, red)
    v.box(4, 15, 9, 5, 18, 10, dark)
    v.set(4, 18, 9, red)
    return v


@hat("crystal_horns", "Crystal Horns", "EPIC")
def crystal_horns():
    v = Vox("crystal_horns")
    plate, p1, p2, p3 = C("5c6270"), C("b58cff"), C("8a55e8"), C("e5d4ff")
    slab(v, 4, 4, 12, 12, 12, plate)
    for xb, s in ((5, -1), (10, 1)):
        v.line((xb, 13, 7), (xb + s * 1.5, 19, 7), p2, r=1.0)
        v.line((xb, 18, 7), (xb + s * 2.2, 21, 7), p1, r=0.5)
        v.set(round(xb + s * 2.2), 21, 7, p3)
        v.line((xb + s, 13, 10), (xb + s * 2, 16, 10), p1, r=0.5)
        v.set(xb + s * 2, 16, 10, p3)
        v.line((xb - s, 13, 5), (xb - s, 15, 4), p1, r=0.3)
    return v


@hat("bunny_ears", "Bunny Ears", "COMMON")
def bunny_ears():
    v = Vox("bunny_ears")
    white, pink, band = C("f6f2f4"), C("f7a8c8"), C("e8e2e6")
    slab(v, 4, 7, 12, 9, 12, band)
    for x0 in (5, 9):
        v.box(x0, 13, 7, x0 + 2, 20, 8, white)
        v.box(x0, 14, 6, x0 + 2, 19, 7, pink)
        v.box(x0, 19, 6, x0 + 2, 20, 7, white)
    return v


@hat("wizard_hat", "Wizard Hat", "RARE")
def wizard_hat():
    v = Vox("wizard_hat")
    p1, p2, gold, star = C("5b2fb5"), C("3e1f86"), C("f2c230"), C("ffe680")
    v.disc(8, 8, 7.1, 11, p2)
    cone(v, 8, 8, 4.8, 12, 9, lambda x, y, z: gold if (x + y + z) % 5 == 0 else (p1 if (y % 3) else p2), lean=(1.5, 2.5), r1=1.0)
    v.disc(8, 8, 4.9, 12, gold, r_in=3.9)
    v.set(10, 21, 11, star)
    v.set(10, 22, 11, star)
    v.set(9, 21, 11, star)
    v.set(11, 21, 11, star)
    return v


@hat("goggles", "Goggles", "COMMON")
def goggles():
    v = Vox("goggles")
    strap, rim, glass, shine = C("6b4423"), C("d0a040"), C("7fd6e8"), C("e8fbff")
    sq_ring(v, 3, 3, 13, 13, 8, 10, strap)
    for x0 in (4, 9):
        v.box(x0, 7, 2, x0 + 3, 11, 3, rim)
        v.box(x0 + 1, 8, 1, x0 + 2, 10, 2, glass)
        v.set(x0 + 1, 9, 1, shine)
        v.box(x0, 8, 1, x0 + 1, 10, 2, rim)
        v.box(x0 + 2, 8, 1, x0 + 3, 10, 2, rim)
    return v


@hat("sunflower_crown", "Sunflower Crown", "COMMON")
def sunflower_crown():
    v = Vox("sunflower_crown")
    y1, y2, leaf, brown = C("f6c625"), C("e09a10"), C("4f9a3a"), C("6b4423")
    sq_ring(v, 3, 3, 13, 13, 12, 13, leaf)
    sq_ring(v, 3, 3, 13, 13, 13, 15, lambda x, y, z: y1 if (x + z) % 2 else y2)
    for x, z in ((3, 3), (12, 3), (3, 12), (12, 12), (7, 3), (12, 7), (8, 12), (3, 8)):
        v.set(x, 15, z, y1)
    v.box(7, 13, 2, 9, 15, 3, brown)
    v.set(6, 14, 2, y1); v.set(9, 14, 2, y1); v.set(7, 15, 2, y1); v.set(8, 12, 2, y1)
    return v


@hat("neon_visor", "Neon Visor", "RARE")
def neon_visor():
    v = Vox("neon_visor")
    black, pink, hot, cyan = C("1d1d24"), C("ff7ad9"), C("ffc4ef"), C("41e0ff")
    sq_ring(v, 3, 3, 13, 13, 7, 10, black)
    v.box(4, 8, 2, 12, 9, 3, pink)
    v.box(5, 8, 2, 7, 9, 3, hot)
    v.box(3, 7, 2, 13, 8, 3, black)
    v.box(3, 9, 2, 13, 10, 3, black)
    v.set(3, 8, 2, black); v.set(12, 8, 2, black)
    v.set(2, 8, 5, cyan); v.set(13, 8, 5, cyan)
    return v


@hat("tiny_ufo", "Tiny UFO", "EPIC")
def tiny_ufo():
    v = Vox("tiny_ufo")
    hull, dark, dome_c, light, beam = C("c4cad6"), C("8a92a3"), C("4a5266"), C("ffe066"), C("9cf2ff")
    v.disc(8, 8, 5.2, 15, hull)
    v.disc(8, 8, 5.2, 15, lambda x, y, z: light if (x + z) % 3 == 0 else dark, r_in=4.3)
    v.disc(8, 8, 3.8, 14, dark)
    dome(v, 8, 8, 2.8, 16, 3, dome_c)
    v.set(8, 19, 8, light)
    v.disc(8, 8, 1.6, 13, beam)
    return v


@hat("ghost_buddy", "Ghost Buddy", "RARE")
def ghost_buddy():
    v = Vox("ghost_buddy")
    w, sh, eye, cheek = C("f4f6fa"), C("d6dbe6"), C("26262e"), C("f7a8c8")
    v.ellipsoid(8, 15.5, 8, 3.2, 3.6, 3.0, w)
    for x in range(5, 11):
        if x % 2 == 0:
            v.set(x, 12, 6, sh)
            v.set(x, 12, 9, sh)
    v.set(7, 16, 5, eye); v.set(9, 16, 5, eye)
    v.set(6, 15, 5, cheek); v.set(10, 15, 5, cheek)
    v.set(8, 14, 5, eye)
    return v


@hat("top_hat", "Top Hat", "RARE")
def top_hat():
    v = Vox("top_hat")
    black, dark, red = C("23232a"), C("15151a"), C("c22b3a")
    v.disc(8, 8, 6.2, 11, dark)
    v.box(4, 12, 4, 12, 19, 12, black)
    v.box(4, 13, 4, 12, 15, 12, red)
    slab(v, 4, 4, 12, 12, 19, dark)
    return v


@hat("beanie", "Beanie", "COMMON")
def beanie():
    v = Vox("beanie")
    red, dark, white = C("c8324a"), C("9a2236"), C("f4f4f4")
    sq_ring(v, 3, 3, 13, 13, 9, 11, lambda x, y, z: dark if (x + z) % 2 else shade(dark, 0.85))
    sq_ring(v, 3, 3, 13, 13, 11, 13, noise(red, 0.07, 5))
    v.box(3, 12, 3, 13, 14, 13, noise(red, 0.07, 6))
    v.box(4, 14, 4, 12, 15, 12, red)
    v.box(7, 15, 7, 9, 17, 9, white)
    v.set(6, 15, 7, white); v.set(9, 15, 8, white); v.set(7, 15, 6, white); v.set(8, 15, 9, white)
    return v


@hat("headphones", "Headphones", "RARE")
def headphones():
    v = Vox("headphones")
    black, gray, glow = C("1e1f26"), C("3a3d4a"), C("41e0ff")
    v.box(3, 12, 6, 13, 13, 10, black)
    v.box(2, 10, 6, 3, 13, 10, black)
    v.box(13, 10, 6, 14, 13, 10, black)
    for x0, x1 in ((1, 3), (13, 15)):
        v.box(x0, 5, 5, x1, 10, 11, gray)
    for x in (0, 15):
        v.box(x, 6, 6, x + 1, 9, 10, glow)
        v.box(x, 7, 7, x + 1, 8, 9, black)
    return v


@hat("cat_ears", "Cat Ears", "COMMON")
def cat_ears():
    v = Vox("cat_ears")
    black, pink, band = C("22222a"), C("f78fb8"), C("2e2e38")
    slab(v, 4, 7, 12, 9, 12, band)
    for x0 in (3, 9):
        ear(v, x0, 7, 4, 5, 13, black, inner=pink, depth=1)
        ear(v, x0, 8, 4, 5, 13, black, depth=1)
    return v


@hat("viking_helmet", "Viking Helmet", "EPIC")
def viking_helmet():
    v = Vox("viking_helmet")
    steel, dark, leather, gold, horn, tip = C("8a96aa"), C("5c667a"), C("7a4a28"), C("d9a536"), C("eee6cf"), C("c8bb97")
    sq_ring(v, 3, 3, 13, 13, 9, 11, gold)
    v.box(3, 11, 3, 13, 14, 13, noise(steel, 0.06, 2))
    v.box(4, 14, 4, 12, 15, 12, steel)
    v.box(5, 15, 5, 11, 16, 11, dark)
    v.box(7, 9, 2, 9, 16, 3, leather)
    v.box(7, 14, 3, 9, 16, 13, leather)
    v.box(3, 14, 7, 13, 15, 9, leather)
    for side in (-1, 1):
        x = 2 if side < 0 else 13
        pts = [(x, 12, 7.5), (x + side * 1.5, 12.5, 7.5), (x + side * 2.6, 13.6, 7.5), (x + side * 3.2, 15.2, 7.5), (x + side * 3.2, 17.0, 7.5), (x + side * 2.6, 18.6, 7.5)]
        for i in range(len(pts) - 1):
            r = 1.2 - i * 0.22
            v.line(pts[i], pts[i + 1], horn if i < 3 else tip, r=max(0.0, r))
    return v


@hat("flower_crown", "Flower Crown", "COMMON")
def flower_crown():
    v = Vox("flower_crown")
    vine = C("4f9a3a")
    cols = [C("f7a8c8"), C("ffffff"), C("ffe066"), C("c79bff")]
    sq_ring(v, 3, 3, 13, 13, 12, 13, vine)
    i = 0
    for x in range(3, 13):
        for z in range(3, 13):
            if (x in (3, 12) or z in (3, 12)) and (x + z) % 2 == 0:
                v.set(x, 13, z, cols[i % 4])
                i += 1
    return v


@hat("chef_hat", "Chef Hat", "COMMON")
def chef_hat():
    v = Vox("chef_hat")
    w, sh, band = C("f4f4f6"), C("d9dce4"), C("e6e8ee")
    sq_ring(v, 3, 3, 13, 13, 11, 14, band)
    v.box(4, 12, 4, 12, 14, 12, w)
    v.box(2, 14, 2, 14, 18, 14, noise(w, 0.06, 9))
    for x, z in ((3, 3), (11, 4), (4, 11), (10, 10), (7, 7)):
        v.box(x, 18, z, x + 3, 19, z + 3, sh if (x + z) % 2 else w)
    for x, z in ((2, 2), (13, 2), (2, 13), (13, 13)):
        for y in (14, 17):
            v.set(x, y, z, None)
    v.set(9, 12, 2, C("d0a040"))
    return v


@hat("pirate_hat", "Pirate Hat", "EPIC")
def pirate_hat():
    v = Vox("pirate_hat")
    black, gold, white, red = C("1c1c22"), C("e0b13a"), C("f2f2f2"), C("d23a3a")
    v.box(1, 12, 3, 15, 13, 13, black)
    v.box(3, 12, 1, 13, 13, 15, black)
    for x in (1, 14):
        v.box(x, 13, 4, x + 1, 15, 12, black)
        v.set(x, 15, 5, gold); v.set(x, 15, 10, gold)
    v.box(4, 13, 3, 12, 16, 13, black)
    v.box(3, 13, 2, 13, 15, 3, black)
    v.box(3, 15, 2, 13, 16, 3, gold)
    v.box(7, 13, 1, 9, 15, 2, white)
    v.set(7, 14, 1, black)
    # feather
    for i, (x, y) in enumerate(((11, 16), (12, 17), (12, 18), (13, 19), (13, 20))):
        v.set(x, y, 10, red)
        v.set(x, y, 11, shade(red, 0.8))
    return v


@hat("propeller_cap", "Propeller Cap", "RARE")
def propeller_cap():
    v = Vox("propeller_cap")
    cols = [C("e8423a"), C("f6c625"), C("3cb44b"), C("3a7be8")]
    v.box(3, 12, 3, 13, 14, 13, lambda x, y, z: cols[(0 if x < 8 else 1) + (0 if z < 8 else 2)])
    v.box(4, 14, 4, 12, 15, 12, lambda x, y, z: cols[(0 if x < 8 else 1) + (0 if z < 8 else 2)])
    v.box(3, 12, 0, 13, 13, 3, C("3aa0e8"))
    v.box(7, 15, 7, 9, 17, 9, C("9aa0ae"))
    v.box(2, 17, 7, 14, 18, 9, C("f6c625"))
    v.set(2, 17, 7, C("e8423a")); v.set(13, 17, 8, C("e8423a"))
    return v


@hat("party_hat", "Party Hat", "COMMON")
def party_hat():
    v = Vox("party_hat")
    w, dots, pom, string = C("f4f2fa"), [C("4fc4ff"), C("ff6fb5"), C("ffe066")], C("ffd24a"), C("7a7a88")
    cone(v, 8, 8, 4.1, 12, 10, lambda x, y, z: dots[(x + y + z) % 3] if (x * 3 + y + z * 5) % 6 == 0 else (C("7fd6ff") if y % 4 == 0 else w), r1=0.6)
    v.box(7, 22, 7, 9, 24, 9, pom)
    for y in range(4, 12):
        v.set(12, y, 8, string)
    return v


@hat("angel_halo", "Angel Halo", "RARE")
def angel_halo():
    v = Vox("angel_halo")
    g1, g2 = C("ffd84a"), C("ffefa0")
    v.disc(8, 8, 4.8, 17, lambda x, y, z: g2 if (x + z) % 3 == 0 else g1, r_in=3.4)
    return v


@hat("void_halo", "Void Halo", "EPIC")
def void_halo():
    v = Vox("void_halo")
    p1, p2, sp = C("9a5cff"), C("c79bff"), C("f0e2ff")
    v.disc(8, 8, 4.8, 16, p1, r_in=3.4)
    for i, (x, z) in enumerate(circle_pts(8, 8, 4.1, 8)):
        v.set(math.floor(x), 17, math.floor(z), p2)
        if i % 2 == 0:
            v.set(math.floor(x), 18, math.floor(z), sp)
    return v


@hat("royal_crown", "Royal Crown", "LEGENDARY")
def royal_crown():
    v = Vox("royal_crown")
    gold, dark, red, ermine, spot, pearl = C("f2c230"), C("b8861a"), C("8f0f2e"), C("f4f1e8"), C("1c1c22"), C("fffaf0")
    sq_ring(v, 3, 3, 13, 13, 11, 12, lambda x, y, z: spot if (x + z) % 3 == 0 else ermine)
    sq_ring(v, 3, 3, 13, 13, 12, 14, gold)
    v.box(4, 12, 4, 12, 16, 12, red)
    dome(v, 8, 8, 3.6, 16, 2, red)
    for x, z in ((3, 3), (12, 3), (3, 12), (12, 12), (8, 3), (8, 12), (3, 8), (12, 8)):
        v.box(x, 14, z, x + 1, 16, z + 1, gold)
        v.set(x, 16, z, pearl)
    # arches
    for k in range(4, 12):
        v.set(k, 17 if 6 <= k <= 9 else 16, 8, gold)
        v.set(8, 17 if 6 <= k <= 9 else 16, k, gold)
    v.box(8, 18, 8, 9, 21, 9, gold)
    v.set(7, 20, 8, gold); v.set(9, 20, 8, gold)
    for x, c in ((5, C("2fa8ff")), (8, C("e8304a")), (10, C("34d27a"))):
        v.set(x, 13, 2, c)
    return v


@hat("ice_crown", "Ice Crown", "EPIC")
def ice_crown():
    v = Vox("ice_crown")
    i1, i2, i3 = C("bfe9ff"), C("8fd3f5"), C("f0fbff")
    sq_ring(v, 3, 3, 13, 13, 11, 13, i2)
    hs = [4, 2, 5, 3, 6, 2, 4, 3, 5, 2]
    k = 0
    for x in range(3, 13):
        for z in range(3, 13):
            if x in (3, 12) or z in (3, 12):
                h = hs[(x * 7 + z * 3) % len(hs)]
                if (x + z) % 2 == 0:
                    v.box(x, 13, z, x + 1, 13 + h, z + 1, i1)
                    v.set(x, 13 + h - 1, z, i3)
    return v


@hat("laurel_wreath", "Laurel Wreath", "RARE")
def laurel_wreath():
    v = Vox("laurel_wreath")
    g1, g2 = C("f2c230"), C("c99a1e")
    sq_ring(v, 3, 3, 13, 13, 12, 13, g2)
    for x in range(2, 14):
        for z in range(2, 14):
            if (x in (2, 13) or z in (2, 13)) and (x + z) % 2 == 1 and not (x in (2, 13) and z in (2, 13)):
                v.set(x, 13, z, g1)
    sq_ring(v, 3, 3, 13, 13, 13, 14, lambda x, y, z: g1 if (x + z) % 2 == 0 else None)
    return v


@hat("captain_hat", "Captain Hat", "RARE")
def captain_hat():
    v = Vox("captain_hat")
    w, sh, black, gold = C("f2f2f4"), C("d0d4dc"), C("1c1c22"), C("e0b13a")
    v.box(3, 11, 3, 13, 13, 13, black)
    v.box(2, 13, 2, 14, 15, 14, noise(w, 0.04, 4))
    v.box(3, 15, 3, 13, 16, 13, sh)
    v.box(4, 11, 0, 12, 12, 3, black)
    v.box(4, 13, 2, 12, 14, 2, gold)
    v.box(7, 12, 2, 9, 14, 3, gold)
    v.box(4, 12, 2, 12, 13, 3, gold)
    return v


@hat("sou_wester", "Sou'wester", "COMMON")
def sou_wester():
    v = Vox("sou_wester")
    y1, y2 = C("f6c625"), C("d9a20e")
    v.box(2, 11, 2, 14, 12, 15, y2)
    v.box(1, 10, 10, 15, 11, 16, y2)
    v.box(3, 12, 3, 13, 15, 13, noise(y1, 0.05, 8))
    v.box(4, 15, 4, 12, 16, 12, y1)
    sq_ring(v, 3, 3, 13, 13, 12, 13, y2)
    return v


@hat("diving_helmet", "Diving Helmet", "LEGENDARY")
def diving_helmet():
    v = Vox("diving_helmet")
    brass, dark, glass, bolt, shine = C("c98a3a"), C("8f5a22"), C("6fb6e0"), C("e8d6a0"), C("cfeeff")
    v.frame(2, 3, 2, 14, 15, 14, noise(brass, 0.08, 7))
    v.box(3, 3, 3, 13, 4, 13, None)
    v.box(3, 15, 3, 13, 16, 13, dark)
    v.box(6, 16, 6, 10, 17, 10, brass)
    for (x0, z0, ax) in ((5, 2, "z"), (2, 5, "x"), (13, 5, "x")):
        for a in range(6):
            for b in range(6):
                if (a - 2.5) ** 2 + (b - 2.5) ** 2 <= 7:
                    col = glass if (a - 2.5) ** 2 + (b - 2.5) ** 2 <= 4 else dark
                    if ax == "z":
                        v.set(x0 + a, 5 + b, z0, col)
                    else:
                        v.set(x0, 5 + b, z0 + a, col)
    v.set(6, 9, 2, shine)
    for x, z in ((2, 2), (13, 2), (2, 13), (13, 13)):
        v.set(x, 4, z, bolt); v.set(x, 13, z, bolt)
    sq_ring(v, 2, 2, 14, 14, 3, 4, dark)
    return v


@hat("fish_hat", "Fish Hat", "RARE")
def fish_hat():
    v = Vox("fish_hat")
    o1, o2, w, black = C("f08a2a"), C("c8641a"), C("f6f2ea"), C("1c1c22")
    v.box(4, 12, 3, 12, 15, 13, o1)
    for z in (5, 9):
        v.box(4, 12, z, 12, 15, z + 1, w)
    v.box(5, 15, 4, 11, 16, 12, o1)
    v.box(5, 12, 1, 11, 14, 3, o1)
    v.set(4, 14, 2, w); v.set(11, 14, 2, w)
    v.set(4, 14, 3, black); v.set(11, 14, 3, black)
    v.box(6, 12, 13, 10, 15, 14, o2)
    v.box(5, 11, 14, 11, 16, 15, o2)
    v.box(7, 16, 6, 9, 17, 11, o2)
    return v


@hat("drill_helmet", "Drill Helmet", "EPIC")
def drill_helmet():
    v = Vox("drill_helmet")
    y1, y2, steel, dark = C("f2c418"), C("cf9e12"), C("b8c0cc"), C("6b7280")
    v.box(2, 11, 2, 14, 12, 14, y2)
    v.box(3, 12, 3, 13, 14, 13, y1)
    v.box(4, 14, 4, 12, 15, 12, y2)
    for i in range(6):
        r = 2.6 - i * 0.42
        v.disc(8, 8, max(0.5, r), 15 + i, lambda x, y, z: steel if (x + y + z) % 2 else dark)
    v.box(5, 12, 2, 11, 13, 3, dark)
    return v


@hat("hard_hat", "Hard Hat", "COMMON")
def hard_hat():
    v = Vox("hard_hat")
    o1, o2, w = C("f2811f"), C("c9620e"), C("f4f4f4")
    v.box(2, 11, 1, 14, 12, 14, o2)
    dome(v, 8, 8, 5.4, 12, 4, o1)
    for x in (5, 8, 10):
        v.box(x, 12, 3, x + 1, 16, 13, o2)
    v.box(3, 12, 2, 13, 13, 3, w)
    return v


@hat("farmer_cap", "Farmer Cap", "COMMON")
def farmer_cap():
    v = Vox("farmer_cap")
    red, w, mesh, green = C("c8324a"), C("f2f2f2"), C("dadde4"), C("4f9a3a")
    v.box(3, 11, 3, 13, 14, 13, mesh)
    v.box(3, 11, 3, 13, 14, 5, w)
    v.box(4, 14, 4, 12, 15, 12, red)
    v.box(3, 11, 0, 13, 12, 3, red)
    v.box(6, 12, 2, 10, 13, 3, green)
    v.set(7, 13, 2, red); v.set(8, 13, 2, red)
    return v


@hat("sun_hat", "Sun Hat", "COMMON")
def sun_hat():
    v = Vox("sun_hat")
    s1, s2, band, fl = C("efdcae"), C("d9c08a"), C("f2a8c8"), [C("ff6fb5"), C("ffe066"), C("ffffff")]
    v.disc(8, 8, 7.8, 11, lambda x, y, z: s2 if round(math.hypot(x + .5 - 8, z + .5 - 8)) == 7 else s1)
    v.disc(8, 8, 4.4, 12, s1, y1=15)
    v.disc(8, 8, 4.4, 12, band, r_in=3.4)
    for i, (x, z) in enumerate(circle_pts(8, 8, 4.4, 6)):
        v.set(math.floor(x), 13, math.floor(z), fl[i % 3])
    return v


@hat("pumpkin_hat", "Pumpkin Hat", "EPIC")
def pumpkin_hat():
    v = Vox("pumpkin_hat")
    o1, o2, glow, stem, leaf = C("e07a1f"), C("b85a12"), C("ffd04a"), C("5a3a1e"), C("4f9a3a")
    v.box(3, 3, 3, 13, 13, 13, lambda x, y, z: o2 if ((x - 3) % 3 == 0 or (z - 3) % 3 == 0) else o1)
    face = ["..........",
            ".GG....GG.",
            ".GG....GG.",
            "..........",
            "....GG....",
            "..........",
            ".G.GGGG.G.",
            "..GG..GG..",
            ".........."]
    for j, row in enumerate(face):
        for i, ch in enumerate(row):
            if ch == "G":
                v.set(3 + i, 12 - j, 3, glow)
    v.box(7, 13, 7, 9, 15, 9, stem)
    v.box(9, 13, 8, 12, 14, 10, leaf)
    return v


@hat("mushroom_cap", "Mushroom Cap", "RARE")
def mushroom_cap():
    v = Vox("mushroom_cap")
    red, w, gill = C("d8323a"), C("f6f4ee"), C("e8dcc8")
    v.disc(8, 8, 7.2, 12, gill)
    dome(v, 8, 8, 7.2, 13, 5, lambda x, y, z: w if ((x * 5 + z * 3 + y * 7) % 11 == 0) else red, flat=0.6)
    for x, y, z in ((4, 15, 2), (10, 14, 2), (2, 14, 8), (13, 14, 6), (7, 17, 5), (9, 16, 11)):
        v.set(x, y, z, w)
    return v


@hat("fox_ears", "Fox Ears", "COMMON")
def fox_ears():
    v = Vox("fox_ears")
    o, w, black, band = C("f08a2a"), C("f6f2ea"), C("2a2228"), C("c8641a")
    slab(v, 4, 7, 12, 9, 12, band)
    for x0 in (3, 9):
        ear(v, x0, 7, 4, 5, 13, o, inner=w, tip=black, depth=1)
        ear(v, x0, 8, 4, 5, 13, o, tip=black, depth=1)
    return v


@hat("bear_ears", "Bear Ears", "COMMON")
def bear_ears():
    v = Vox("bear_ears")
    b, pink, band = C("7a4a28"), C("e8a0a8"), C("5c3820")
    slab(v, 4, 7, 12, 9, 12, band)
    for x0 in (4, 9):
        v.box(x0, 13, 7, x0 + 3, 16, 9, b)
        v.set(x0 + 1, 14, 6, pink)
        v.set(x0 + 1, 15, 6, pink)
        v.set(x0, 15, 7, None); v.set(x0 + 2, 15, 7, None)
        v.set(x0, 15, 8, None); v.set(x0 + 2, 15, 8, None)
        v.box(x0 + 1, 16, 7, x0 + 2, 17, 9, b)
    return v


@hat("frog_hat", "Frog Hat", "RARE")
def frog_hat():
    v = Vox("frog_hat")
    g1, g2, w, black, pink = C("5cc84a"), C("3f9a34"), C("f6f6f6"), C("1c1c22"), C("f78fb8")
    v.box(3, 11, 3, 13, 14, 13, noise(g1, 0.06, 3))
    v.box(4, 14, 4, 12, 15, 12, g1)
    sq_ring(v, 3, 3, 13, 13, 11, 12, g2)
    for x0 in (3, 10):
        v.box(x0, 14, 3, x0 + 3, 17, 6, g1)
        v.box(x0, 15, 2, x0 + 3, 17, 3, w)
        v.set(x0 + 1, 15, 2, black)
        v.set(x0 + 1, 16, 2, black)
    v.set(3, 12, 2, pink); v.set(12, 12, 2, pink)
    v.box(5, 12, 2, 11, 13, 3, g2)
    return v


@hat("knight_helm", "Knight Helm", "LEGENDARY")
def knight_helm():
    v = Vox("knight_helm")
    steel, dark, slit, gold, plume, plume2 = C("aeb6c4"), C("6e7686"), C("1a1c22"), C("e0b13a"), C("d8323a"), C("a8202a")
    v.frame(3, 3, 3, 13, 14, 13, noise(steel, 0.06, 11))
    v.box(4, 3, 4, 12, 4, 12, None)
    v.box(4, 14, 4, 12, 15, 12, steel)
    v.box(4, 8, 3, 12, 9, 4, slit)
    for x in (5, 7, 9, 11):
        v.box(x, 4, 3, x + 1, 7, 4, slit)
    v.box(7, 3, 2, 9, 14, 3, gold)
    v.box(4, 10, 2, 12, 11, 3, gold)
    sq_ring(v, 3, 3, 13, 13, 3, 4, dark)
    for i, (y, z) in enumerate(((15, 6), (16, 6), (17, 7), (18, 8), (18, 9), (17, 10), (16, 11), (15, 12), (14, 13))):
        v.box(7, y, z, 9, y + 1, z + 1, plume if i % 2 == 0 else plume2)
    v.set(3, 9, 2, gold)
    return v


@hat("cowboy_hat", "Cowboy Hat", "RARE")
def cowboy_hat():
    v = Vox("cowboy_hat")
    b1, b2, band, buckle = C("8a5a32"), C("6b4423"), C("3a2616"), C("d9b24a")
    v.box(1, 11, 2, 15, 12, 14, b2)
    v.box(0, 12, 3, 1, 13, 13, b2)
    v.box(15, 12, 3, 16, 13, 13, b2)
    v.box(3, 12, 4, 13, 16, 12, noise(b1, 0.06, 2))
    v.box(4, 16, 5, 12, 17, 11, b1)
    v.box(7, 16, 5, 9, 17, 11, b2)
    sq_ring(v, 3, 4, 13, 12, 12, 13, band)
    v.set(8, 12, 3, buckle)
    return v


@hat("witch_hat", "Witch Hat", "EPIC")
def witch_hat():
    v = Vox("witch_hat")
    p1, p2, band, buckle = C("3e2466"), C("2a1848"), C("4fe0a0"), C("f2c230")
    v.disc(8, 8, 7.4, 11, p2)
    cone(v, 8, 8, 4.6, 12, 10, p1, lean=(-2.5, 3.0), r1=0.7)
    v.disc(8, 8, 4.7, 12, band, r_in=3.7, y1=14)
    v.set(8, 13, 3, buckle)
    return v


@hat("graduation_cap", "Graduation Cap", "RARE")
def graduation_cap():
    v = Vox("graduation_cap")
    black, edge, gold = C("1c1c22"), C("2e2e38"), C("e0b13a")
    v.box(3, 11, 3, 13, 14, 13, black)
    v.box(1, 14, 1, 15, 15, 15, lambda x, y, z: edge if (x in (1, 14) or z in (1, 14)) else black)
    v.set(8, 15, 8, gold)
    for x in range(8, 14):
        v.set(x, 15, 8, gold)
    for y in range(9, 14):
        v.set(14, y, 8, gold)
    v.box(14, 7, 8, 15, 9, 9, gold)
    return v


@hat("traffic_cone", "Traffic Cone", "COMMON")
def traffic_cone():
    v = Vox("traffic_cone")
    o, w, black = C("f2671f"), C("f4f4f4"), C("1c1c22")
    v.box(2, 12, 2, 14, 13, 14, black)
    cone(v, 8, 8, 4.4, 13, 10, lambda x, y, z: w if y in (16, 17, 20) else o, r1=1.0)
    return v


@hat("winter_hat", "Winter Hat", "RARE")
def winter_hat():
    v = Vox("winter_hat")
    b1, b2, w = C("2f62c0"), C("1f4590"), C("f4f4f4")
    sq_ring(v, 3, 3, 13, 13, 10, 12, lambda x, y, z: w if (x + z + y) % 2 == 0 else b2)
    v.box(3, 12, 3, 13, 14, 13, noise(b1, 0.06, 12))
    v.box(4, 14, 4, 12, 15, 12, b1)
    v.box(7, 15, 7, 9, 17, 9, w)
    for x in (2, 13):
        v.box(x, 5, 6, x + 1, 11, 10, b1)
        v.set(x, 4, 8, w); v.set(x, 3, 8, w); v.set(x, 2, 8, w)
    return v


@hat("coral_crown", "Coral Crown", "EPIC")
def coral_crown():
    v = Vox("coral_crown")
    teal, pink, orange, shell = C("2fb8a0"), C("f2708a"), C("f2a03a"), C("f6eee0")
    sq_ring(v, 3, 3, 13, 13, 12, 13, teal)
    for i, (x, z) in enumerate(((3, 4), (6, 3), (12, 5), (12, 10), (8, 12), (3, 10))):
        col = pink if i % 2 == 0 else orange
        h = 3 + (i % 2)
        v.box(x, 13, z, x + 1, 13 + h, z + 1, col)
        v.set(x + (1 if x < 8 else -1), 14 + (i % 2), z, col)
        v.set(x + (1 if x < 8 else -1), 15 + (i % 2), z, col)
    v.box(9, 13, 2, 11, 15, 3, shell)
    return v


@hat("gem_tiara", "Gem Tiara", "LEGENDARY")
def gem_tiara():
    v = Vox("gem_tiara")
    silver, shine, gem, gem2 = C("dfe3ea"), C("ffffff"), C("a65cff"), C("e6c8ff")
    sq_ring(v, 3, 3, 13, 13, 12, 13, silver)
    for x in range(3, 13):
        h = 1 + max(0, 3 - abs(x - 7.5) // 1.5)
        v.box(x, 13, 3, x + 1, 13 + int(h), 4, silver)
    v.box(7, 14, 2, 9, 16, 3, gem)
    v.set(7, 15, 2, gem2)
    v.set(8, 17, 3, shine)
    v.set(5, 14, 2, gem); v.set(10, 14, 2, gem)
    return v


@hat("snorkel_mask", "Snorkel Mask", "RARE")
def snorkel_mask():
    v = Vox("snorkel_mask")
    y1, glass, strap, o, w = C("f2c418"), C("bfe9ff"), C("1c1c22"), C("f2671f"), C("f4f4f4")
    sq_ring(v, 3, 3, 13, 13, 8, 9, strap)
    v.box(4, 6, 2, 12, 11, 3, y1)
    v.box(5, 7, 1, 11, 10, 2, lambda x, y, z: glass if (x + y) % 2 else shade(glass, 0.9))
    for y in range(4, 16):
        v.set(2, y, 6, o if (y // 2) % 2 else w)
    v.set(2, 4, 5, o); v.set(2, 4, 4, o)
    return v


@hat("antenna_band", "Antenna Band", "COMMON")
def antenna_band():
    v = Vox("antenna_band")
    band, stalk, ball, glow = C("2e2e38"), C("1c1c22"), C("5af08a"), C("c8ffd8")
    slab(v, 3, 7, 13, 9, 12, band)
    for x, lean in ((5, -1), (10, 1)):
        v.set(x, 13, 8, stalk); v.set(x, 14, 8, stalk); v.set(x + lean, 15, 8, stalk); v.set(x + lean, 16, 8, stalk)
        v.box(x + lean - (1 if lean < 0 else 0), 17, 7, x + lean + (1 if lean > 0 else 0) + (0 if lean > 0 else 1), 19, 9, ball)
        v.set(x + lean, 18, 7, glow)
    return v


@hat("welding_mask", "Welding Mask", "RARE")
def welding_mask():
    v = Vox("welding_mask")
    g1, g2, glass, y1, black = C("4a5060"), C("343846"), C("1a2a1e"), C("f2c418"), C("1c1c22")
    sq_ring(v, 3, 3, 13, 13, 9, 10, black)
    v.box(3, 12, 1, 13, 14, 12, g1)
    v.box(4, 14, 2, 12, 15, 11, g2)
    v.box(5, 14, 3, 11, 15, 6, glass)
    for x in range(3, 13):
        v.set(x, 13, 1, y1 if x % 2 == 0 else black)
    return v


@hat("gear_crown", "Gear Crown", "EPIC")
def gear_crown():
    v = Vox("gear_crown")
    b1, b2, glow = C("9a6a3a"), C("6b4423"), C("41e0ff")
    sq_ring(v, 3, 3, 13, 13, 11, 13, b1)
    for x in range(2, 14):
        for z in range(2, 14):
            if (x in (2, 13) or z in (2, 13)) and (x + z) % 3 == 0 and not (x in (2, 13) and z in (2, 13)):
                v.box(x, 11, z, x + 1, 13, z + 1, b2)
    sq_ring(v, 3, 3, 13, 13, 13, 14, lambda x, y, z: b2 if (x + z) % 2 == 0 else None)
    for x, z in ((3, 3), (12, 3), (3, 12), (12, 12), (8, 2)):
        v.set(x, 12, z, glow)
    return v
