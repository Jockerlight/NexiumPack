"""The 36 back items, in body space: torso x 4..12, y 2..14, z 6..10, the
player looks towards +z, the back is the z = 6 side. Items live at z < 6.
The player's left is +x."""
import math
from vox import Vox, shade, mix
from shapes import C, slab, sq_ring, circle_pts, noise
import sprite as S

BACKS = []


def back(id, name, rarity):
    def deco(fn):
        BACKS.append((id, name, rarity, fn))
        return fn
    return deco


def wings(v, tex, W=14, H=14, root_y=11.5, z=5.0, sweep=22.5, gap=1.0, root_frac=13 / 32):
    """Two textured planes (left + mirrored right), swept back."""
    y_top = root_y + root_frac * H
    y_bot = y_top - H
    xl = 8 + gap
    xr = 8 - gap
    v.plane([xl, y_bot, z], [xl + W, y_top, z], tex,
            {"north": [0, 0, 16, 16], "south": [16, 0, 0, 16]}, rot=("y", sweep, [xl, root_y, z]))
    v.plane([xr - W, y_bot, z], [xr, y_top, z], tex,
            {"north": [16, 0, 0, 16], "south": [0, 0, 16, 16]}, rot=("y", -sweep, [xr, root_y, z]))


def mount(v, c, y0=9, y1=13):
    """A small block between the shoulder blades that wings sit on."""
    v.box(7, y0, 4, 9, y1, 6, c)


def straps(v, c, y0=3, y1=14):
    for x in (5, 10):
        v.box(x, y0, 5, x + 1, y1, 6, c)


def tank(v, x0, z0, y0, y1, c, band=None, r=1.6):
    for y in range(y0, y1):
        col = band if band and y in (y0 + 2, y1 - 3) else c
        v.disc(x0, z0, r, y, col)


def flame(v, x, z, y):
    v.set(x, y, z, C("ffd24a"))
    v.set(x, y - 1, z, C("ff8a1e"))
    v.set(x, y - 2, z, C("e8421e"))


# ------------------------------------------------------------------ wings
@back("crystal_wings", "Crystal Wings", "LEGENDARY")
def crystal_wings():
    v = Vox("crystal_wings")
    tex = S.spike_wing("wing_crystal", C("3a8fd8"), C("9ce8ff"), C("f0ffff"), n=8)
    wings(v, tex, W=15, H=14)
    mount(v, C("bfe9ff"))
    return v


@back("bee_wings", "Bee Wings", "RARE")
def bee_wings():
    v = Vox("bee_wings")
    tex = S.insect_wing("wing_bee", C("aab8cc"), C("6f7c92"), C("8794aa"), glassy=True)
    wings(v, tex, W=12, H=12, sweep=22.5)
    mount(v, C("f2c418"), 9, 12)
    v.set(7, 10, 3, C("1c1c22")); v.set(8, 10, 3, C("1c1c22"))
    return v


@back("angel_wings", "Angel Wings", "LEGENDARY")
def angel_wings():
    v = Vox("angel_wings")
    tex = S.feather_wing("wing_angel", C("f4f6fa"), C("c9d0de"), C("ffffff"), accent=C("f2c230"))
    wings(v, tex, W=15, H=15)
    mount(v, C("f2c230"))
    return v


@back("bat_wings", "Bat Wings", "EPIC")
def bat_wings():
    v = Vox("bat_wings")
    tex = S.membrane_wing("wing_bat", C("3a2a4a"), C("4e3a63"), C("2a1e36"))
    wings(v, tex, W=15, H=15)
    mount(v, C("2a1e36"))
    return v


@back("butterfly_wings", "Butterfly Wings", "EPIC")
def butterfly_wings():
    v = Vox("butterfly_wings")
    spots = [(5, 6), (3, 10), (9, 3), (14, 2), (24, 28), (16, 29)]
    tex = S.insect_wing("wing_butterfly", C("f08a1e"), C("1c1c22"), C("1c1c22"), spots=spots)
    wings(v, tex, W=12, H=13)
    mount(v, C("1c1c22"))
    return v


