"""2D pixel art for planes (wings, capes, banners) and pickaxe skins.

Wing textures are drawn for the LEFT wing as seen from behind the player:
the root (shoulder) at the right edge, the tip to the left. The right wing
uses the same texture mirrored.
"""
import math
from PIL import Image, ImageDraw
from vox import hexc, mix, shade

TEXTURES = {}   # "nexium:item/cos/<name>" -> PIL image
OUTLINE = (18, 20, 28, 255)


def reg(name, im):
    TEXTURES["nexium:item/cos/" + name] = im
    return "nexium:item/cos/" + name


def new(w=32, h=32):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def rgba(c, a=255):
    return tuple(c[:3]) + (a,)


def outline(im, col=OUTLINE, diag=False):
    """Paint every empty pixel that touches a filled one."""
    w, h = im.size
    px = im.load()
    add = []
    nb = ((1, 0), (-1, 0), (0, 1), (0, -1)) + (((1, 1), (-1, -1), (1, -1), (-1, 1)) if diag else ())
    for y in range(h):
        for x in range(w):
            if px[x, y][3] == 0:
                for dx, dy in nb:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] > 0 and px[nx, ny][:3] != col[:3]:
                        add.append((x, y))
                        break
    for x, y in add:
        px[x, y] = col
    return im


def thick_line(dr, a, b, col, w=1):
    dr.line([a, b], fill=col, width=w)


def poly(dr, pts, col):
    dr.polygon([(round(x), round(y)) for x, y in pts], fill=col)


def ellipse_pts(cx, cy, rx, ry, ang, n=24):
    out = []
    ca, sa = math.cos(ang), math.sin(ang)
    for k in range(n):
        t = 2 * math.pi * k / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        out.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return out


