"""Small software renderer for the exported item models (preview sheets).

Not Minecraft's renderer: flat colours, painter's algorithm, simple light.
Good enough to see shape, colours and placement before anything is in game.
"""
import math
from PIL import Image, ImageDraw, ImageFont

CORNERS = {
    "north": [(1, 1, 0), (0, 1, 0), (0, 0, 0), (1, 0, 0)],
    "south": [(0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 1)],
    "east": [(1, 1, 1), (1, 1, 0), (1, 0, 0), (1, 0, 1)],
    "west": [(0, 1, 0), (0, 1, 1), (0, 0, 1), (0, 0, 0)],
    "up": [(0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)],
    "down": [(0, 0, 1), (1, 0, 1), (1, 0, 0), (0, 0, 0)],
}


def rot_axis(p, axis, ang, org):
    a = math.radians(ang)
    x, y, z = p[0] - org[0], p[1] - org[1], p[2] - org[2]
    c, s = math.cos(a), math.sin(a)
    if axis == "y":
        x, z = x * c + z * s, -x * s + z * c
    elif axis == "x":
        y, z = y * c - z * s, y * s + z * c
    else:
        x, y = x * c - y * s, x * s + y * c
    return (x + org[0], y + org[1], z + org[2])


def euler_xyz(p, r):
    """Minecraft ItemTransform rotation: X then Y then Z (degrees)."""
    x, y, z = p
    for axis, ang in (("z", r[2]), ("y", r[1]), ("x", r[0])):
        x, y, z = rot_axis((x, y, z), axis, ang, (0, 0, 0))
    return (x, y, z)


def transform(p, disp):
    """model units -> view units (centered, display transform applied)."""
    x, y, z = p[0] - 8, p[1] - 8, p[2] - 8
    sc = disp.get("scale", [1, 1, 1])
    x, y, z = x * sc[0], y * sc[1], z * sc[2]
    x, y, z = euler_xyz((x, y, z), disp.get("rotation", [0, 0, 0]))
    t = disp.get("translation", [0, 0, 0])
    return (x + t[0], y + t[1], z + t[2])


def sample(img, u, v):
    w, h = img.size
    px = min(w - 1, max(0, int(u / 16 * w)))
    py = min(h - 1, max(0, int(v / 16 * h)))
    return img.getpixel((px, py))


def faces_of(model, textures, extra=None):
    """[(corners3d, colour or (img, uv), face, normal)] in model space."""
    out = []
    els = list(model.get("elements", [])) + list(extra or [])
    for el in els:
        f0, t0 = el["from"], el["to"]
        rot = el.get("rotation")
        for fname, fd in el["faces"].items():
            pts = []
            for cx, cy, cz in CORNERS[fname]:
                p = (t0[0] if cx else f0[0], t0[1] if cy else f0[1], t0[2] if cz else f0[2])
                if rot:
                    p = rot_axis(p, rot["axis"], rot["angle"], rot["origin"])
                pts.append(p)
            if "color" in fd:
                out.append((pts, fd["color"], fname, None))
                continue
            img = textures[model["textures"][fd["texture"].lstrip("#")]]
            u0, v0, u1, v1 = fd["uv"]
            if abs(u1 - u0) <= 1.01 and abs(v1 - v0) <= 1.01 or fd["texture"] == "#p":
                c = sample(img, (u0 + u1) / 2, (v0 + v1) / 2)
                if c[3] > 0:
                    out.append((pts, c[:3], fname, None))
            else:
                out.append((pts, (img, fd["uv"]), fname, None))
    return out


def normal(q):
    a, b, c = q[0], q[1], q[2]
    u = [b[i] - a[i] for i in range(3)]
    v = [c[i] - a[i] for i in range(3)]
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    l = math.sqrt(sum(k * k for k in n)) or 1
    return tuple(-k / l for k in n)  # corners are listed clockwise seen from outside


LIGHT = (0.35, 0.85, 0.55)


