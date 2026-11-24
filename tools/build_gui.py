#!/usr/bin/env python3
"""The blue title banner every menu gets (font nexium:gui).

    python tools/build_gui.py            writes the font + textures into pack/
    python tools/build_gui.py --preview  also previews/gui.png
    python tools/build_gui.py --java     prints the glyph widths for the plugin

The server's NexiumPack plugin rewrites each menu title (when it opens) to:
  <shift -16> <banner> <shift to centre> <title in this font>
so the banner hangs over the top edge of the menu and the name sits centred
on it. Menu titles are drawn at x 8, y 6 of the menu; a glyph's top lands at
y + 7 - ascent.

Writes (generated, don't edit by hand):
  pack/assets/nexium/font/gui.json
  pack/assets/nexium/textures/font/gui/{banner,bold,thin}.png
"""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "pack" / "assets" / "nexium"

MENU_W = 176          # every 9-wide menu
OVER = 8              # the banner reaches this far past each side
BANNER_W = MENU_W + 2 * OVER
BANNER_H = 24
BANNER_TOP = -9       # menu y of the banner's top edge
TEXT_TOP = 0          # menu y of the letters' top
CELL_W, CELL_H = 8, 14

WHITE = (255, 255, 255, 255)
SHADOW = (14, 38, 92, 255)