# --------------------------------------------------------------- wings
def _interp(pts, x):
    """y of a polyline (x descending or ascending) at x."""
    pts = sorted(pts)
    if x <= pts[0][0]:
        return pts[0][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / max(1e-6, x1 - x0)
    return pts[-1][1]


def feather_wing(name, c_root, c_tip, c_cover, accent=None, spiky=False, rows=3, w=32, h=32, line=None):
    """Bird / angel wing: rounded top edge, three feather layers (coverts,
    secondaries, primaries) with scalloped edges, feather lines in the long
    layer. Root (shoulder) at the right edge, tip at the left."""
    im = new(w, h)
    px = im.load()
    top = [(31, 11), (26, 5), (19, 2), (11, 1), (5, 2), (1, 5)]
    bot_base = [(1, 9), (3, 17), (7, 24), (13, 29), (20, 29), (26, 25), (31, 20)]
    line = line or shade(c_root, 0.72)
    for x in range(w):
        yt = _interp(top, x)
        yb = _interp(bot_base, x)
        if spiky:
            yb += 3 * abs(math.sin(x * math.pi / 2.5)) - 1.5
        else:
            yb += 1.6 * abs(math.sin(x * math.pi / 3.0)) - 0.8
        for y in range(h):
            if yt <= y + 0.5 <= yb:
                d = (y + 0.5 - yt) / max(1.0, yb - yt)        # 0 top .. 1 bottom
                t = 1 - x / (w - 1)                            # 0 root .. 1 tip
                if d < 0.28 + 0.03 * math.sin(x * 1.7):
                    col = mix(c_cover, c_root, 0.15)
                elif d < 0.58 + 0.04 * math.sin(x * 1.3 + 1):
                    col = mix(c_root, c_tip, t * 0.5)
                else:
                    col = mix(c_root, c_tip, 0.35 + t * 0.65)
                b1 = abs(d - (0.28 + 0.03 * math.sin(x * 1.7))) < 0.035
                b2 = abs(d - (0.58 + 0.04 * math.sin(x * 1.3 + 1))) < 0.03
                feather = d > 0.62 and (x + int(d * 4)) % 3 == 0
                if b1 or b2 or feather:
                    col = line if not (b1 and accent) else accent
                px[x, y] = rgba(col)
    if accent:
        for x, y in ((28, 9), (22, 5), (15, 3), (8, 3)):
            if px[x, y][3]:
                px[x, y] = rgba(accent)
    return reg(name, outline(im))


def membrane_wing(name, c_mem, c_mem2, c_bone, claw=(235, 230, 220), w=32, h=32):
    """Bat / dragon / demon wing: bones from the wrist, membrane between."""
    im = new(w, h)
    dr = ImageDraw.Draw(im)
    root = (w - 2, 12)
    wrist = (17, 3)
    tips = [(1, 6), (2, 17), (8, 26), (18, 30)]
    bottom = (w - 2, 27)
    edge = [root, wrist]
    for i, tp in enumerate(tips):
        edge.append(tp)
        if i < len(tips) - 1:
            nx = tips[i + 1]
            mx = (tp[0] + nx[0]) / 2 + (wrist[0] - (tp[0] + nx[0]) / 2) * 0.22
            my = (tp[1] + nx[1]) / 2 + (wrist[1] - (tp[1] + nx[1]) / 2) * 0.22
            edge.append((mx, my))
    edge.append(((tips[-1][0] + bottom[0]) / 2 + 2, (tips[-1][1] + bottom[1]) / 2 - 2))
    edge.append(bottom)
    poly(dr, edge, rgba(c_mem))
    # lighter panels between the bones
    for i in range(len(tips) - 1):
        a, b = tips[i], tips[i + 1]
        poly(dr, [wrist, (a[0] * 0.75 + wrist[0] * 0.25, a[1] * 0.75 + wrist[1] * 0.25),
                  (b[0] * 0.75 + wrist[0] * 0.25, b[1] * 0.75 + wrist[1] * 0.25)], rgba(c_mem2))
    dr.line([root, wrist], fill=rgba(c_bone), width=2)
    for tp in tips:
        dr.line([wrist, tp], fill=rgba(c_bone), width=1)
    dr.line([root, bottom], fill=rgba(shade(c_bone, 0.85)), width=1)
    im.putpixel((wrist[0], wrist[1] - 1), rgba(claw))
    im.putpixel((wrist[0] - 1, wrist[1] - 2), rgba(claw))
    for tp in tips[:3]:
        im.putpixel((max(0, tp[0]), min(h - 1, tp[1])), rgba(claw))
    return reg(name, outline(im))


def insect_wing(name, c_main, c_edge, c_vein, spots=None, lobes=((14, 11, 13, 9, -0.35), (20, 23, 9, 7, 0.4)), glassy=False, w=32, h=32):
    im = new(w, h)
    dr = ImageDraw.Draw(im)
    for cx, cy, rx, ry, a in lobes:
        poly(dr, ellipse_pts(cx, cy, rx + 1, ry + 1, a), rgba(c_edge))
        poly(dr, ellipse_pts(cx, cy, rx - 0.5, ry - 0.5, a), rgba(c_main))
    root = (w - 2, 16)
    for ang in (-150, -170, 175, 160, 140, 120):
        a = math.radians(ang)
        dr.line([root, (root[0] + math.cos(a) * 30, root[1] + math.sin(a) * 30)], fill=rgba(c_vein))
    # keep the veins inside the wing
    px = im.load()
    base = new(w, h)
    bd = ImageDraw.Draw(base)
    for cx, cy, rx, ry, a in lobes:
        poly(bd, ellipse_pts(cx, cy, rx + 1, ry + 1, a), (255, 255, 255, 255))
    bp = base.load()
    for y in range(h):
        for x in range(w):
            if bp[x, y][3] == 0:
                px[x, y] = (0, 0, 0, 0)
    if spots:
        for x, y in spots:
            if px[x, y][3] > 0:
                px[x, y] = rgba((250, 250, 245))
    if glassy:
        for x, y in ((8, 8), (9, 8), (8, 9), (17, 21), (18, 21)):
            if px[x, y][3] > 0:
                px[x, y] = rgba((240, 250, 255))
    return reg(name, outline(im))


def spike_wing(name, c_base, c_tip, c_hi, n=7, w=32, h=32, length=(14, 28)):
    """Crystal / ice wing: sharp spikes fanning out from the shoulder."""
    im = new(w, h)
    dr = ImageDraw.Draw(im)
    root = (w - 2, 14)
    for i in range(n):
        t = i / (n - 1)
        ang = math.radians(195 - 85 * t)       # from up-left round to down-left
        ln = length[0] + (length[1] - length[0]) * math.sin(t * math.pi * 0.9 + 0.3)
        ex, ey = root[0] + math.cos(ang) * ln, root[1] + math.sin(ang) * ln * 0.95
        nx, ny = -math.sin(ang), math.cos(ang)
        base_w = 3.2
        b1 = (root[0] + nx * base_w, root[1] + ny * base_w)
        b2 = (root[0] - nx * base_w, root[1] - ny * base_w)
        poly(dr, [b1, b2, (ex, ey)], rgba(mix(c_base, c_tip, 0.3 + 0.4 * t)))
        poly(dr, [b1, ((b1[0] + ex) / 2, (b1[1] + ey) / 2), (ex, ey)], rgba(c_tip))
        dr.line([((root[0] + ex) / 2, (root[1] + ey) / 2), (ex, ey)], fill=rgba(c_hi))
    return reg(name, outline(im))


def leaf_wing(name, c_leaf, c_dark, c_rib, n=5, w=32, h=32):
    im = new(w, h)
    dr = ImageDraw.Draw(im)
    root = (w - 3, 15)
    for i in range(n):
        t = i / (n - 1)
        ang = math.radians(200 - 70 * t)
        ln = 15 + 6 * math.sin(t * math.pi)
        cx, cy = root[0] + math.cos(ang) * ln * 0.55, root[1] + math.sin(ang) * ln * 0.55
        poly(dr, ellipse_pts(cx, cy, ln * 0.55, 3.4, ang), rgba(c_dark))
        poly(dr, ellipse_pts(cx, cy, ln * 0.5, 2.5, ang), rgba(c_leaf))
        dr.line([root, (root[0] + math.cos(ang) * ln, root[1] + math.sin(ang) * ln)], fill=rgba(c_rib))
    dr.line([(root[0], root[1] - 3), (root[0], root[1] + 3)], fill=rgba((92, 62, 36)), width=2)
    return reg(name, outline(im))


def blade_wing(name, c_metal, c_dark, c_light, c_glow, w=32, h=32):
    """Mech wing: stacked metal blades with lights at the ends."""
    im = new(w, h)
    dr = ImageDraw.Draw(im)
    for i, (y, ln) in enumerate(((5, 29), (11, 26), (17, 22), (23, 17))):
        x0 = w - 1 - ln
        dr.rectangle([x0, y, w - 2, y + 3], fill=rgba(c_metal))
        dr.line([(x0, y), (w - 2, y)], fill=rgba(c_light))
        dr.line([(x0, y + 3), (w - 2, y + 3)], fill=rgba(c_dark))
        dr.rectangle([x0, y + 1, x0 + 1, y + 2], fill=rgba(c_glow))
        for x in range(x0 + 4, w - 3, 5):
            im.putpixel((x, y + 2), rgba(c_dark))
    dr.rectangle([w - 4, 4, w - 2, 27], fill=rgba(c_dark))
    return reg(name, outline(im))


# --------------------------------------------------------------- capes
def cape(name, c1, c2, trim, rod, emblem=None, w=16, h=32, stripes=True):
    im = new(w, h)
    dr = ImageDraw.Draw(im)
    dr.rectangle([1, 2, w - 2, h - 2], fill=rgba(c1))
    if stripes:
        for x in range(2, w - 2, 3):
            dr.line([(x, 4), (x, h - 3)], fill=rgba(c2))
    dr.rectangle([1, 2, w - 2, h - 2], outline=rgba(trim))
    dr.rectangle([0, 0, w - 1, 2], fill=rgba(rod))
    for x in range(1, w - 1, 3):
        im.putpixel((x, h - 1), rgba(trim))
    if emblem:
        emblem(im)
    return reg(name, outline(im))