@back("dragon_wings", "Dragon Wings", "MYTHIC")
def dragon_wings():
    v = Vox("dragon_wings")
    tex = S.membrane_wing("wing_dragon", C("2f8a3a"), C("4fb84a"), C("e8dcb0"), claw=C("f6eee0"))
    wings(v, tex, W=16, H=16)
    mount(v, C("2a6a30"))
    return v


@back("phoenix_wings", "Phoenix Wings", "MYTHIC")
def phoenix_wings():
    v = Vox("phoenix_wings")
    tex = S.feather_wing("wing_phoenix", C("ff6a1e"), C("d8201e"), C("ffd24a"), accent=C("fff0a0"))
    wings(v, tex, W=16, H=15)
    mount(v, C("ffb02e"))
    return v


@back("mech_wings", "Mech Wings", "LEGENDARY")
def mech_wings():
    v = Vox("mech_wings")
    tex = S.blade_wing("wing_mech", C("a8b2c2"), C("5c6678"), C("dfe6f0"), C("41e0ff"))
    wings(v, tex, W=14, H=13)
    v.box(6, 7, 3, 10, 13, 6, C("5c6678"))
    v.box(7, 8, 2, 9, 10, 3, C("41e0ff"))
    return v


@back("frost_wings", "Frost Wings", "LEGENDARY")
def frost_wings():
    v = Vox("frost_wings")
    tex = S.feather_wing("wing_frost", C("e8f6ff"), C("5ab8ee"), C("ffffff"), accent=C("9ce8ff"), spiky=True)
    wings(v, tex, W=15, H=15)
    mount(v, C("bfe9ff"))
    return v


@back("leaf_wings", "Leaf Wings", "RARE")
def leaf_wings():
    v = Vox("leaf_wings")
    tex = S.leaf_wing("wing_leaf", C("5cc84a"), C("2f7a2a"), C("b8f0a0"))
    wings(v, tex, W=13, H=13)
    mount(v, C("6b4423"))
    return v


# ------------------------------------------------------------------ capes
def cape_plane(v, tex, y_top=14.5, H=22, x0=3, x1=13, z=5.5):
    v.plane([x0, y_top - H, z], [x1, y_top, z], tex, {"north": [16, 0, 0, 16], "south": [0, 0, 16, 16]},
            rot=("x", 22.5, [8, y_top, z]))


@back("royal_cape", "Royal Cape", "LEGENDARY")
def royal_cape():
    v = Vox("royal_cape")
    tex = S.cape("cape_royal", C("a3123a"), C("8a0f30"), C("f2c230"), C("dfe3ea"))
    cape_plane(v, tex)
    return v


@back("frost_cape", "Frost Cape", "EPIC")
def frost_cape():
    v = Vox("frost_cape")

    def flake(im):
        for x, y in ((8, 8), (7, 7), (9, 9), (7, 9), (9, 7), (8, 6), (8, 10), (6, 8), (10, 8)):
            im.putpixel((x, y), (240, 250, 255, 255))
    tex = S.cape("cape_frost", C("3a8fd8"), C("2f74b8"), C("ffffff"), C("e8f6ff"), emblem=flake)
    cape_plane(v, tex)
    return v


@back("cape_banner", "Cape Banner", "RARE")
def cape_banner():
    v = Vox("cape_banner")

    def diamond(im):
        for x, y in ((8, 7), (7, 8), (9, 8), (8, 9), (6, 9), (10, 9), (7, 10), (9, 10), (8, 11)):
            im.putpixel((x, y), (65, 224, 255, 255))
    tex = S.cape("banner_cyan", C("1e2a4a"), C("24345a"), C("41e0ff"), C("d9a536"), emblem=diamond)
    v.plane([4, 0, 5], [12, 16, 5], tex, {"north": [16, 0, 0, 16], "south": [0, 0, 16, 16]})
    v.box(3, 15, 4, 13, 16, 5, C("d9a536"))
    return v