# 5x7 letters ('#' = pixel); narrower ones are simply narrower
GLYPHS = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
    "J": ["..###", "....#", "....#", "....#", "#...#", "#...#", ".###."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": [".#.", "##.", ".#.", ".#.", ".#.", ".#.", "###"],
    "2": [".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"],
    "3": [".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": ["..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."],
    ".": [".", ".", ".", ".", ".", ".", "#"],
    ",": [".", ".", ".", ".", ".", "#", "#"],
    ":": [".", ".", "#", ".", ".", "#", "."],
    ";": [".", ".", "#", ".", ".", "#", "#"],
    "!": ["#", "#", "#", "#", "#", ".", "#"],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "'": ["#", "#", ".", ".", ".", ".", "."],
    "\"": ["#.#", "#.#", "...", "...", "...", "...", "..."],
    "(": [".#", "#.", "#.", "#.", "#.", "#.", ".#"],
    ")": ["#.", ".#", ".#", ".#", ".#", ".#", "#."],
    "[": ["##", "#.", "#.", "#.", "#.", "#.", "##"],
    "]": ["##", ".#", ".#", ".#", ".#", ".#", "##"],
    "-": ["....", "....", "....", "####", "....", "....", "...."],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "=": [".....", ".....", "#####", ".....", "#####", ".....", "....."],
    "/": ["....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."],
    "&": [".##..", "#..#.", ".##..", ".##.#", "#..#.", "#..#.", ".##.#"],
    "%": ["##..#", "##.#.", "...#.", "..#..", ".#...", ".#.##", "#..##"],
    "#": [".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."],
    "_": [".....", ".....", ".....", ".....", ".....", ".....", "#####"],
    "<": ["...#", "..#.", ".#..", "#...", ".#..", "..#.", "...#"],
    ">": ["#...", ".#..", "..#.", "...#", "..#.", ".#..", "#..."],
    "*": [".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."],
    "»": [".....", "#.#..", ".#.#.", "..#.#", ".#.#.", "#.#..", "....."],
    "·": [".", ".", ".", "#", ".", ".", "."],
    "✔": [".....", "....#", "...#.", "#.#..", ".#...", ".....", "....."],
}
CHARS = list(GLYPHS)
SPACE_BOLD, SPACE_THIN = 5, 4
THIN_BASE = 0xE100     # thin glyph of CHARS[i] is chr(THIN_BASE + i)
THIN_SPACE = ""
BANNER = ""
# shifts: .. = -1, -2, -4 .. -256 ; .. = +1 .. +256
SHIFTS = {chr(0xF801 + i): -(1 << i) for i in range(9)}
SHIFTS.update({chr(0xF821 + i): 1 << i for i in range(9)})


def glyph(rows, bold):
    """Cell image (CELL_W x CELL_H): white letter, dark shadow 1 px down-right."""
    w = len(rows[0])
    on = set()
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch == "#":
                on.add((x, y))
                if bold:
                    on.add((x + 1, y))
    im = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
    for x, y in on:
        if (x + 1, y + 1) not in on:
            im.putpixel((x + 1, y + 1), SHADOW)
    for x, y in on:
        im.putpixel((x, y), WHITE)
    width = max(x for x, _ in on) + 2 if on else w   # letter + shadow column
    return im, width


def sheet(bold):
    cols = 16
    rows = (len(CHARS) + cols - 1) // cols
    im = Image.new("RGBA", (cols * CELL_W, rows * CELL_H), (0, 0, 0, 0))
    adv = {}
    for i, c in enumerate(CHARS):
        g, w = glyph(GLYPHS[c], bold)
        im.paste(g, ((i % cols) * CELL_W, (i // cols) * CELL_H))
        adv[c] = w + 1
    lines = []
    for r in range(rows):
        line = ""
        for k in range(cols):
            i = r * cols + k
            if i < len(CHARS):
                line += CHARS[i] if bold else chr(THIN_BASE + i)
            else:
                line += "\u0000"
        lines.append(line)
    return im, lines, adv


def banner():
    """192 x 24: a blue ribbon with a light inner frame and darker ends."""
    W, H = BANNER_W, BANNER_H
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    top, bot = (86, 152, 240), (38, 98, 196)
    for y in range(H):
        t = y / (H - 1)
        c = tuple(round(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,)
        for x in range(W):
            im.putpixel((x, y), c)
    dark = (11, 30, 70, 255)
    for x in range(W):
        im.putpixel((x, 0), dark)
        im.putpixel((x, H - 1), dark)
        im.putpixel((x, 1), (150, 198, 255, 255))
        im.putpixel((x, H - 2), (24, 66, 140, 255))
        im.putpixel((x, H - 3), (30, 80, 160, 255))
    for y in range(H):
        im.putpixel((0, y), dark)
        im.putpixel((W - 1, y), dark)
    # darker ends: the ribbon folds behind at both sides
    for y in range(1, H - 1):
        for x in range(1, 7):
            r, g, b, a = im.getpixel((x, y))
            im.putpixel((x, y), (int(r * 0.72), int(g * 0.72), int(b * 0.78), a))
            r, g, b, a = im.getpixel((W - 1 - x, y))
            im.putpixel((W - 1 - x, y), (int(r * 0.72), int(g * 0.72), int(b * 0.78), a))
        im.putpixel((7, y), dark)
        im.putpixel((W - 8, y), dark)
    # light inner frame
    frame = (170, 210, 255, 255)
    for x in range(10, W - 10):
        im.putpixel((x, 3), frame)
        im.putpixel((x, H - 5), (120, 170, 240, 255))
    for y in range(3, H - 4):
        im.putpixel((10, y), frame)
        im.putpixel((W - 11, y), (120, 170, 240, 255))
    return im


def font_json(bold_lines, thin_lines):
    adv = {" ": SPACE_BOLD, THIN_SPACE: SPACE_THIN}
    adv.update(SHIFTS)
    asc_text = 7 + 6 - TEXT_TOP
    return {"providers": [
        {"type": "space", "advances": adv},
        {"type": "bitmap", "file": "nexium:font/gui/banner.png", "height": BANNER_H,
         "ascent": 7 + 6 - BANNER_TOP, "chars": [BANNER]},
        {"type": "bitmap", "file": "nexium:font/gui/bold.png", "height": CELL_H, "ascent": asc_text,
         "chars": bold_lines},
        {"type": "bitmap", "file": "nexium:font/gui/thin.png", "height": CELL_H, "ascent": asc_text,
         "chars": thin_lines},
    ]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--java", action="store_true")
    a = ap.parse_args()
    b_im, b_lines, b_adv = sheet(True)
    t_im, t_lines, t_adv = sheet(False)
    d = PACK / "textures" / "font" / "gui"
    d.mkdir(parents=True, exist_ok=True)
    banner().save(d / "banner.png", optimize=True)
    b_im.save(d / "bold.png", optimize=True)
    t_im.save(d / "thin.png", optimize=True)
    f = PACK / "font" / "gui.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(font_json(b_lines, t_lines), ensure_ascii=True, separators=(",", ":")), encoding="utf-8")
    if a.java:
        chars = "".join(CHARS)
        print('CHARS = "%s";' % chars.encode("unicode_escape").decode().replace('"', '\\"'))
        print('BOLD  = "%s";' % "".join(chr(ord("0") + b_adv[c]) for c in CHARS))
        print('THIN  = "%s";' % "".join(chr(ord("0") + t_adv[c]) for c in CHARS))
    if a.preview:
        preview(b_adv, t_adv)
    print("gui font: %d glyphs, banner %dx%d" % (len(CHARS), BANNER_W, BANNER_H))


MAX_TEXT = MENU_W - 20


def measure(text, adv, space):
    return sum(space if c == " " else adv.get(c, space) for c in text) - 1


def fit(title, b_adv, t_adv):
    """The plugin's rule: bold if it fits, else thin, else thin and cut with '..'."""
    text = "".join(c for c in title.upper() if c == " " or c in GLYPHS).strip()
    if measure(text, b_adv, SPACE_BOLD) <= MAX_TEXT:
        return text, True
    while measure(text, t_adv, SPACE_THIN) > MAX_TEXT:
        text = text[:-3].rstrip() + ".."
    return text, False


def preview(b_adv, t_adv):
    """What the plugin draws, on a plain 9x4 menu (scaled 3x)."""
    titles = ["Help Menu", "Pickaxe Engines", "Fossilium Menu (Jockerlight)", "Gang · Nexium"]
    cells = []
    for title in titles:
        rows = 4
        H = 17 + rows * 18 + 14 + 3 * 18 + 4 + 18 + 7
        im = Image.new("RGBA", (MENU_W + 40, H + 20), (24, 30, 50, 255))
        ox, oy = 20, 14
        menu = Image.new("RGBA", (MENU_W, H), (198, 198, 198, 255))
        for r in range(rows):
            for c in range(9):
                x, y = 7 + c * 18, 17 + r * 18
                for i in range(18):
                    for j in range(18):
                        e = i == 0 or j == 0
                        menu.putpixel((x + i, y + j), (55, 55, 55, 255) if e else (139, 139, 139, 255))
        im.paste(menu, (ox, oy))
        b = Image.open(PACK / "textures/font/gui/banner.png")
        im.alpha_composite(b, (ox - OVER, oy + BANNER_TOP))
        text, bold = fit(title, b_adv, t_adv)
        adv = b_adv if bold else t_adv
        sheet_im = Image.open(PACK / "textures/font/gui" / ("%s.png" % ("bold" if bold else "thin")))
        width = measure(text, adv, SPACE_BOLD if bold else SPACE_THIN)
        x = 8 + (MENU_W - width) // 2
        for ch in text:
            if ch == " " or ch not in CHARS:
                x += SPACE_BOLD if adv is b_adv else SPACE_THIN
                continue
            i = CHARS.index(ch)
            g = sheet_im.crop(((i % 16) * CELL_W, (i // 16) * CELL_H, (i % 16 + 1) * CELL_W, (i // 16 + 1) * CELL_H))
            im.alpha_composite(g, (ox + x, oy + TEXT_TOP))
            x += adv[ch]
        cells.append(im.resize((im.width * 3, im.height * 3), Image.NEAREST))
    out = Image.new("RGBA", (sum(c.width for c in cells), cells[0].height), (24, 30, 50, 255))
    x = 0
    for c in cells:
        out.paste(c, (x, 0))
        x += c.width
    (ROOT / "previews").mkdir(exist_ok=True)
    out.save(ROOT / "previews" / "gui.png")


if __name__ == "__main__":
    sys.exit(main())
