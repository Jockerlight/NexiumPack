"""Software renderer for the exported item models (preview sheets).

Draws every texel of every face (Minecraft's face / UV conventions), sorted
back to front, with simple directional light. Faces with "shade": false
(glowing parts) are drawn unlit. Not Minecraft's renderer, but it reads the
exact files the game reads, so wrong UVs or holes show up here too.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# corner order: (u0,v0), (u1,v0), (u1,v1), (u0,v1) - Minecraft's FaceInfo
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
    x, y, z = p
    for axis, ang in (("z", r[2]), ("y", r[1]), ("x", r[0])):
        x, y, z = rot_axis((x, y, z), axis, ang, (0, 0, 0))
    return (x, y, z)


def transform(p, disp):
    x, y, z = p[0] - 8, p[1] - 8, p[2] - 8
    sc = disp.get("scale", [1, 1, 1])
    x, y, z = x * sc[0], y * sc[1], z * sc[2]
    x, y, z = euler_xyz((x, y, z), disp.get("rotation", [0, 0, 0]))
    t = disp.get("translation", [0, 0, 0])
    return (x + t[0], y + t[1], z + t[2])


LIGHT = np.array([0.35, 0.85, 0.55])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def _texels(q, img, uv):
    """Split face quad q (4 view-space points) into texel quads + colours."""
    W, H = img.size
    u0, v0, u1, v1 = uv
    nu = max(1, int(round(abs(u1 - u0) / 16 * W)))
    nv = max(1, int(round(abs(v1 - v0) / 16 * H)))
    q = np.array(q, float)
    a = np.linspace(0, 1, nu + 1)
    b = np.linspace(0, 1, nv + 1)
    top = q[0][None] + (q[1] - q[0])[None] * a[:, None]          # (nu+1, 3)
    bot = q[3][None] + (q[2] - q[3])[None] * a[:, None]
    grid = top[:, None] + (bot - top)[:, None] * b[None, :, None]  # (nu+1, nv+1, 3)
    px = np.asarray(img)
    us = u0 + (u1 - u0) * (np.arange(nu) + 0.5) / nu
    vs = v0 + (v1 - v0) * (np.arange(nv) + 0.5) / nv
    ix = np.clip((us / 16 * W).astype(int), 0, W - 1)
    iy = np.clip((vs / 16 * H).astype(int), 0, H - 1)
    cols = px[iy[None, :], ix[:, None]]   # (nu, nv, C)
    return grid, cols


def render(model, textures, disp, size=160, px=None, extra=None, bg=None, supersample=1):
    """Orthographic view from +z, y up. textures: {texture id: PIL image}."""
    S = size * supersample
    if px is None:
        px = size / 26.0
    px *= supersample
    im = Image.new("RGBA", (S, S), bg or (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    cx = cy = S / 2
    polys = []
    els = list(model.get("elements", [])) + list(extra or [])
    tex = model.get("textures", {})
    for el in els:
        f0, t0 = el["from"], el["to"]
        rot = el.get("rotation")
        lit = el.get("shade", True)
        for fname, fd in el["faces"].items():
            pts = []
            for ccx, ccy, ccz in CORNERS[fname]:
                p = (t0[0] if ccx else f0[0], t0[1] if ccy else f0[1], t0[2] if ccz else f0[2])
                if rot:
                    p = rot_axis(p, rot["axis"], rot["angle"], rot["origin"])
                pts.append(transform(p, disp))
            q = np.array(pts)
            n = np.cross(q[3] - q[0], q[1] - q[0])
            ln = np.linalg.norm(n)
            if ln < 1e-9:
                continue
            n = n / ln
            if n[2] <= 1e-6:
                continue
            b = 1.0 if not lit else 0.62 + 0.38 * max(-0.3, float(n @ LIGHT))
            if "color" in fd:
                # split into small quads so the back-to-front sort stays right
                n = 16
                a_ = np.linspace(0, 1, n + 1)
                top = q[0][None] + (q[1] - q[0])[None] * a_[:, None]
                bot = q[3][None] + (q[2] - q[3])[None] * a_[:, None]
                grid = top[:, None] + (bot - top)[:, None] * a_[None, :, None]
                col = np.array(fd["color"][:3]) * b
                for i in range(n):
                    for j in range(n):
                        poly = np.array([grid[i, j], grid[i + 1, j], grid[i + 1, j + 1], grid[i, j + 1]])
                        polys.append((poly[:, 2].mean(), poly, col))
                continue
            key = fd["texture"].lstrip("#")
            img = textures[tex.get(key, key)].convert("RGBA")
            grid, cols = _texels(q, img, fd["uv"])
            nu, nv = cols.shape[:2]
            for i in range(nu):
                for j in range(nv):
                    c = cols[i, j]
                    if c[3] < 128:
                        continue
                    poly = np.array([grid[i, j], grid[i + 1, j], grid[i + 1, j + 1], grid[i, j + 1]])
                    polys.append((poly[:, 2].mean() + 1e-4, poly, c[:3].astype(float) * b))
    polys.sort(key=lambda t: t[0])
    for _, poly, col in polys:
        c = tuple(int(max(0, min(255, v))) for v in col) + (255,)
        dr.polygon([(cx + p[0] * px, cy - p[1] * px) for p in poly], fill=c)
    if supersample > 1:
        im = im.resize((size, size), Image.LANCZOS)
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
