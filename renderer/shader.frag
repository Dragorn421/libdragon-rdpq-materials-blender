uniform int inValidInputs;
uniform sampler2D inTex0;
uniform ivec4 inCombiner;

in vec4 shadeColor;
in vec2 uv;

out vec4 FragColor;

vec3 gammaToLinear(in vec3 color) {
    return mix(
        color * (1.0 / 12.92),
        pow((color + 0.055) * (1.0 / 1.055), vec3(2.4)),
        step(0.04045, color)
    );
}

int getCombinerWord(int word) {
    switch (word) {
        case 0: return inCombiner.x;
        case 1: return inCombiner.y;
        case 2: return inCombiner.z;
        case 3: return inCombiner.w;
    }
}

#define COMBINER_RGB_2A_SUBA ((getCombinerWord(COMBINER_RGB_2A_SUBA_WORD) >> COMBINER_RGB_2A_SUBA_SHIFT) & COMBINER_MASK)
#define COMBINER_RGB_2A_SUBB ((getCombinerWord(COMBINER_RGB_2A_SUBB_WORD) >> COMBINER_RGB_2A_SUBB_SHIFT) & COMBINER_MASK)
#define COMBINER_RGB_2A_MUL ((getCombinerWord(COMBINER_RGB_2A_MUL_WORD) >> COMBINER_RGB_2A_MUL_SHIFT) & COMBINER_MASK)
#define COMBINER_RGB_2A_ADD ((getCombinerWord(COMBINER_RGB_2A_ADD_WORD) >> COMBINER_RGB_2A_ADD_SHIFT) & COMBINER_MASK)
#define COMBINER_RGB_2B_SUBA ((getCombinerWord(COMBINER_RGB_2B_SUBA_WORD) >> COMBINER_RGB_2B_SUBA_SHIFT) & COMBINER_MASK)
#define COMBINER_RGB_2B_SUBB ((getCombinerWord(COMBINER_RGB_2B_SUBB_WORD) >> COMBINER_RGB_2B_SUBB_SHIFT) & COMBINER_MASK)
#define COMBINER_RGB_2B_MUL ((getCombinerWord(COMBINER_RGB_2B_MUL_WORD) >> COMBINER_RGB_2B_MUL_SHIFT) & COMBINER_MASK)
#define COMBINER_RGB_2B_ADD ((getCombinerWord(COMBINER_RGB_2B_ADD_WORD) >> COMBINER_RGB_2B_ADD_SHIFT) & COMBINER_MASK)

vec4 texture_wrap(sampler2D tex, vec2 uv) {
    if ((inValidInputs & VALID_IN_TEX0) != 0 && (inValidInputs & VALID_IN_UV) != 0)
        return texture(tex, uv);
    else
        return vec4(1, 0, 1, 1);
}

vec3 combinerEvaluateSlotRGB(int slot, vec3 prevCycleCombined) {
    switch (slot) {
        case COMBINER_0: return vec3(0);
        case COMBINER_1: return vec3(1);
        case COMBINER_ENV: return vec3(0); // TODO
        case COMBINER_ENV_ALPHA: return vec3(0); // TODO
        case COMBINER_K4: return vec3(0); // TODO
        case COMBINER_K5: return vec3(0); // TODO
        case COMBINER_KEYCENTER: return vec3(0); // TODO
        case COMBINER_KEYSCALE: return vec3(0); // TODO
        case COMBINER_LOD_FRAC: return vec3(0); // TODO
        case COMBINER_NOISE: return vec3(0); // TODO
        case COMBINER_PRIM: return vec3(0); // TODO
        case COMBINER_PRIM_ALPHA: return vec3(0); // TODO
        case COMBINER_PRIM_LOD_FRAC: return vec3(0); // TODO
        case COMBINER_SHADE: return gammaToLinear(shadeColor.rgb);
        case COMBINER_SHADE_ALPHA: return vec3(shadeColor.a);
        case COMBINER_TEX0: return texture_wrap(inTex0, uv).rgb;
        case COMBINER_TEX0_ALPHA: return vec3(texture_wrap(inTex0, uv).a);
        case COMBINER_TEX1: return vec3(0); // TODO
        case COMBINER_TEX1_ALPHA: return vec3(0); // TODO
        case COMBINER_COMBINED: return prevCycleCombined;
    }
}

vec3 combinerEvaluateCycleRGB(int suba, int subb, int mul, int add, vec3 prevCycleCombined) {
    // TODO handle clamp/overflow
    return (
        combinerEvaluateSlotRGB(suba, prevCycleCombined)
        - combinerEvaluateSlotRGB(subb, prevCycleCombined)
    ) * combinerEvaluateSlotRGB(mul, prevCycleCombined)
    + combinerEvaluateSlotRGB(add, prevCycleCombined);
}

void main() 
{
    vec3 combined;
    combined = combinerEvaluateCycleRGB(
        COMBINER_RGB_2A_SUBA, COMBINER_RGB_2A_SUBB,
        COMBINER_RGB_2A_MUL, COMBINER_RGB_2A_ADD,
        vec3(0)
    );
    combined = combinerEvaluateCycleRGB(
        COMBINER_RGB_2B_SUBA, COMBINER_RGB_2B_SUBB,
        COMBINER_RGB_2B_MUL, COMBINER_RGB_2B_ADD,
        combined
    );
    FragColor = vec4(combined, 1);
}