# ------------------------------------------------------------------ voxel items
@back("compact_jetpack", "Compact Jetpack", "RARE")
def compact_jetpack():
    v = Vox("compact_jetpack")
    gray, dark, orange = C("9aa4b4"), C("5c6678"), C("f08a1e")
    for x in (5.5, 10.5):
        tank(v, x, 3.5, 5, 13, gray, band=orange)
        flame(v, math.floor(x), 3, 4)
    v.box(7, 6, 4, 9, 12, 6, dark)
    straps(v, C("3a3d4a"))
    return v


@back("tool_backpack", "Tool Backpack", "COMMON")
def tool_backpack():
    v = Vox("tool_backpack")
    b1, b2, buckle = C("8a5a32"), C("6b4423"), C("d9b24a")
    v.box(4, 3, 3, 12, 12, 6, noise(b1, 0.06, 4))
    v.box(5, 4, 2, 11, 8, 3, b2)
    v.set(8, 7, 2, buckle)
    v.box(9, 12, 4, 10, 16, 5, C("8a6a4a"))
    v.box(8, 15, 4, 11, 16, 5, C("9aa4b4"))
    v.box(5, 12, 4, 7, 14, 5, C("c8324a"))
    return v


@back("fish_tank", "Fish Tank", "EPIC")
def fish_tank():
    v = Vox("fish_tank")
    frame, water, light, fish = C("4a5060"), C("3a8fd8"), C("8fd3f5"), C("f08a1e")
    v.frame(4, 3, 2, 12, 12, 6, frame)
    v.box(5, 4, 2, 11, 10, 3, water)
    v.box(5, 10, 2, 11, 11, 3, light)
    v.set(7, 7, 2, fish); v.set(8, 7, 2, fish); v.set(9, 6, 2, fish); v.set(9, 8, 2, fish)
    v.set(6, 5, 2, light)
    return v


@back("tractor_toolcase", "Tractor Toolcase", "RARE")
def tractor_toolcase():
    v = Vox("tractor_toolcase")
    red, dark, yel = C("c8324a"), C("8a1f30"), C("f2c418")
    v.box(4, 3, 3, 12, 12, 6, red)
    v.box(4, 7, 2, 12, 8, 3, dark)
    v.box(6, 4, 2, 10, 6, 3, lambda x, y, z: yel if (x + y) % 2 else dark)
    v.box(6, 12, 4, 10, 13, 5, dark)
    v.box(6, 13, 4, 7, 14, 5, dark); v.box(9, 13, 4, 10, 14, 5, dark)
    return v


@back("dragon_spines", "Dragon Spines", "EPIC")
def dragon_spines():
    v = Vox("dragon_spines")
    p1, p2, tip = C("8a55e8"), C("5b2fb5"), C("f0e2ff")
    for i, y in enumerate(range(3, 14, 2)):
        v.box(7, y, 4, 9, y + 2, 6, p2)
        v.box(7, y + 1, 3, 9, y + 2, 4, p1)
        v.set(8 if i % 2 else 7, y + 1, 2, tip)
    return v


@back("energy_cell", "Energy Cell", "RARE")
def energy_cell():
    v = Vox("energy_cell")
    dark, glow, cap = C("2a2e3a"), C("41e0ff"), C("8a92a3")
    tank(v, 8, 3.5, 3, 13, dark, r=2.6)
    for y in (5, 8, 11):
        v.disc(8, 3.5, 2.6, y, glow)
    v.disc(8, 3.5, 1.8, 13, cap)
    v.disc(8, 3.5, 1.8, 2, cap)
    straps(v, dark)
    return v


@back("neon_battery", "Neon Battery", "RARE")
def neon_battery():
    v = Vox("neon_battery")
    dark, pink, hot = C("2a2232"), C("ff5ccf"), C("ffc4ef")
    v.box(5, 3, 3, 11, 12, 6, dark)
    for x in (5, 10):
        v.box(x, 4, 2, x + 1, 11, 3, pink)
    v.box(6, 10, 2, 10, 11, 3, hot)
    v.box(7, 12, 4, 9, 13, 5, C("8a92a3"))
    return v


