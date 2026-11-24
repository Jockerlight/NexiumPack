#version 330

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

// NEXIUM: text in one of these colours (or their shadows: x 0.25) is drawn as
// a rainbow running along the text (tools/build_shaders.py in the pack repo)
const vec3 NX_WAVE[7] = vec3[7](vec3(250.0, 82.0, 82.0), vec3(250.0, 168.0, 2.0), vec3(250.0, 250.0, 82.0), vec3(82.0, 250.0, 82.0), vec3(82.0, 250.0, 250.0), vec3(90.0, 140.0, 250.0), vec3(174.0, 114.0, 250.0));

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
    float h = fract(GameTime * 800.0 - Position.x / 52.0);
    vec3 rgb = clamp(abs(mod(h * 6.0 + vec3(0.0, 4.0, 2.0), 6.0) - 3.0) - 1.0, 0.0, 1.0);
    rgb = rgb * (2.0 / 3.0) + 1.0 / 3.0;
    return vec4(rgb * k, color.a);
}

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