def render(model, textures, disp, size=160, px=None, extra=None, bg=None):
    """Orthographic, viewer at +z looking at -z, y up. px = pixels per unit."""
    fs = faces_of(model, textures, extra)
    polys = []
    for pts, col, fname, _ in fs:
        q = [transform(p, disp) for p in pts]
        polys.append((q, col, normal(q)))
    if px is None:
        px = size / 26.0
    im = Image.new("RGBA", (size, size), bg or (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    cx = cy = size / 2

    def scr(p):
        return (cx + p[0] * px, cy - p[1] * px)

    def bright(n):
        d = n[0] * LIGHT[0] + n[1] * LIGHT[1] + n[2] * LIGHT[2]
        return 0.62 + 0.38 * max(-0.3, d)

    items = []
    for q, col, n in polys:
        if n[2] < -1e-6:
            continue  # facing away
        depth = sum(p[2] for p in q) / 4
        items.append((depth, q, col, n))
    items.sort(key=lambda t: t[0])
    for depth, q, col, n in items:
        b = bright(n)
        if isinstance(col, tuple) and len(col) == 3 and not isinstance(col[0], Image.Image):
            c = tuple(max(0, min(255, int(v * b))) for v in col)
            dr.polygon([scr(p) for p in q], fill=c + (255,))
        else:
            img, uv = col
            u0, v0, u1, v1 = uv
            w, h = img.size
            nu = max(1, int(round(abs(u1 - u0) / 16 * w)))
            nv = max(1, int(round(abs(v1 - v0) / 16 * h)))
            # corners: q[0]=top-left(u0,v0), q[1]=top-right, q[2]=bottom-right, q[3]=bottom-left
            for i in range(nu):
                for j in range(nv):
                    uu = u0 + (u1 - u0) * (i + 0.5) / nu
                    vv = v0 + (v1 - v0) * (j + 0.5) / nv
                    c = sample(img, uu, vv)
                    if c[3] < 128:
                        continue
                    def at(a, bb):
                        top = [q[0][k] + (q[1][k] - q[0][k]) * a for k in range(3)]
                        bot = [q[3][k] + (q[2][k] - q[3][k]) * a for k in range(3)]
                        return [top[k] + (bot[k] - top[k]) * bb for k in range(3)]
                    a0, a1 = i / nu, (i + 1) / nu
                    b0, b1 = j / nv, (j + 1) / nv
                    poly = [at(a0, b0), at(a1, b0), at(a1, b1), at(a0, b1)]
                    cc = tuple(max(0, min(255, int(v * b))) for v in c[:3])
                    dr.polygon([scr(p) for p in poly], fill=cc + (255,))
    return im


def head_cube(color=(58, 64, 82)):
    """The player's head (model units 4..12) for hat previews."""
    return [{"from": [4, 4, 4], "to": [12, 12, 12],
             "faces": {f: {"color": color} for f in CORNERS}}]


def body_parts(color=(58, 64, 82)):
    """Torso + head + arms in back-model space (torso x4..12 y2..14 z6..10)."""
    parts = [([4, 2, 6], [12, 14, 10]), ([4, 14, 4], [12, 22, 12]),
             ([0, 2, 6], [4, 14, 10]), ([12, 2, 6], [16, 14, 10]),
             ([4, -10, 6], [8, 2, 10]), ([8, -10, 6], [12, 2, 10])]
    return [{"from": a, "to": b, "faces": {f: {"color": color} for f in CORNERS}} for a, b in parts]


def sheet(cells, cols, cell=150, title="", label_h=14, bg=(22, 28, 48)):
    """cells: [(name, image)] -> one PNG like the reference sheets."""
    rows = math.ceil(len(cells) / cols)
    W = cols * cell
    H = rows * (cell + label_h) + 16
    out = Image.new("RGB", (W, H), bg)
    dr = ImageDraw.Draw(out)
    font = ImageFont.load_default()
    dr.text((4, 2), title, fill=(220, 220, 230), font=font)
    for i, (name, im) in enumerate(cells):
        x = (i % cols) * cell
        y = 16 + (i // cols) * (cell + label_h)
        dr.rectangle([x + 1, y + 1, x + cell - 2, y + cell + label_h - 2], fill=(28, 36, 60))
        out.paste(im, (x + (cell - im.size[0]) // 2, y + (cell - im.size[1]) // 2), im)
        dr.text((x + 4, y + cell), name.upper(), fill=(200, 200, 210), font=font)
    return out
