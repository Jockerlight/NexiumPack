#!/usr/bin/env python3
"""Draws the sample art of the resource pack: the test pickaxe skin (32x32)
and the pack icon (128x128, shown in the pack prompt and pack list).

    python tools/draw_test_art.py

Writes pack/assets/nexium/textures/item/test_pickaxe.png and
pack/pack.png. Only samples to try the pack out: replace the PNGs
with real art any time (and stop running this script).
"""
import math
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pack/assets/nexium/textures/item/test_pickaxe.png"
ICON = ROOT / "pack/pack.png"
N = 32

OUTLINE = (12, 30, 34, 255)
CRYSTAL = [(20, 110, 80), (40, 190, 120), (62, 224, 127), (39, 231, 231), (170, 255, 240)]
HANDLE_DARK = (52, 34, 70, 255)
HANDLE_LIGHT = (104, 78, 140, 255)
GOLD = (255, 216, 74, 255)
GOLD_DARK = (196, 140, 30, 255)


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def crystal(t, light):
    """t: 0..1 along the arc (colour shift), light: 0..1 (dark inner edge .. bright outer edge)."""
    base = lerp(CRYSTAL[1], CRYSTAL[3], t)
    if light < 0.5:
        c = lerp(CRYSTAL[0], base, light * 2)
    else:
        c = lerp(base, CRYSTAL[4], (light - 0.5) * 1.4)
    return c + (255,)


def main():
    px = [[None] * N for _ in range(N)]
    # handle: bottom left to the middle of the head
    hx0, hy0, hx1, hy1 = 4.5, 27.5, 19.0, 13.0
    for y in range(N):
        for x in range(N):
            cx, cy = x + 0.5, y + 0.5
            dx, dy = hx1 - hx0, hy1 - hy0
            t = ((cx - hx0) * dx + (cy - hy0) * dy) / (dx * dx + dy * dy)
            if 0 <= t <= 1:
                qx, qy = hx0 + t * dx, hy0 + t * dy
                d = math.hypot(cx - qx, cy - qy)
                if d <= 1.25:
                    band = int(t * 14)
                    if 0.80 <= t <= 0.90:
                        px[y][x] = GOLD if (x + y) % 2 == 0 else GOLD_DARK
                    else:
                        px[y][x] = HANDLE_LIGHT if band % 2 == 0 else HANDLE_DARK
    # head: a crescent around a point on the handle line, bulging up-right
    ux, uy = 1 / math.sqrt(2), -1 / math.sqrt(2)
    R = 13.0
    ccx, ccy = 21.0 - ux * R, 11.0 - uy * R
    for y in range(N):
        for x in range(N):
            cx, cy = x + 0.5, y + 0.5
            vx, vy = cx - ccx, cy - ccy
            r = math.hypot(vx, vy)
            ang = math.atan2(vy, vx) - math.atan2(uy, ux)
            ang = (ang + math.pi) % (2 * math.pi) - math.pi
            span = math.radians(62)
            if abs(ang) > span:
                continue
            k = abs(ang) / span
            thick = 4.2 * (1 - k ** 1.6) + 0.6
            inner, outer = R - thick * 0.45, R + thick * 0.55
            if inner <= r <= outer:
                light = (r - inner) / max(0.01, outer - inner)
                t = (ang / span + 1) / 2
                # facets: a darker line through the middle of the crystal
                if abs(r - R) < 0.35 and k < 0.75:
                    light *= 0.55
                px[y][x] = crystal(t, light)
    # sparkle
    for (x, y) in [(23, 6), (12, 9)]:
        if px[y][x] is not None:
            px[y][x] = (240, 255, 250, 255)
    # outline: empty pixels touching a filled one
    out = [row[:] for row in px]
    for y in range(N):
        for x in range(N):
            if px[y][x] is None:
                for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + ddx, y + ddy
                    if 0 <= nx < N and 0 <= ny < N and px[ny][nx] is not None:
                        out[y][x] = OUTLINE
                        break
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    for y in range(N):
        for x in range(N):
            if out[y][x] is not None:
                img.putpixel((x, y), out[y][x])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, optimize=True)
    print("wrote", OUT)
    icon(img)


def icon(pick):
    """128x128: dark teal glow with the pickaxe in the middle."""
    S = 128
    im = Image.new("RGBA", (S, S))
    for y in range(S):
        for x in range(S):
            d = math.hypot(x - S / 2 + 0.5, y - S / 2 + 0.5) / (S * 0.72)
            c = lerp((22, 70, 64), (8, 14, 20), min(1.0, d))
            im.putpixel((x, y), c + (255,))
    big = pick.resize((96, 96), Image.NEAREST)
    shadow = Image.new("RGBA", big.size, (0, 0, 0, 0))
    shadow.putalpha(big.getchannel("A").point(lambda a: 110 if a else 0))
    im.alpha_composite(shadow, (18, 20))
    im.alpha_composite(big, (16, 16))
    im.save(ICON, optimize=True)
    print("wrote", ICON)


if __name__ == "__main__":
    main()