@back("hiking_bag", "Hiking Bag", "COMMON")
def hiking_bag():
    v = Vox("hiking_bag")
    g1, g2, tan, strap = C("4f8a3a"), C("3a6a2a"), C("d9b77a"), C("2a3a22")
    v.box(4, 3, 3, 12, 12, 6, noise(g1, 0.06, 6))
    v.box(5, 4, 2, 11, 8, 3, g2)
    v.box(3, 12, 3, 13, 14, 6, tan)
    v.box(3, 12, 3, 4, 14, 6, shade(tan, 0.8)); v.box(12, 12, 3, 13, 14, 6, shade(tan, 0.8))
    v.box(7, 8, 2, 9, 9, 3, strap)
    return v


@back("quiver", "Quiver", "COMMON")
def quiver():
    v = Vox("quiver")
    leather, dark, shaft, red, white = C("a8743a"), C("6b4423"), C("8a6a4a"), C("d8323a"), C("f4f4f4")
    v.line((10.5, 3, 4), (5.5, 12, 4), leather, r=1.1)
    v.line((11, 2, 4), (11.5, 3, 4), dark, r=0.6)
    for k, (dx, dz) in enumerate(((0, 0), (1, 0), (0, -1))):
        x0, y0 = 5 + dx, 12
        v.line((x0, y0, 4 + dz), (x0 - 2, y0 + 3, 4 + dz), shaft)
        v.set(x0 - 2, y0 + 3, 4 + dz, red if k % 2 == 0 else white)
        v.set(x0 - 3, y0 + 3, 4 + dz, red)
    v.line((12, 2, 5), (3, 14, 5), dark)
    return v


@back("shield_emblem", "Shield Emblem", "EPIC")
def shield_emblem():
    v = Vox("shield_emblem")
    gold, blue, dark, red = C("e0b13a"), C("2f5ea8"), C("1e3a6a"), C("d8323a")
    for x in range(2, 15):
        for y in range(1, 15):
            d = math.hypot(x + 0.5 - 8, y + 0.5 - 8)
            if d <= 5.6:
                v.set(x, y, 4, gold if d > 4.6 else (blue if (x + y) % 2 else dark))
    v.box(7, 6, 3, 9, 10, 4, red)
    v.box(6, 7, 3, 10, 9, 4, red)
    v.box(5, 5, 5, 11, 11, 6, dark)
    return v


@back("gear_wheel", "Gear Wheel", "RARE")
def gear_wheel():
    v = Vox("gear_wheel")
    b1, b2, hub = C("b07a3a"), C("7a4a22"), C("3a2616")
    for x in range(1, 16):
        for y in range(1, 16):
            dx, dy = x + 0.5 - 8.5, y + 0.5 - 8.5
            d = math.hypot(dx, dy)
            a = math.atan2(dy, dx)
            tooth = math.cos(a * 8) > 0.4
            if 2.0 < d <= 5.2 or (5.2 < d <= 6.6 and tooth):
                v.set(x, y, 4, b1 if d < 5 else b2)
            elif d <= 2.0:
                v.set(x, y, 4, hub)
    for x in range(3, 8):
        for y in range(2, 7):
            d = math.hypot(x + 0.5 - 5, y + 0.5 - 4.5)
            if 0.9 < d <= 2.3:
                v.set(x, y, 3, C("d9a536"))
    v.box(7, 7, 5, 10, 10, 6, hub)
    return v


@back("solar_panel", "Solar Panel", "EPIC")
def solar_panel():
    v = Vox("solar_panel")
    cell, grid, frame, gold = C("2f5ea8"), C("8fb8e8"), C("c4cad6"), C("e0b13a")
    for x0, x1 in ((-5, 7), (9, 21)):
        for x in range(x0, x1):
            for y in range(6, 13):
                edge = x in (x0, x1 - 1) or y in (6, 12)
                v.set(x, y, 4, frame if edge else (grid if (x % 3 == 0 or y % 3 == 0) else cell))
    v.box(7, 6, 3, 9, 13, 6, gold)
    return v


