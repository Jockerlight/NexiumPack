#!/usr/bin/env python3
"""The rainbow wave for chat text (REBIRTH / PRESTIGE lines).

    python tools/build_shaders.py

Text in one of the seven WAVE colours below (or in its shadow colour) is
drawn as a rainbow that runs along the text over time. Everything else is
drawn exactly like vanilla. The colours are a plain rainbow themselves, so a
client without the shader (older Minecraft) still shows a rainbow, just a
still one.

Minecraft's text vertex shader is replaced through pack overlays, one per
game version whose shader we know (the files differ between versions):
  pack/nx_wave_88/   26.2 (pack format 88)
  pack/nx_wave_97/   26.3 (pack format 97)
For another version: add its vanilla core/text.vsh below (from that
version's client jar), add the overlay to pack.mcmeta.

The server sends the wave colours, see sp_rb_line / sp_pr_line in the
SimuxPrison repository (40_progression/ranks.sk): the seven colours must
match WAVE here.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# the marker colours (a rainbow; no other text on the server uses them)
WAVE = [(250, 82, 82), (250, 168, 2), (250, 250, 82), (82, 250, 82), (82, 250, 250), (90, 140, 250), (174, 114, 250)]
PERIOD = 52.0      # GUI pixels for one full rainbow (about one bold word of 7 letters)
SPEED = 800.0      # GameTime runs 0..1 per 24000 ticks: 800 = one rainbow per 1.5 s

WAVE_GLSL = """
// NEXIUM: text in one of these colours (or their shadows: x 0.25) is drawn as
// a rainbow running along the text (tools/build_shaders.py in the pack repo)
const vec3 NX_WAVE[7] = vec3[7](%(cols)s);

vec4 nx_wave(vec4 color) {
    vec3 c = floor(color.rgb * 255.0 + 0.5);
    float k = 0.0;
    for (int i = 0; i < 7; i++) {
        if (all(equal(c, NX_WAVE[i]))) {
            k = 1.0;
        } else if (all(equal(c, floor(NX_WAVE[i] * 0.25)))) {
            k = 0.25;
        }
    }
    if (k == 0.0) {
        return color;
    }
    float h = fract(GameTime * %(speed)s - Position.x / %(period)s);
    vec3 rgb = clamp(abs(mod(h * 6.0 + vec3(0.0, 4.0, 2.0), 6.0) - 3.0) - 1.0, 0.0, 1.0);
    rgb = rgb * (2.0 / 3.0) + 1.0 / 3.0;
    return vec4(rgb * k, color.a);
}
"""

# vanilla 26.2 core/text.vsh, plus the globals import and nx_wave
TEXT_88 = """#version 330

#if !defined(IS_GUI) && !defined(IS_SEE_THROUGH)
#moj_import <minecraft:fog.glsl>
#moj_import <minecraft:sample_lightmap.glsl>
#endif

#moj_import <minecraft:dynamictransforms.glsl>
#moj_import <minecraft:projection.glsl>
#moj_import <minecraft:globals.glsl>

in vec3 Position;
in vec4 Color;
in vec2 UV0;
#if !defined(IS_GUI) && !defined(IS_SEE_THROUGH)
in ivec2 UV2;
#endif

#if !defined(IS_GUI) && !defined(IS_SEE_THROUGH)
uniform sampler2D Sampler2;
out float sphericalVertexDistance;
out float cylindricalVertexDistance;
#endif

out vec4 vertexColor;
out vec2 texCoord0;
%(wave)s
void main() {
    gl_Position = ProjMat * ModelViewMat * vec4(Position, 1.0);

#if !defined(IS_GUI) && !defined(IS_SEE_THROUGH)
    sphericalVertexDistance = fog_spherical_distance(Position);
    cylindricalVertexDistance = fog_cylindrical_distance(Position);
    vertexColor = nx_wave(Color) * sample_lightmap(Sampler2, UV2);
#else
    vertexColor = nx_wave(Color);
#endif
    texCoord0 = UV0;
}
"""

# vanilla 26.3 core/text.vsh, plus the globals include and nx_wave
TEXT_97 = """#version 330
#extension GL_ARB_separate_shader_objects : require

#if !defined(IS_GUI) && !defined(IS_SEE_THROUGH)
#include <minecraft:fog.glsl>
#include <minecraft:sample_lightmap.glsl>
#endif

#include <minecraft:dynamictransforms.glsl>
#include <minecraft:projection.glsl>
#include <minecraft:globals.glsl>

layout(location = 0) in vec3 Position;
layout(location = 1) in vec4 Color;
layout(location = 2) in vec2 UV0;
#if !defined(IS_GUI) && !defined(IS_SEE_THROUGH)
layout(location = 3) in ivec2 UV2;
#endif

#if !defined(IS_GUI) && !defined(IS_SEE_THROUGH)
uniform sampler2D Sampler2;
layout(location = 0) out float sphericalVertexDistance;
layout(location = 1) out float cylindricalVertexDistance;
#endif

layout(location = 2) out vec4 vertexColor;
layout(location = 3) out vec2 texCoord0;
%(wave)s
void main() {
    gl_Position = ProjMat * ModelViewMat * vec4(Position, 1.0);

#if !defined(IS_GUI) && !defined(IS_SEE_THROUGH)
    sphericalVertexDistance = fog_spherical_distance(Position);
    cylindricalVertexDistance = fog_cylindrical_distance(Position);
    vertexColor = nx_wave(Color) * sample_lightmap(Sampler2, UV2);
#else
    vertexColor = nx_wave(Color);
#endif
    texCoord0 = UV0;
}
"""

OVERLAYS = {"nx_wave_88": TEXT_88, "nx_wave_97": TEXT_97}


def wave_glsl():
    cols = ", ".join("vec3(%.1f, %.1f, %.1f)" % c for c in WAVE)
    return WAVE_GLSL % {"cols": cols, "speed": "%.1f" % SPEED, "period": "%.1f" % PERIOD}


def main():
    w = wave_glsl()
    for d, src in OVERLAYS.items():
        p = ROOT / "pack" / d / "assets" / "minecraft" / "shaders" / "core" / "text.vsh"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(src % {"wave": w}, encoding="utf-8")
        print("wrote", p.relative_to(ROOT))
    print("wave colours:", " ".join("%02X%02X%02X" % c for c in WAVE))


if __name__ == "__main__":
    main()
