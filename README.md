# NexiumPack

The resource pack of the **NEXIUM** prison server: **54 hats, 36 back
items, 8 outfits, 30 pickaxe skins** and the Skin Crate, about 2 MB.

The **outfits**, the **wings** and the **capes** are the pixel art of the
design sheets, copied pixel for pixel into `tools/art/` and built from there:
armour, helmet faces, wings, crowns, halos, jetpacks. The hats and the other
back items are built from voxels four times finer than a skin pixel (a head
is 32 voxels wide, like a 32x skin), with their own texture: woven straw,
knitted wool, polished gold, cut gems, brushed metal, glass, fur and so on,
soft shadows in every crease and a light edge on every corner. Glowing
parts (halos, visors, flames, crystals, lava edges) really glow in the dark.

Players never download anything by hand: the server's **NexiumPack**
plugin sends this pack to every player when they join. Everything custom
lives in the `nexium` namespace, so nothing of vanilla Minecraft is
replaced: a normal diamond pickaxe still looks normal.

## How a change reaches the players

1. Change files and push to `main`.
2. The **Release pack** workflow (Actions tab) builds `NexiumPack.zip`
   and publishes it as a release named `pack-<first 12 characters of its SHA-1>`,
   together with `pack.json` (download link + SHA-1).
3. The plugin reads
   `https://github.com/Jockerlight/NexiumPack/releases/latest/download/pack.json`
   every 5 minutes. When the pack changed, it sends the new one to everyone
   online and to everyone who joins. In game, `/nexiumpack check` checks
   right away.

A push that doesn't change the pack makes no new release. The 10 newest
releases are kept.

## How the cosmetics work in game

| Kind | Item model | On the server |
|---|---|---|
| Hat | `nexium:hat/<id>` | the helmet gets this look, its stats stay |
| Back item | `nexium:back/<id>` | an item display riding on the player, turned with the body |
| Outfit | `nexium:outfit/<id>_head`, `_back` + equipment `nexium:<id>` | head look, armour textures on chest / legs / feet, wings or cape |
| Pickaxe skin | `nexium:pick/<id>` | the pickaxe's look (Skin Crate, `/skins`): a 32x32 icon in menus, a 3D model in the hand |

Menus: every menu gets a blue title banner with its name in white capitals,
centred (font `nexium:gui`: `textures/font/gui/banner.png` and a small
title font, made by `tools/build_gui.py`). The NexiumPack plugin swaps the
title when a menu opens; the scripts keep their plain titles.

The server's scripts (`50_systems/coswear.sk`, `pickskins.sk`,
`cosmetics.sk` in the SimuxPrison repository) know the ids. A new cosmetic
needs an entry there too, otherwise nobody can get it.

## Layout

```
pack/                                    what goes into the zip
  pack.mcmeta, pack.png                  name, formats, icon
  assets/nexium/items/<kind>/<id>.json   item model definitions
  assets/nexium/models/item/<kind>/      the 3D models
  assets/nexium/textures/item/cos/<kind>/<id>.png   each model's own texture
  assets/nexium/textures/item/pick/      the 32x32 pickaxe icons
  assets/nexium/equipment/<id>.json      outfit armour layers
  assets/nexium/font/gui.json            menu title banner font (+ textures/font/gui/)
  assets/nexium/textures/entity/equipment/{humanoid,humanoid_leggings}/<id>.png  (128x64)
tools/
  art/outfits/<id>/                      outfit pixel art (see below)
  art/backs/<id>/                        wings and capes as pixel art
  build_cos.py                           generates every cosmetic into pack/
  build_gui.py                           the menu title banner + its font
  build_shaders.py                       the rainbow wave text shader (overlays nx_wave_88 / nx_wave_97)
  buildpack.py                           builds build/NexiumPack.zip (CI runs this)
  gen/hd.py                              voxel models: shapes and materials
  gen/bake.py                            voxels -> boxes + one baked texture per model
  gen/parts.py, gen/wings.py             reusable parts (bands, gems, brims, horns, wings ...)
  gen/hats.py, backs.py, outfits.py,     the cosmetics, one function each
  gen/pickaxes.py, misc.py               pickaxe skins, Skin Crate
  gen/render.py                          preview renderer (reads the exported files)
cosmetics.json                           id, name, rarity, kind of everything
previews/                                preview sheets (hats.png, backs.png ...)
```

Everything under `pack/assets/nexium/` except `pack.mcmeta` / `pack.png`
is generated: change the generator, not the files.

## Adding or changing a cosmetic

Each cosmetic is a small Python function that fills shapes with materials.
Coordinates are skin pixels (the head is x/y/z 4..12, its front is north),
the voxels are 4 times finer. A new hat in `tools/gen/hats.py`:

