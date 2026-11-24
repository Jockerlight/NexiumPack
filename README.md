# NexiumPack

The resource pack of the **NEXIUM** prison server (pickaxe skins and more).

Players never download anything by hand: the server's **NexiumPack**
plugin sends this pack to every player when they join.

## How a change reaches the players

1. Change files in `pack/` and push to `main` (the GitHub website's
   "Add file → Upload files" works too).
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

## Layout

```
pack/
  pack.mcmeta                                  name, description, formats
  pack.png                                     icon (128x128)
  assets/nexium/items/<name>.json              item model definition
  assets/nexium/models/item/<name>.json        3D/2D model
  assets/nexium/textures/item/<name>.png       texture
tools/
  buildpack.py                                 builds build/NexiumPack.zip
  draw_test_art.py                             draws the sample pickaxe + icon
```

Everything custom lives in the `nexium` namespace, so nothing of vanilla
Minecraft is replaced: a normal diamond pickaxe still looks normal.

## Adding a pickaxe skin

Example for a skin called `frost_pickaxe`:

1. Texture: `pack/assets/nexium/textures/item/frost_pickaxe.png`
   (16x16 or 32x32 pixels, transparent background).
2. Model: `pack/assets/nexium/models/item/frost_pickaxe.json`
   ```json
   {
     "parent": "minecraft:item/handheld",
     "textures": { "layer0": "nexium:item/frost_pickaxe" }
   }
   ```
3. Item model definition: `pack/assets/nexium/items/frost_pickaxe.json`
   ```json
   { "model": { "type": "minecraft:model", "model": "nexium:item/frost_pickaxe" } }
   ```
4. Push. After the release is out (about a minute) and the plugin picked it
   up, hold your pickaxe and type `/nexiumpack skin nexium:frost_pickaxe`
   (admins) to see it. `/nexiumpack skin off` puts the normal look back.

On the server, a skin is the `item_model` component of the pickaxe
(`nexium:frost_pickaxe`): the pickaxe stays a real pickaxe and only looks
different.

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
python tools/buildpack.py
```

writes `build/NexiumPack.zip` and prints its SHA-1. The zip is the same
byte for byte for the same files, so players only download the pack again
when something really changed.
