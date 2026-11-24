# NexiumPack

The resource pack of the **NEXIUM** prison server: **54 hats, 36 back
items, 8 outfits, 30 pickaxe skins** and the Skin Crate, about 185 KB.

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
| Pickaxe skin | `nexium:pick/<id>` | the pickaxe's look (Skin Crate, `/skins`) |

The server's scripts (`50_systems/coswear.sk`, `pickskins.sk`,
`cosmetics.sk` in the SimuxPrison repository) know the ids. A new cosmetic
needs an entry there too, otherwise nobody can get it.

## Layout

```
pack/                                    what goes into the zip
  pack.mcmeta, pack.png                  name, formats, icon
  assets/nexium/items/<kind>/<id>.json   item model definitions
  assets/nexium/models/item/<kind>/      the 3D models
  assets/nexium/textures/item/cos/       palette.png (all voxel colours) + plane textures
  assets/nexium/equipment/<id>.json      outfit armour layers
  assets/nexium/textures/entity/equipment/{humanoid,humanoid_leggings}/<id>.png
tools/
  build_cos.py                           generates every cosmetic into pack/
  buildpack.py                           builds build/NexiumPack.zip (CI runs this)
  gen/hats.py, backs.py, outfits.py,     the cosmetics, one function each
  gen/pickaxes.py
  gen/vox.py, shapes.py, sprite.py,      voxel model + greedy mesher, shape helpers,
  gen/render.py                          pixel sprites, preview renderer
cosmetics.json                           id, name, rarity, kind of everything
previews/                                preview sheets (hats.png, backs.png ...)
```

Everything under `pack/assets/nexium/` except `pack.mcmeta` / `pack.png`
is generated: change the generator, not the files.

## Adding or changing a cosmetic

Each cosmetic is a small Python function that sets voxels. A new hat in
`tools/gen/hats.py`:

```python
@hat("pointy_hat", "Pointy Hat", "COMMON")
def pointy_hat():
    v = Vox("pointy_hat")
    # head = x/y/z 4..12, front = north; a cone from radius 3.5 at y = 12, 7 high
    cone(v, 8, 8, 3.5, 12, 7, C("ff5cc8"))
    return v
```

Back items go in `backs.py` (`@back`), outfits in `outfits.py`
(`@outfit`), pickaxe skins in `pickaxes.py`. Then:

```
pip install pillow
python tools/build_cos.py --preview
```

writes the models and textures into `pack/`, updates `cosmetics.json` and
draws `previews/*.png` so you can look at the result without starting
Minecraft. Push `pack/`, `tools/` and `cosmetics.json` together.

## Why the pack is so small

- One shared 64x64 palette texture for all voxel models (4x4 pixels per
  colour) instead of a texture per model.
- Greedy meshing: neighbouring voxels of the same colour become one box,
  hidden faces are left out.
- Minified JSON, the smallest lossless PNG (indexed when 256 colours or
  fewer), and a deterministic zip (sorted, fixed dates): the same files
  always give the same SHA-1, so players only download again when
  something really changed.

`tools/buildpack.py` checks every model before building: a texture that
doesn't exist stops the build (in game it would be the purple and black
"missing texture").

## Minecraft versions

`pack.mcmeta` says the pack works from 1.21.4 (format 46) to 26.2
(format 88): item model definitions (`items/`) need 1.21.4 or newer. When the
server moves to a newer Minecraft, raise `max_format` to that version's
resource pack format (Minecraft wiki, "Pack format").

## Building by hand

```
pip install pillow
python tools/buildpack.py
```

writes `build/NexiumPack.zip` and prints its SHA-1.