```python
@hat("pointy_hat", "Pointy Hat", "COMMON")
def pointy_hat():
    m = hat_model("pointy_hat")
    m.fill(cone(8, 8, 3.5, 12.5, 7), velvet("ff5cc8"))     # a velvet cone on the head
    m.fill(head_band(11.2, 12.6), gold())                  # a gold band around it
    m.fill(sphere(8, 19.8, 8, 0.6), glow("ffd54a", 15))    # a glowing tip
    return m
```

Shapes: `box`, `rbox` (rounded), `sphere`, `ellipsoid`, `cyl`, `cone`,
`dome`, `ring`, `torus`, `tube` / `capsule` (curves), `prism` (2D outline),
combined with `|`, `&`, `-` and moved with `.move()` / `.rot()`. Materials:
`solid`, `gold`, `silver`, `gem`, `crystal`, `velvet`, `fabric`, `knit`,
`fur`, `wood`, `leather`, `straw`, `stone`, `metal`, `glass`, `glow`,
`grad`, `stripes`. Back items go in `backs.py` (`@back`, wings with
`wings.py`), pickaxe skins in `pickaxes.py` (`@pick`).

Outfits, wings and capes are drawn as pixel art instead
(`tools/art/outfits/<id>/`, `tools/art/backs/<id>/`, read by
`gen/outfits.py`; a back item with an art folder uses it instead of its
function in `backs.py`):

| File | What |
|---|---|
| `humanoid.png`, `humanoid_leggings.png` | the armour, Minecraft's 64x32 armour layout at 2x |
| `head_front.png`, `head_back.png` | the helmet's front and back (sides and top continue their edges) |
| `<head or back>_<n>_<mode>.png` | a sprite, one pixel = a quarter skin pixel |
| `art.json` | where each sprite goes and how: `wing` (the left wing, swept back 22.5 degrees, the right one mirrors it), `flat` (a thin plate: capes, rings), `slab` (pushed through z: crests, antlers, jetpacks), `band` (on all four sides of the head: crowns), `ring` (bent round a level ring: halos); `glow` colours light up |

Edit the PNGs in any pixel editor and run the build. Then:

```
pip install pillow numpy
python tools/build_cos.py --preview
python tools/build_cos.py --only hat:pointy_hat --preview     # just one, quickly
```

writes the models and textures into `pack/`, updates `cosmetics.json` and
draws `previews/*.png` so you can look at the result without starting
Minecraft. Push `pack/`, `tools/` and `cosmetics.json` together.

## Rainbow wave in chat

The REBIRTH / PRESTIGE words of the rebirth and prestige lines in chat are
a rainbow that runs along the word. The server sends them in seven special
colours (`WAVE` in `tools/build_shaders.py`); the pack's text shader turns
exactly these colours (and their shadows) into the moving rainbow and draws
all other text like vanilla. The shader file differs per Minecraft version,
so it comes as overlays (`pack.mcmeta`): `pack/nx_wave_88/` for 26.2 and
`pack/nx_wave_97/` for 26.3. Other versions show the seven colours as a
still rainbow. `python tools/build_shaders.py` writes both overlays; a new
Minecraft version needs its vanilla `core/text.vsh` added there.

## Menu title banner

`python tools/build_gui.py --preview` draws the banner and the title font
into `pack/` and shows four sample menus in `previews/gui.png`. The plugin
needs the width of every letter: after changing a letter run
`python tools/build_gui.py --java` and copy the three lines into
`GuiTitles.java` (SimuxPrison repository, `nexiumpack/`). Names that are too
wide for the banner use the thin letters, and are cut with `..` if even
those don't fit.

## Size and speed

- Voxels are merged into as few boxes as possible, hidden faces are left
  out, each visible face gets exactly its pixels in the model's texture.
- Textures are packed tightly (powers of two, so Minecraft keeps all mipmap
  levels), with at most 256 colours.
- Minified JSON, the smallest lossless PNG and a deterministic zip (sorted,
  fixed dates): the same files always give the same SHA-1, so players only
  download again when something really changed.

`tools/buildpack.py` checks every model before building: a texture that
doesn't exist stops the build (in game it would be the purple and black
"missing texture").

## Minecraft versions

`pack.mcmeta` says the pack works from 1.21.4 (format 46) to 26.3
(format 97): item model definitions (`items/`) need 1.21.4 or newer. When the
server moves to a newer Minecraft, raise `max_format` to that version's
resource pack format (Minecraft wiki, "Pack format").

## Building by hand

```
pip install pillow
python tools/buildpack.py
```

writes `build/NexiumPack.zip` and prints its SHA-1.
