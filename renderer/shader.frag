vec3 gammaToLinear(in vec3 color) {
    return mix(
        color * (1.0 / 12.92),
        pow((color + 0.055) * (1.0 / 1.055), vec3(2.4)),
        step(0.04045, color)
    );
}

int getCombinerWord(int word) {
    switch (word) {
        case 0: return inState.combiner.x;
        case 1: return inState.combiner.y;
        case 2: return inState.combiner.z;
        case 3: return inState.combiner.w;
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
#define COMBINER_A_2A_SUBA ((getCombinerWord(COMBINER_A_2A_SUBA_WORD) >> COMBINER_A_2A_SUBA_SHIFT) & COMBINER_MASK)
#define COMBINER_A_2A_SUBB ((getCombinerWord(COMBINER_A_2A_SUBB_WORD) >> COMBINER_A_2A_SUBB_SHIFT) & COMBINER_MASK)
#define COMBINER_A_2A_MUL ((getCombinerWord(COMBINER_A_2A_MUL_WORD) >> COMBINER_A_2A_MUL_SHIFT) & COMBINER_MASK)
#define COMBINER_A_2A_ADD ((getCombinerWord(COMBINER_A_2A_ADD_WORD) >> COMBINER_A_2A_ADD_SHIFT) & COMBINER_MASK)
#define COMBINER_A_2B_SUBA ((getCombinerWord(COMBINER_A_2B_SUBA_WORD) >> COMBINER_A_2B_SUBA_SHIFT) & COMBINER_MASK)
#define COMBINER_A_2B_SUBB ((getCombinerWord(COMBINER_A_2B_SUBB_WORD) >> COMBINER_A_2B_SUBB_SHIFT) & COMBINER_MASK)
#define COMBINER_A_2B_MUL ((getCombinerWord(COMBINER_A_2B_MUL_WORD) >> COMBINER_A_2B_MUL_SHIFT) & COMBINER_MASK)
#define COMBINER_A_2B_ADD ((getCombinerWord(COMBINER_A_2B_ADD_WORD) >> COMBINER_A_2B_ADD_SHIFT) & COMBINER_MASK)

#define MISSING_COLOR vec4(1, 0, 1, 1)

float uv_compute_axis(int i, int axis) {
    int dim;
    float translate;
    int scale;
    float repeats;
    int flags;
    if (i == 0) {
        if (axis == 0) {
            dim = inState.tex0SDim;
            translate = inState.tex0STranslate;
            scale = inState.tex0SScale;
            repeats = inState.tex0SRepeats;
            flags = inState.tex0SFlags;
        } else {
            dim = inState.tex0TDim;
            translate = inState.tex0TTranslate;
            scale = inState.tex0TScale;
            repeats = inState.tex0TRepeats;
            flags = inState.tex0TFlags;
        }
    } else {
        if (axis == 0) {
            dim = inState.tex1SDim;
            translate = inState.tex1STranslate;
            scale = inState.tex1SScale;
            repeats = inState.tex1SRepeats;
            flags = inState.tex1SFlags;
        } else {
            dim = inState.tex1TDim;
            translate = inState.tex1TTranslate;
            scale = inState.tex1TScale;
            repeats = inState.tex1TRepeats;
            flags = inState.tex1TFlags;
        }
    }
    float v = axis == 0 ? uv.x : uv.y;
    if (scale < 0) {
        v *= 1 << -scale;
    } else {
        v /= 1 << scale;
    }
    v -= translate / dim;
    if ((flags & TEX_ST_FLAG_REPEATS_INF) == 0) {
        if (v < 0.5 / dim) {
            v = 0.5 / dim;
        } else if (v > repeats - 0.5 / dim) {
            v = repeats - 0.5 / dim;
        }
    }
    if ((flags & TEX_ST_FLAG_MIRROR) != 0) {
        v = mod(v, 2);
        if (v >= 1) {
            v = 2 - v;
        }
        v = clamp(v, 0.5 / dim, 1 - 0.5 / dim);
    }
    return v;
}

vec2 uv_compute(int i) {
    return vec2(uv_compute_axis(i, 0), uv_compute_axis(i, 1));
}

vec4 texture_wrap(int i) {
    if ((inState.validInputs & (i == 0 ? VALID_IN_TEX0 : VALID_IN_TEX1)) != 0
        && (inState.validInputs & VALID_IN_UV) != 0
        && (inState.validInputs & (i == 0 ? VALID_IN_TEX0_ST : VALID_IN_TEX1_ST)) != 0
    ) {
        if (i == 0) {
            return texture(inTex0, uv_compute(i));
        } else {
            return texture(inTex1, uv_compute(i));
        }
    } else {
        return MISSING_COLOR;
    }
}

vec3 combinerEvaluateSlotRGB(int slot, vec3 prevCycleCombinedRGB, float prevCycleCombinedA) {
    switch (slot) {
        case COMBINER_0: return vec3(0);
        case COMBINER_1: return vec3(1);
        case COMBINER_ENV: return (inState.validInputs & VALID_IN_COMBINER_REG_ENV) != 0 ? inState.combinerRegEnv.rgb : MISSING_COLOR.rgb;
        case COMBINER_ENV_ALPHA: return (inState.validInputs & VALID_IN_COMBINER_REG_ENV) != 0 ? vec3(inState.combinerRegEnv.a) : MISSING_COLOR.rgb;
        case COMBINER_K4: return (inState.validInputs & VALID_IN_COMBINER_REG_K4) != 0 ? vec3(inState.combinerRegK4) : MISSING_COLOR.rgb;
        case COMBINER_K5: return (inState.validInputs & VALID_IN_COMBINER_REG_K5) != 0 ? vec3(inState.combinerRegK5) : MISSING_COLOR.rgb;
        case COMBINER_KEYCENTER: return MISSING_COLOR.rgb; // TODO
        case COMBINER_KEYSCALE: return MISSING_COLOR.rgb; // TODO
        case COMBINER_LOD_FRAC: return MISSING_COLOR.rgb; // TODO
        case COMBINER_NOISE: return MISSING_COLOR.rgb; // TODO
        case COMBINER_PRIM: return (inState.validInputs & VALID_IN_COMBINER_REG_PRIM) != 0 ? inState.combinerRegPrim.rgb : MISSING_COLOR.rgb;
        case COMBINER_PRIM_ALPHA: return (inState.validInputs & VALID_IN_COMBINER_REG_PRIM) != 0 ? vec3(inState.combinerRegPrim.a) : MISSING_COLOR.rgb;
        case COMBINER_PRIM_LOD_FRAC: return (inState.validInputs & VALID_IN_COMBINER_REG_PRIM_LOD_FRAC) != 0 ? vec3(inState.combinerRegPrimLODFrac) : MISSING_COLOR.rgb;
        case COMBINER_SHADE: return gammaToLinear(shadeColor.rgb);
        case COMBINER_SHADE_ALPHA: return vec3(shadeColor.a);
        case COMBINER_TEX0: return texture_wrap(0).rgb;
        case COMBINER_TEX0_ALPHA: return vec3(texture_wrap(0).a);
        case COMBINER_TEX1: return texture_wrap(1).rgb;
        case COMBINER_TEX1_ALPHA: return vec3(texture_wrap(1).a);
        case COMBINER_COMBINED: return prevCycleCombinedRGB;
        case COMBINER_COMBINED_ALPHA: return vec3(prevCycleCombinedA);
    }
}

float combinerEvaluateSlotA(int slot, float prevCycleCombinedA) {
    switch (slot) {
        case COMBINER_0: return 0;
        case COMBINER_1: return 1;
        case COMBINER_ENV: return (inState.validInputs & VALID_IN_COMBINER_REG_ENV) != 0 ? inState.combinerRegEnv.a : MISSING_COLOR.a;
        case COMBINER_LOD_FRAC: return MISSING_COLOR.a; // TODO
        case COMBINER_PRIM: return (inState.validInputs & VALID_IN_COMBINER_REG_PRIM) != 0 ? inState.combinerRegPrim.a : MISSING_COLOR.a;
        case COMBINER_PRIM_LOD_FRAC: return (inState.validInputs & VALID_IN_COMBINER_REG_PRIM_LOD_FRAC) != 0 ? inState.combinerRegPrimLODFrac : MISSING_COLOR.a;
        case COMBINER_SHADE: return shadeColor.a;
        case COMBINER_TEX0: return texture_wrap(0).a;
        case COMBINER_TEX1: return texture_wrap(1).a;
        case COMBINER_COMBINED: return prevCycleCombinedA;
    }
}

vec3 combinerEvaluateCycleRGB(int suba, int subb, int mul, int add, vec3 prevCycleCombinedRGB, float prevCycleCombinedA) {
    // TODO handle clamp/overflow
    return (
        combinerEvaluateSlotRGB(suba, prevCycleCombinedRGB, prevCycleCombinedA)
        - combinerEvaluateSlotRGB(subb, prevCycleCombinedRGB, prevCycleCombinedA)
    ) * combinerEvaluateSlotRGB(mul, prevCycleCombinedRGB, prevCycleCombinedA)
    + combinerEvaluateSlotRGB(add, prevCycleCombinedRGB, prevCycleCombinedA);
}

float combinerEvaluateCycleA(int suba, int subb, int mul, int add, float prevCycleCombinedA) {
    // TODO handle clamp/overflow
    return (
        combinerEvaluateSlotA(suba, prevCycleCombinedA)
        - combinerEvaluateSlotA(subb, prevCycleCombinedA)
    ) * combinerEvaluateSlotA(mul, prevCycleCombinedA)
    + combinerEvaluateSlotA(add, prevCycleCombinedA);
}

void main() 
{
    vec3 combinedRGB;
    float combinedAlphaA, combinedAlphaB;
    combinedRGB = combinerEvaluateCycleRGB(
        COMBINER_RGB_2A_SUBA, COMBINER_RGB_2A_SUBB,
        COMBINER_RGB_2A_MUL, COMBINER_RGB_2A_ADD,
        vec3(0), 0
    );
    combinedAlphaA = combinerEvaluateCycleA(
        COMBINER_A_2A_SUBA, COMBINER_A_2A_SUBB,
        COMBINER_A_2A_MUL, COMBINER_A_2A_ADD,
        0
    );
    combinedRGB = combinerEvaluateCycleRGB(
        COMBINER_RGB_2B_SUBA, COMBINER_RGB_2B_SUBB,
        COMBINER_RGB_2B_MUL, COMBINER_RGB_2B_ADD,
        combinedRGB, combinedAlphaA
    );
    combinedAlphaB = combinerEvaluateCycleA(
        COMBINER_A_2B_SUBA, COMBINER_A_2B_SUBB,
        COMBINER_A_2B_MUL, COMBINER_A_2B_ADD,
        combinedAlphaA
    );
    float alpha;
    if ((inState.generalFlags & GENERAL_FLAG_ALPHA_COMPARE) == 0) {
        alpha = combinedAlphaB;
    } else {
        // Note: RDP silicon bug, compare first cycle output
        if (combinedAlphaA >= inState.alphaCompareThreshold) {
            // TODO is this correct? (could be alpha=1 ?)
            alpha = combinedAlphaB;
        } else {
            discard;
        }
    }
    FragColor = vec4(combinedRGB, alpha);
}
