#!/usr/bin/env python3
"""Chat emojis: the emoji pictures in the chat font (minecraft:default).

    python tools/build_emoji.py            writes the font + sheet into pack/
    python tools/build_emoji.py --fetch    downloads missing source pictures first
    python tools/build_emoji.py --preview  also previews/emoji.png
    python tools/build_emoji.py --list     prints the list for the server script

Minecraft's fonts have no colour emoji: a real emoji (U+1F525 and so on)
shows as a box. This adds a picture for each emoji in EMOJI below to the
default font, the font chat, signs and menus use:
  - emojis past U+FFFF get their real code point, so an emoji pasted from a
    phone or Discord shows as the picture too;
  - emojis inside U+0000 - U+FFFF (heart, sparkles, check mark ...) get a
    private-use code point from U+E100 instead: vanilla already has a plain
    glyph for most of them and the server's menus use those (❤ ⚡ ⛏ ✔ ...),
    so they stay as they are;
  - the invisible emoji helpers (variation selectors U+FE0E / U+FE0F, the
    zero-width joiner U+200D, the skin tones U+1F3FB - U+1F3FF) get no width,
    vanilla drew them as boxes ("❤️" was a heart and a box).
Nothing of vanilla is replaced: fonts of all packs are merged, these
providers only cover code points vanilla has no glyph for.

The server (SimuxPrison 60_ui/emoji.sk) turns :fire: and :) into these
characters and colours them white (a font picture is multiplied with the
text colour, grey chat text would make it grey).

Pictures: Noto Emoji by Google (Apache License 2.0, see
pack/assets/nexium/textures/font/emoji/LICENSE-noto-emoji.txt), 72 px
sources in tools/art/emoji/, scaled to CELL px.

Writes (generated, don't edit by hand):
  pack/assets/minecraft/font/default.json
  pack/assets/nexium/textures/font/emoji/emoji.png
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "art" / "emoji"
OUT_FONT = ROOT / "pack" / "assets" / "minecraft" / "font" / "default.json"
OUT_TEX_DIR = ROOT / "pack" / "assets" / "nexium" / "textures" / "font" / "emoji"
OUT_TEX = OUT_TEX_DIR / "emoji.png"
NOTO = "https://cdn.jsdelivr.net/gh/googlefonts/noto-emoji@v2.047/png/72/emoji_u{cp:x}.png"

CELL = 32        # px per emoji in the sheet
COLS = 16
HEIGHT = 8       # the emoji's height in chat (text is 8 high, 7 above the line)
ASCENT = 7
PUA_FROM = 0xE100

# (code point, names): the first name is the :name:, the others work too
EMOJI = [
    # faces
    (0x1F604, "smile happy"), (0x1F601, "grin"), (0x1F602, "joy lol"),
    (0x1F923, "rofl"), (0x1F606, "laughing xd"), (0x1F605, "sweat_smile"),
    (0x1F642, "slight_smile"), (0x1F643, "upside_down"), (0x1F609, "wink"),
    (0x1F60A, "blush"), (0x1F607, "innocent angel"), (0x1F60D, "heart_eyes love"),
    (0x1F618, "kiss"), (0x1F60B, "yum"), (0x1F61B, "tongue"), (0x1F92A, "zany"),
    (0x1F911, "money_mouth"), (0x1F917, "hug"), (0x1F92B, "shush"),
    (0x1F914, "thinking think hmm"), (0x1F610, "neutral"), (0x1F611, "expressionless"),
    (0x1F644, "eyeroll rolling_eyes"), (0x1F60F, "smirk"), (0x1F62C, "grimace"),
    (0x1F60C, "relieved"), (0x1F634, "sleeping sleepy"), (0x1F971, "yawn"),
    (0x1F922, "sick nauseated"), (0x1F92E, "vomit"), (0x1F975, "hot"), (0x1F976, "cold"),
    (0x1F92F, "mindblown exploding_head"), (0x1F973, "party partying"),
    (0x1F60E, "cool sunglasses"), (0x1F913, "nerd"), (0x1F615, "confused"),
    (0x1F641, "frown"), (0x1F62E, "wow open_mouth"), (0x1F633, "flushed"),
    (0x1F97A, "pleading"), (0x1F622, "cry sad"), (0x1F62D, "sob"),
    (0x1F631, "scream"), (0x1F624, "huff triumph"), (0x1F620, "angry"),
    (0x1F621, "rage"), (0x1F92C, "swear cursing"), (0x1F608, "devil"),
    (0x1F480, "skull dead"), (0x1F4A9, "poop"), (0x1F921, "clown"),
    (0x1F47B, "ghost"), (0x1F47D, "alien"), (0x1F916, "robot"),
    (0x1FAE1, "salute"), (0x1FAE0, "melting"),
    # hands and people
    (0x1F44D, "thumbsup like +1"), (0x1F44E, "thumbsdown dislike -1"),
    (0x1F44C, "ok ok_hand"), (0x1F44F, "clap"), (0x1F64C, "yay raised_hands"),
    (0x1F44B, "wave hi bye"), (0x1F64F, "pray thanks"), (0x1F4AA, "muscle strong"),
    (0x1F44A, "punch fist"), (0x1F91D, "handshake deal"), (0x1F91E, "fingers_crossed"),
    (0x270C, "peace v"), (0x1F440, "eyes"), (0x1F9E0, "brain"),
    # hearts
    (0x2764, "heart"), (0x1F9E1, "orange_heart"), (0x1F49B, "yellow_heart"),
    (0x1F49A, "green_heart"), (0x1F499, "blue_heart"), (0x1F49C, "purple_heart"),
    (0x1F5A4, "black_heart"), (0x1F90D, "white_heart"), (0x1F494, "broken_heart"),
    (0x1F495, "two_hearts"), (0x1F496, "sparkling_heart"),
    # symbols
    (0x1F525, "fire lit"), (0x2728, "sparkles"), (0x2B50, "star"),
    (0x1F31F, "glowing_star"), (0x26A1, "zap lightning"), (0x1F4A5, "boom"),
    (0x1F4AF, "100"), (0x1F4A2, "anger"), (0x1F4A6, "sweat"), (0x1F4A4, "zzz"),
    (0x1F4AC, "speech"), (0x2705, "check yes"), (0x274C, "x no"),
    (0x2753, "question"), (0x2757, "exclamation"), (0x26A0, "warning"),
    (0x1F6AB, "forbidden"),
    # prison things
    (0x1F48E, "gem diamond"), (0x1F4B0, "moneybag money"), (0x1F4B8, "money_wings"),
    (0x1F4B5, "dollar cash"), (0x1FA99, "coin token"), (0x1F451, "crown"),
    (0x1F3C6, "trophy"), (0x1F947, "first gold"), (0x1F948, "second silver"),
    (0x1F949, "third bronze"), (0x26CF, "pickaxe pick"), (0x2694, "swords pvp"),
    (0x1F6E1, "shield"), (0x1F4A3, "bomb nuke"), (0x1F680, "rocket"),
    (0x1F4C8, "stonks"), (0x1F4C9, "not_stonks"), (0x1F511, "key"),
    (0x1F512, "lock"), (0x1F514, "bell"), (0x1F3AE, "game"), (0x1F3B2, "dice"),
    (0x1F3AF, "target"), (0x1F3B5, "music"), (0x23F0, "alarm"), (0x231B, "hourglass"),
    # party and food
    (0x1F389, "tada"), (0x1F38A, "confetti"), (0x1F381, "gift"), (0x1F382, "cake"),
    (0x1F36A, "cookie"), (0x1F355, "pizza"), (0x1F354, "burger"), (0x1F37A, "beer"),
    (0x2615, "coffee"), (0x1F95A, "egg"),
    # nature and animals
    (0x1F308, "rainbow"), (0x2600, "sun"), (0x1F319, "moon"), (0x2744, "snowflake"),
    (0x1F30D, "earth world"), (0x1F340, "clover"), (0x1F339, "rose"),
    (0x1F409, "dragon"), (0x1F431, "cat"), (0x1F436, "dog"), (0x1F437, "pig"),
    (0x1F414, "chicken"), (0x1F41F, "fish"), (0x1F410, "goat"), (0x1F40D, "snake"),
    (0x1F984, "unicorn"), (0x1F41D, "bee"), (0x1F98A, "fox"), (0x1F43C, "panda"),
    # seasons
    (0x1F383, "pumpkin jack_o_lantern"), (0x1F384, "christmas_tree xmas"),
    (0x1F385, "santa"), (0x26C4, "snowman"),
]

# classic emoticons the server turns into emojis (only as their own word)
EMOTICONS = {
    ":)": "slight_smile", ":-)": "slight_smile", ":D": "smile", ":-D": "smile",
    "xD": "laughing", "XD": "laughing", ";)": "wink", ";-)": "wink",
    ":(": "frown", ":-(": "frown", ":'(": "cry", ":P": "tongue", ":p": "tongue",
    ":O": "wow", ":o": "wow", "<3": "heart", "</3": "broken_heart",
    "B)": "cool", ":|": "neutral",
}

ZERO_WIDTH = [0xFE0E, 0xFE0F, 0x200D, 0x1F3FB, 0x1F3FC, 0x1F3FD, 0x1F3FE, 0x1F3FF]


def glyph_cp(cp, i_bmp):
    """The code point the font uses: the real one past U+FFFF, else private use."""
    return cp if cp > 0xFFFF else PUA_FROM + i_bmp


def entries():
    out = []
    nb = 0
    names = set()
    for cp, n in EMOJI:
        ns = n.split()
        for x in ns:
            if x in names:
                sys.exit(f"name {x} twice")
            names.add(x)
        g = glyph_cp(cp, nb)
        if cp <= 0xFFFF:
            nb += 1
        out.append({"cp": cp, "glyph": g, "names": ns})
    return out


def src_path(cp):
    return SRC / f"emoji_u{cp:x}.png"


def fetch():
    SRC.mkdir(parents=True, exist_ok=True)
    for cp, _ in EMOJI:
        p = src_path(cp)
        if p.exists():
            continue
        url = NOTO.format(cp=cp)
        with urllib.request.urlopen(url, timeout=30) as r:
            p.write_bytes(r.read())
        print("fetched", p.name)


def scaled(cp):
    im = Image.open(src_path(cp)).convert("RGBA")
    # scale with premultiplied alpha: no dark fringe on the edges
    im = im.convert("RGBa").resize((CELL, CELL), Image.LANCZOS).convert("RGBA")
    # pixels the scaling made almost clear: fully clear (the font measures
    # an emoji's width by its last column with alpha)
    px = im.load()
    for y in range(CELL):
        for x in range(CELL):
            if px[x, y][3] < 24:
                px[x, y] = (0, 0, 0, 0)
    return im


def build(preview=False):
    es = entries()
    rows = (len(es) + COLS - 1) // COLS
    sheet = Image.new("RGBA", (COLS * CELL, rows * CELL), (0, 0, 0, 0))
    chars = []
    for r in range(rows):
        line = ""
        for c in range(COLS):
            i = r * COLS + c
            if i < len(es):
                sheet.paste(scaled(es[i]["cp"]), (c * CELL, r * CELL))
                line += chr(es[i]["glyph"])
            else:
                line += "\u0000"
        chars.append(line)
    OUT_TEX_DIR.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT_TEX, optimize=True)
    font = {"providers": [
        {"type": "space", "advances": {chr(cp): 0 for cp in ZERO_WIDTH}},
        {"type": "bitmap", "file": "nexium:font/emoji/emoji.png",
         "height": HEIGHT, "ascent": ASCENT, "chars": chars},
    ]}
    OUT_FONT.parent.mkdir(parents=True, exist_ok=True)
    OUT_FONT.write_text(json.dumps(font, ensure_ascii=True, indent=1) + "\n", encoding="utf-8")
    print(f"{len(es)} emojis, sheet {sheet.size[0]}x{sheet.size[1]} -> {OUT_TEX.relative_to(ROOT)}")
    if preview:
        pv = ROOT / "previews"
        pv.mkdir(exist_ok=True)
        big = sheet.resize((sheet.size[0] * 2, sheet.size[1] * 2), Image.NEAREST)
        bg = Image.new("RGBA", big.size, (60, 60, 60, 255))
        bg.alpha_composite(big)
        bg.convert("RGB").save(pv / "emoji.png")
    return es


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--list", action="store_true", help="print the server list (JSON)")
    a = ap.parse_args()
    if a.fetch:
        fetch()
    es = build(a.preview)
    if a.list:
        print(json.dumps({"emoji": [{"glyph": e["glyph"], "cp": e["cp"], "names": e["names"]} for e in es],
                          "emoticons": EMOTICONS}))


if __name__ == "__main__":
    main()