@back("void_orb", "Void Orb", "LEGENDARY")
def void_orb():
    v = Vox("void_orb")
    core, glow, ring = C("4a2a7a"), C("c79bff"), C("e5d4ff")
    v.ellipsoid(8, 9, 1.5, 2.4, 2.4, 2.4, lambda x, y, z: glow if (x + y + z) % 3 == 0 else core)
    for x, z in circle_pts(8, 1.5, 3.6, 12):
        v.set(math.floor(x), 9, math.floor(z), ring)
    return v


@back("rocket_pack", "Rocket Pack", "EPIC")
def rocket_pack():
    v = Vox("rocket_pack")
    red, white, glass, gray = C("d8323a"), C("f4f4f4"), C("8fd3f5"), C("9aa4b4")
    for y in range(4, 14):
        r = 2.1 if y < 11 else (1.5 if y < 13 else 0.8)
        v.disc(8, 3.5, r, y, red if (y // 2) % 2 else white)
    v.set(8, 10, 1, glass); v.set(7, 10, 1, glass)
    for x, z in ((5, 3), (10, 3)):
        v.box(x, 4, z, x + 1, 7, z + 1, red)
    flame(v, 7, 3, 3); flame(v, 8, 3, 3)
    v.box(7, 6, 5, 9, 12, 6, gray)
    return v


@back("retro_jetpack", "Retro Jetpack", "RARE")
def retro_jetpack():
    v = Vox("retro_jetpack")
    copper, dark, brass = C("b8743a"), C("7a4a22"), C("d9b24a")
    for x in (5.5, 10.5):
        tank(v, x, 3.5, 5, 13, lambda xx, y, z: brass if y in (7, 11) else copper)
        v.disc(x, 3.5, 1.0, 13, dark)
        flame(v, math.floor(x), 3, 4)
    v.box(7, 6, 4, 9, 12, 6, dark)
    straps(v, C("3a2616"))
    return v


@back("rod_on_back", "Rod on Back", "COMMON")
def rod_on_back():
    v = Vox("rod_on_back")
    rod, grip, line, bob, basket = C("8a5a32"), C("3a2616"), C("dfe3ea"), C("d8323a"), C("c9a046")
    v.line((10, 1, 4), (5, 17, 4), rod)
    v.line((10, 1, 4), (9.5, 3, 4), grip, r=0.6)
    v.line((5, 17, 3), (4, 14, 3), line)
    v.set(4, 13, 3, bob)
    v.box(9, 3, 3, 13, 7, 6, lambda x, y, z: basket if (x + y) % 2 else shade(basket, 0.8))
    v.box(9, 7, 3, 13, 8, 6, C("7a4a22"))
    return v


@back("crossed_picks", "Crossed Picks", "EPIC")
def crossed_picks():
    v = Vox("crossed_picks")
    handle, head, dark = C("8a5a32"), C("aeb6c4"), C("6e7686")
    v.line((3, 2, 4), (13, 13, 4), handle)
    v.line((13, 2, 3), (3, 13, 3), handle)
    for (cx, cy, z, s) in ((13, 13, 4, 1), (3, 13, 3, -1)):
        v.line((cx - s * 3, cy - 1, z), (cx, cy + 1, z), head)
        v.line((cx, cy + 1, z), (cx + s * 2, cy - 2, z), head)
        v.set(cx - s * 3, cy - 2, z, dark)
        v.set(cx + s * 2, cy - 3, z, dark)
    return v


@back("harvest_basket", "Harvest Basket", "COMMON")
def harvest_basket():
    v = Vox("harvest_basket")
    w1, w2 = C("c9a046"), C("8a6a2a")
    v.box(4, 3, 2, 12, 10, 6, lambda x, y, z: w1 if (x + y) % 2 else w2)
    v.box(5, 10, 3, 11, 11, 5, C("6b4423"))
    v.box(5, 10, 3, 7, 12, 5, C("d8323a"))
    v.box(8, 10, 3, 10, 12, 4, C("f08a1e"))
    v.box(9, 12, 3, 10, 13, 4, C("4f9a3a"))
    v.box(10, 10, 4, 11, 12, 5, C("5cc84a"))
    return v


@back("scuba_tank", "Scuba Tank", "RARE")
def scuba_tank():
    v = Vox("scuba_tank")
    y1, black, gray = C("f2c418"), C("1c1c22"), C("9aa4b4")
    for x in (6, 10):
        tank(v, x, 3.5, 3, 12, lambda xx, y, z: black if y == 6 else y1, r=1.9)
        v.box(x - 1, 12, 3, x + 1, 14, 4, gray)
        v.set(x - 1, 14, 3, black)
    v.box(7, 9, 2, 9, 10, 3, gray)
    return v


@back("turtle_shell", "Turtle Shell", "RARE")
def turtle_shell():
    v = Vox("turtle_shell")
    g1, g2, g3, rim = C("4f9a3a"), C("2f6a2a"), C("8ac85a"), C("d9a536")
    for x in range(3, 13):
        for y in range(2, 14):
            edge = x in (3, 12) or y in (2, 13)
            v.set(x, y, 5, rim if edge else g2)
            if not edge:
                inner = (x - 3) % 3 == 0 or (y - 2) % 4 == 0
                v.set(x, y, 4, g2 if inner else g1)
                if 5 <= x <= 10 and 4 <= y <= 11 and not inner:
                    v.set(x, y, 3, g3 if (x + y) % 3 else g1)
    return v


@back("guitar", "Guitar", "EPIC")
def guitar():
    v = Vox("guitar")
    red, white, neck, head, black = C("c8324a"), C("f4f4f4"), C("8a5a32"), C("1c1c22"), C("2a2a32")
    v.ellipsoid(5.5, 5, 3.5, 3.0, 3.6, 1.2, red)
    v.box(4, 3, 2, 7, 6, 3, white)
    v.line((6, 7, 3), (12, 15, 3), neck, r=0.6)
    v.box(11, 15, 3, 14, 17, 4, head)
    v.line((3, 1, 5), (14, 15, 5), black)
    return v


@back("crystal_quiver", "Crystal Quiver", "EPIC")
def crystal_quiver():
    v = Vox("crystal_quiver")
    tube, dark, c1, c2 = C("6a4aa8"), C("3e2a6a"), C("c79bff"), C("f0e2ff")
    v.line((10.5, 3, 4), (5.5, 12, 4), tube, r=1.1)
    v.line((9.5, 5, 3), (6.5, 10, 3), dark)
    for k, (dx, dz) in enumerate(((0, 0), (1, 0), (-1, 0))):
        v.line((5 + dx, 12, 4 + dz), (4 + dx, 15, 4 + dz), c1)
        v.set(4 + dx, 15, 4 + dz, c2)
    v.line((12, 2, 5), (3, 14, 5), dark)
    return v


@back("propeller_pack", "Propeller Pack", "LEGENDARY")
def propeller_pack():
    v = Vox("propeller_pack")
    rim, housing, blade, hub = C("e0b13a"), C("c8324a"), C("41b8e0"), C("1c1c22")
    for x in range(1, 16):
        for y in range(1, 16):
            dx, dy = x + 0.5 - 8.5, y + 0.5 - 8.5
            d = math.hypot(dx, dy)
            if d <= 6.6:
                v.set(x, y, 4, rim if d > 5.6 else housing)
                if d <= 5.4 and (abs(dx - dy) < 1.2 or abs(dx + dy) < 1.2):
                    v.set(x, y, 3, blade)
    v.box(8, 8, 2, 9, 9, 3, hub)
    v.box(6, 6, 5, 11, 11, 6, hub)
    return v
