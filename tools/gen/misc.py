"""The Skin Crate (block size, 0..16) and its lid, in HD."""
import math

from hd import (Model, box, rbox, ellipsoid, sphere, cyl, cyl_z, torus, cone, prism, half, solid, gold, velvet, gem,
                glow, metal, silver, crystal, wood)
from parts import set_gem, rivets, star_points


def skin_crate():
    base = Model("skin_crate", (-1, -1, -1), (17, 17, 17))
    G = gold()
    R = velvet("a3123a")
    base.fill(rbox(1.0, 0.0, 2.0, 15.0, 9.0, 14.0, 0.4), wood("7a1a2a"))
    # planks
    for z in (4.6, 7.2, 9.8, 12.4):
        base.paint(box(0, 0, z - 0.1, 16, 9, z + 0.1), wood("4a0e1a"))
    for x in (4.6, 8.0, 11.4):
        base.paint(box(x - 0.1, 0, 0, x + 0.1, 9, 16), wood("4a0e1a"))
    # gold frame: corner posts, bottom + top rims
    for x in (1.0, 14.0):
        for z in (2.0, 13.0):
            base.fill(rbox(x - 0.25, 0, z - 0.25, x + 1.25, 9.0, z + 1.25, 0.3), G)
    base.fill(rbox(0.75, 0, 1.75, 15.25, 0.9, 14.25, 0.3), G)
    base.fill(rbox(0.75, 8.2, 1.75, 15.25, 9.0, 14.25, 0.3), G)
    rivets(base, [(x, 0.45, 1.65) for x in (3.0, 5.5, 8.0, 10.5, 13.0)], gold(), 0.2)
    # lock plate + keyhole
    base.fill(rbox(6.0, 2.8, 1.2, 10.0, 8.2, 2.1, 0.4), G)
    base.fill(cyl_z(8, 5.8, 0.55, 1.0, 1.3), solid("1c1c22", 0.1))
    base.fill(box(7.8, 4.4, 1.0, 8.2, 5.6, 1.3), solid("1c1c22", 0.1))
    set_gem(base, (8, 7.3, 1.15), "-z", 0.45, "41e0ff", G)
    # side handles
    for x in (0.6, 15.4):
        base.fill(torus(0, 0, 0, 1.1, 0.22).rot("z", 90, (0, 0, 0)).move(x, 5.6, 8) & half("y", 5.6, above=False), silver())
    lid = Model("skin_crate_lid", (-1, -1, -1), (17, 17, 17))
    lid.fill(rbox(1.0, 9.0, 2.0, 15.0, 13.4, 14.0, 0.6), wood("6a1424"))
    lid.fill(cyl_x_round(9.0, 13.2), velvet("8a1a2e"))
    for x in (1.0, 7.25, 14.0):
        lid.fill(rbox(x - 0.25, 9.0, 1.75, x + (1.5 if x == 7.25 else 1.25), 14.6, 14.25, 0.4), G)
    lid.fill(rbox(0.75, 9.0, 1.75, 15.25, 9.8, 14.25, 0.3), G)
    set_gem(lid, (8, 14.7, 8.0), "+y", 0.9, "41e0ff", G)
    for x in (4.2, 11.8):
        lid.fill(prism(star_points(0, 0, 0.9, 0.38), "z", 1.6, 1.85).move(x, 11.6, 0), glow("ffd54a", 13))
    return base, lid


def cyl_x_round(y0, y1):
    """Rounded lid top (half cylinder along x)."""
    from hd import Shape
    import numpy as np
    r = 6.0

    def fn(X, Y, Z):
        return (X >= 1.3) & (X < 14.7) & ((Y - (y1 - r)) ** 2 + (Z - 8) ** 2 <= r * r) & (Y >= y0) & (np.abs(Z - 8) < 5.9)
    return Shape(fn, ((1.3, y0, 2.0), (14.7, y1 + 0.1, 14.0)))
