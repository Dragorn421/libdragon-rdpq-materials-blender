bl_info = {
    "name": "libdragon RDPQ materials",
    "version": (0, 0, 1),
    "author": "Dragorn421",
    "location": "Material Properties",
    "description": "RDPQ materials for the libdragon N64 homebrew SDK",
    "category": "Material",
    "blender": (3, 2, 0),
}

import dataclasses
from typing import Iterable, Literal

import bpy
import bpy.utils


class RDPQMaterialTextureAxisProperties(bpy.types.PropertyGroup):
    translate: bpy.props.FloatProperty(
        name="Translate",
        description="",
        default=0,
    )
    scale: bpy.props.IntProperty(
        name="Scale",
        description="",
        default=0,
    )
    repeats_inf: bpy.props.BoolProperty(
        name="Repeats Infinitely",
        description="",
        default=False,
    )
    repeats: bpy.props.FloatProperty(
        name="Repeats",
        description="",
        default=1,
    )
    mirror: bpy.props.BoolProperty(
        name="Mirror",
        description="",
        default=False,
    )


class RDPQMaterialTextureProperties(bpy.types.PropertyGroup):
    use_texture: bpy.props.BoolProperty(
        name="Use Texture",
        description="",
        default=True,
    )
    use_placeholder: bpy.props.BoolProperty(
        name="Use Placeholder",
        description="",
        default=False,
    )
    placeholder: bpy.props.IntProperty(
        name="Placeholder",
        description="",
        default=1,
        min=1,
        max=15,
    )
    format: bpy.props.EnumProperty(
        name="Format",
        description="",
        items=(
            ("AUTO", "Auto", ""),
            ("I4", "I4", ""),
            ("I8", "I8", ""),
            # TODO fill in
            ("SHQ", "SHQ", ""),
            ("IHQ", "IHQ", ""),
        ),
        default="AUTO",
    )
    mipmap: bpy.props.EnumProperty(
        name="Mipmap",
        description="",
        items=(
            ("NONE", "None", ""),
            ("BOX", "Box", ""),
        ),
        default="NONE",
    )
    dithering: bpy.props.EnumProperty(
        name="Dithering",
        description="",
        items=(
            ("NONE", "None", ""),
            ("RANDOM", "Random", ""),
            ("ORDERED", "Ordered", ""),
        ),
        default="NONE",
    )
    s_: bpy.props.PointerProperty(type=RDPQMaterialTextureAxisProperties)
    t_: bpy.props.PointerProperty(type=RDPQMaterialTextureAxisProperties)

    @property
    def s(self) -> RDPQMaterialTextureAxisProperties:
        return self.s_

    @property
    def t(self) -> RDPQMaterialTextureAxisProperties:
        return self.t_


# https://n64brew.dev/wiki/Reality_Display_Processor/Commands?oldid=5601#0x3C_-_Set_Combine_Mode
rgb_A_inputs_items = (
    ("COMBINED", "COMBINED", "Combined color from first cycle"),
    (
        "TEX0",
        "TEX0",
        "Texture color sampled from the tile set in the primitive command, after texture LOD if enabled",
    ),
    (
        "TEX1",
        "TEX1",
        "Texture color sampled from the tile set in the primitive command, after texture LOD if enabled, plus one (mod 8, e.g. if TEX0 refers to tile 7, TEX1 refers to tile 0)",
    ),
    ("PRIMITIVE", "PRIMITIVE", "Primitive color register (rgb)"),
    ("SHADE", "SHADE", "Shade color interpolated per-pixel from shade coefficients"),
    ("ENVIRONMENT", "ENVIRONMENT", "Environment color register (rgb)"),
    ("1", "1", "Fixed 1"),
    (
        "NOISE",
        "NOISE",
        "Per-pixel noise. This is a 9-bit value whose top 3 bits are random, while the bottom 6 are fixed to 0b100000 (0x20).",
    ),
    ("0", "0", "Fixed 0"),
)
rgb_B_inputs_items = (
    ("COMBINED", "COMBINED", "Combined color from first cycle"),
    (
        "TEX0",
        "TEX0",
        "Texture color sampled from the tile set in the primitive command, after texture LOD if enabled",
    ),
    (
        "TEX1",
        "TEX1",
        "Texture color sampled from the tile set in the primitive command, after texture LOD if enabled, plus one (mod 8, e.g. if TEX0 refers to tile 7, TEX1 refers to tile 0)",
    ),
    ("PRIMITIVE", "PRIMITIVE", "Primitive color register (rgb)"),
    ("SHADE", "SHADE", "Shade color interpolated per-pixel from shade coefficients"),
    ("ENVIRONMENT", "ENVIRONMENT", "Environment color register (rgb)"),
    ("CENTER", "CENTER", "Chroma key center (see Set Key R and Set Key GB)"),
    ("K4", "K4", "K4 value (see Set Convert)"),
    ("0", "0", "Fixed 0"),
)
rgb_C_inputs_items = (
    ("COMBINED", "COMBINED", "Combined color from first cycle"),
    (
        "TEX0",
        "TEX0",
        "Texture color sampled from the tile set in the primitive command, after texture LOD if enabled",
    ),
    (
        "TEX1",
        "TEX1",
        "Texture color sampled from the tile set in the primitive command, after texture LOD if enabled, plus one (mod 8, e.g. if TEX0 refers to tile 7, TEX1 refers to tile 0)",
    ),
    ("PRIMITIVE", "PRIMITIVE", "Primitive color register (rgb)"),
    ("SHADE", "SHADE", "Shade color interpolated per-pixel from shade coefficients"),
    ("ENVIRONMENT", "ENVIRONMENT", "Environment color register (rgb)"),
    ("SCALE", "SCALE", "Chroma key scale (see Set Key R and Set Key GB)"),
    ("COMBINED_ALPHA", "COMBINED_ALPHA", "Combined alpha from first cycle"),
    (
        "TEX0_ALPHA",
        "TEX0_ALPHA",
        "Texture alpha sampled from the tile set in the primitive command, after texture LOD if enabled",
    ),
    (
        "TEX1_ALPHA",
        "TEX1_ALPHA",
        "Texture alpha sampled from the tile set in the primitive command, after texture LOD if enabled, plus one",
    ),
    ("PRIMITIVE_ALPHA", "PRIMITIVE_ALPHA", "Primitive color register (alpha)"),
    (
        "SHADE_ALPHA",
        "SHADE_ALPHA",
        "Shade alpha interpolated per-pixel from shade coefficients",
    ),
    ("ENVIRONMENT_ALPHA", "ENVIRONMENT_ALPHA", "Environment color register (alpha)"),
    ("LOD_FRACTION", "LOD_FRACTION", "LOD Fraction computed as part of Texture LOD"),
    (
        "PRIM_LOD_FRAC",
        "PRIM_LOD_FRAC",
        "Primitive LOD Fraction (see Set Primitive Color)",
    ),
    ("K5", "K5", "K5 value (see Set Convert)"),
    ("0", "0", "Fixed 0"),
)
rgb_D_inputs_items = (
    ("COMBINED", "COMBINED", "Combined color from first cycle"),
    (
        "TEX0",
        "TEX0",
        "Texture color sampled from the tile set in the primitive command, after texture LOD if enabled",
    ),
    (
        "TEX1",
        "TEX1",
        "Texture color sampled from the tile set in the primitive command, after texture LOD if enabled, plus one (mod 8, e.g. if TEX0 refers to tile 7, TEX1 refers to tile 0)",
    ),
    ("PRIMITIVE", "PRIMITIVE", "Primitive color register (rgb)"),
    ("SHADE", "SHADE", "Shade color interpolated per-pixel from shade coefficients"),
    ("ENVIRONMENT", "ENVIRONMENT", "Environment color register (rgb)"),
    ("1", "1", "Fixed 1"),
    ("0", "0", "Fixed 0"),
)

alpha_A_inputs_items = (
    ("COMBINED", "COMBINED", "Combined alpha from first cycle"),
    (
        "TEX0",
        "TEX0",
        "Texture alpha sampled from the tile set in the primitive command, after texture LOD if enabled",
    ),
    (
        "TEX1",
        "TEX1",
        "Texture alpha sampled from the tile set in the primitive command, after texture LOD if enabled, plus one (mod 8, e.g. if TEX0 refers to tile 7, TEX1 refers to tile 0)",
    ),
    ("PRIMITIVE", "PRIMITIVE", "Primitive color register (alpha)"),
    ("SHADE", "SHADE", "Shade alpha interpolated per-pixel from shade coefficients"),
    ("ENVIRONMENT", "ENVIRONMENT", "Environment color register (alpha)"),
    ("1", "1", "Fixed 1"),
    ("0", "0", "Fixed 0"),
)
alpha_B_inputs_items = (
    ("COMBINED", "COMBINED", "Combined alpha from first cycle"),
    (
        "TEX0",
        "TEX0",
        "Texture alpha sampled from the tile set in the primitive command, after texture LOD if enabled",
    ),
    (
        "TEX1",
        "TEX1",
        "Texture alpha sampled from the tile set in the primitive command, after texture LOD if enabled, plus one (mod 8, e.g. if TEX0 refers to tile 7, TEX1 refers to tile 0)",
    ),
    ("PRIMITIVE", "PRIMITIVE", "Primitive color register (alpha)"),
    ("SHADE", "SHADE", "Shade alpha interpolated per-pixel from shade coefficients"),
    ("ENVIRONMENT", "ENVIRONMENT", "Environment color register (alpha)"),
    ("1", "1", "Fixed 1"),
    ("0", "0", "Fixed 0"),
)
alpha_C_inputs_items = (
    ("LOD_FRACTION", "LOD_FRACTION", "LOD Fraction computed as part of Texture LOD"),
    (
        "TEX0",
        "TEX0",
        "Texture alpha sampled from the tile set in the primitive command, after texture LOD if enabled",
    ),
    (
        "TEX1",
        "TEX1",
        "Texture alpha sampled from the tile set in the primitive command, after texture LOD if enabled, plus one (mod 8, e.g. if TEX0 refers to tile 7, TEX1 refers to tile 0)",
    ),
    ("PRIMITIVE", "PRIMITIVE", "Primitive color register (alpha)"),
    ("SHADE", "SHADE", "Shade alpha interpolated per-pixel from shade coefficients"),
    ("ENVIRONMENT", "ENVIRONMENT", "Environment color register (alpha)"),
    (
        "PRIM_LOD_FRAC",
        "PRIM_LOD_FRAC",
        "Primitive LOD Fraction (see Set Primitive Color)",
    ),
    ("0", "0", "Fixed 0"),
)
alpha_D_inputs_items = (
    ("COMBINED", "COMBINED", "Combined alpha from first cycle"),
    (
        "TEX0",
        "TEX0",
        "Texture alpha sampled from the tile set in the primitive command, after texture LOD if enabled",
    ),
    (
        "TEX1",
        "TEX1",
        "Texture alpha sampled from the tile set in the primitive command, after texture LOD if enabled, plus one (mod 8, e.g. if TEX0 refers to tile 7, TEX1 refers to tile 0)",
    ),
    ("PRIMITIVE", "PRIMITIVE", "Primitive color register (alpha)"),
    ("SHADE", "SHADE", "Shade alpha interpolated per-pixel from shade coefficients"),
    ("ENVIRONMENT", "ENVIRONMENT", "Environment color register (alpha)"),
    ("1", "1", "Fixed 1"),
    ("0", "0", "Fixed 0"),
)


def combiner_items(items: Iterable[tuple[str, str, str]], cycle: Literal[0, 1]):
    new_items: list[tuple[str, str, str]] = []
    for id, name, desc in items:
        if cycle == 0 and id in {"COMBINED", "COMBINED_ALPHA"}:
            continue
        if cycle == 1 and id == "TEX0":
            id = "TEX1"
            name = "TEX1"
        elif cycle == 1 and id == "TEX1":
            id = "TEX0_BUG"
            name = "TEX0_BUG"
        new_items.append((id, name, desc))
    return new_items


class RDPQMaterialCombinerProperties(bpy.types.PropertyGroup):
    preset: bpy.props.EnumProperty(
        name="Combiner Preset",
        description="",
        items=(
            ("FLAT", "Flat", ""),
            ("SHADE", "Shade", ""),
            ("TEX", "Tex", ""),
            ("TEX_FLAT", "Tex Flat", ""),
            ("TEX_SHADE", "Tex Shade", ""),
            ("CUSTOM_1_PASS", "Custom 1 Pass", ""),
            ("CUSTOM_2_PASSES", "Custom 2 Passes", ""),
        ),
        default="TEX",
    )

    rgb_A_0: bpy.props.EnumProperty(
        name="RGB A 1",
        description="RGB A Input (First Cycle)",
        items=combiner_items(rgb_A_inputs_items, 0),
    )
    rgb_B_0: bpy.props.EnumProperty(
        name="RGB B 1",
        description="RGB B Input (First Cycle)",
        items=combiner_items(rgb_B_inputs_items, 0),
    )
    rgb_C_0: bpy.props.EnumProperty(
        name="RGB C 1",
        description="RGB C Input (First Cycle)",
        items=combiner_items(rgb_C_inputs_items, 0),
    )
    rgb_D_0: bpy.props.EnumProperty(
        name="RGB D 1",
        description="RGB D Input (First Cycle)",
        items=combiner_items(rgb_D_inputs_items, 0),
    )

    alpha_A_0: bpy.props.EnumProperty(
        name="Alpha A 1",
        description="RGB A Input (First Cycle)",
        items=combiner_items(alpha_A_inputs_items, 0),
    )
    alpha_B_0: bpy.props.EnumProperty(
        name="Alpha B 1",
        description="RGB B Input (First Cycle)",
        items=combiner_items(alpha_B_inputs_items, 0),
    )
    alpha_C_0: bpy.props.EnumProperty(
        name="Alpha C 1",
        description="RGB C Input (First Cycle)",
        items=combiner_items(alpha_C_inputs_items, 0),
    )
    alpha_D_0: bpy.props.EnumProperty(
        name="Alpha D 1",
        description="RGB D Input (First Cycle)",
        items=combiner_items(alpha_D_inputs_items, 0),
    )

    rgb_A_1: bpy.props.EnumProperty(
        name="RGB A 2",
        description="RGB A Input (Second Cycle)",
        items=combiner_items(rgb_A_inputs_items, 1),
    )
    rgb_B_1: bpy.props.EnumProperty(
        name="RGB B 2",
        description="RGB B Input (Second Cycle)",
        items=combiner_items(rgb_B_inputs_items, 1),
    )
    rgb_C_1: bpy.props.EnumProperty(
        name="RGB C 2",
        description="RGB C Input (Second Cycle)",
        items=combiner_items(rgb_C_inputs_items, 1),
    )
    rgb_D_1: bpy.props.EnumProperty(
        name="RGB D 2",
        description="RGB D Input (Second Cycle)",
        items=combiner_items(rgb_D_inputs_items, 1),
    )

    alpha_A_1: bpy.props.EnumProperty(
        name="Alpha A 2",
        description="RGB A Input (Second Cycle)",
        items=combiner_items(alpha_A_inputs_items, 1),
    )
    alpha_B_1: bpy.props.EnumProperty(
        name="Alpha B 2",
        description="RGB B Input (Second Cycle)",
        items=combiner_items(alpha_B_inputs_items, 1),
    )
    alpha_C_1: bpy.props.EnumProperty(
        name="Alpha C 2",
        description="RGB C Input (Second Cycle)",
        items=combiner_items(alpha_C_inputs_items, 1),
    )
    alpha_D_1: bpy.props.EnumProperty(
        name="Alpha D 2",
        description="RGB D Input (Second Cycle)",
        items=combiner_items(alpha_D_inputs_items, 1),
    )


# names and description from https://n64brew.dev/wiki/Reality_Display_Processor/Commands?oldid=5601#0x2F_-_Set_Other_Modes (CC BY-SA 4.0)
blender_P_M_inputs_items = (
    (
        "INPUT",
        "Input",
        "First cycle: output color from Color Combiner final stage; Second cycle: output color from first blender cycle",
    ),
    ("MEMORY", "Memory", "Memory color from framebuffer"),
    ("BLEND_COLOR", "Blend Color", "Blend color register RGB"),
    ("FOG_COLOR", "Fog Color", "Fog color register RGB "),
)
blender_A_inputs_items = (
    ("INPUT_ALPHA", "Input Alpha", "Output alpha from Color Combiner final stage"),
    ("FOG_ALPHA", "Fog Alpha", "Fog color register Alpha"),
    ("SHADE_ALPHA", "Shade Alpha", "Shade Alpha (interpolated per-pixel)"),
    ("0", "0", "Fixed 0.0"),
)
blender_B_inputs_items = (
    ("1_MINUS_A", "1 - A", "1.0 - A, where A is the other alpha input"),
    ("MEMORY_COVERAGE", "Memory Coverage", "Memory coverage from framebuffer"),
    ("1", "1", "Fixed 1.0"),
    ("0", "0", "Fixed 0.0"),
)


class RDPQMaterialBlenderProperties(bpy.types.PropertyGroup):
    preset: bpy.props.EnumProperty(
        name="Blender Preset",
        description="",
        items=(
            ("NONE", "None", ""),
            ("MULTIPLY", "Multiply", ""),
            ("MULTIPLY_CONST", "Multiply Const", ""),
            ("ADDITIVE", "Additive", ""),
            ("CUSTOM_1_PASS", "Custom 1 Pass", ""),
            ("CUSTOM_2_PASSES", "Custom 2 Passes", ""),
        ),
    )

    p_0: bpy.props.EnumProperty(
        name="P1",
        description="Blender input P (first cycle)",
        items=blender_P_M_inputs_items,
    )
    a_0: bpy.props.EnumProperty(
        name="A1",
        description="Blender input A (first cycle)",
        items=blender_A_inputs_items,
    )
    m_0: bpy.props.EnumProperty(
        name="M1",
        description="Blender input M (first cycle)",
        items=blender_P_M_inputs_items,
    )
    b_0: bpy.props.EnumProperty(
        name="B1",
        description="Blender input B (first cycle)",
        items=blender_B_inputs_items,
    )

    p_1: bpy.props.EnumProperty(
        name="P2",
        description="Blender input P (second cycle)",
        items=blender_P_M_inputs_items,
    )
    a_1: bpy.props.EnumProperty(
        name="A2",
        description="Blender input A (second cycle)",
        items=blender_A_inputs_items,
    )
    m_1: bpy.props.EnumProperty(
        name="M2",
        description="Blender input M (second cycle)",
        items=blender_P_M_inputs_items,
    )
    b_1: bpy.props.EnumProperty(
        name="B2",
        description="Blender input B (second cycle)",
        items=blender_B_inputs_items,
    )

    blend_color: bpy.props.FloatVectorProperty(
        name="Blend Color",
        description="",
        default=(1, 1, 1, 1),
        min=0,
        max=1,
        subtype="COLOR",
        size=4,
    )
    fog_color: bpy.props.FloatVectorProperty(
        name="Fog Color",
        description="",
        default=(1, 1, 1, 1),
        min=0,
        max=1,
        subtype="COLOR",
        size=4,
    )


class RDPQMaterialOverrideRenderModeProperties(bpy.types.PropertyGroup):
    override_antialias: bpy.props.BoolProperty(
        name="Override Antialias",
        description="",
    )
    antialias: bpy.props.EnumProperty(
        name="Antialias",
        description="",
        items=(
            ("NONE", "None", ""),
            ("STANDARD", "Standard", ""),
            ("REDUCED", "Reduced", ""),
        ),
        default="STANDARD",
    )

    override_fog: bpy.props.BoolProperty(
        name="Override Fog",
        description="",
    )
    fog: bpy.props.EnumProperty(
        name="Fog",
        description="",
        items=(
            ("NONE", "None", ""),
            ("STANDARD", "Standard", ""),
            ("CUSTOM", "Custom", ""),
        ),
        default="STANDARD",
    )

    override_dithering: bpy.props.BoolProperty(
        name="Override Dithering",
        description="",
    )
    dithering: bpy.props.EnumProperty(
        name="Dithering",
        description="",
        items=(
            ("RGB_SQUARE_A_SQUARE", "rgb=SQUARE alpha=SQUARE", ""),
            ("RGB_SQUARE_A_INVSQUARE", "rgb=SQUARE alpha=INVSQUARE", ""),
            ("RGB_SQUARE_A_NOISE", "rgb=SQUARE alpha=NOISE", ""),
            ("RGB_SQUARE_A_NONE", "rgb=SQUARE alpha=NONE", ""),
            ("RGB_BAYER_A_BAYER", "rgb=BAYER alpha=BAYER", ""),
            ("RGB_BAYER_A_INVBAYER", "rgb=BAYER alpha=INVBAYER", ""),
            ("RGB_BAYER_A_NOISE", "rgb=BAYER alpha=NOISE", ""),
            ("RGB_BAYER_A_NONE", "rgb=BAYER alpha=NONE", ""),
            ("RGB_NOISE_A_SQUARE", "rgb=NOISE alpha=SQUARE", ""),
            ("RGB_NOISE_A_INVSQUARE", "rgb=NOISE alpha=INVSQUARE", ""),
            ("RGB_NOISE_A_NOISE", "rgb=NOISE alpha=NOISE", ""),
            ("RGB_NOISE_A_NONE", "rgb=NOISE alpha=NONE", ""),
            ("RGB_NONE_A_BAYER", "rgb=NONE alpha=BAYER", ""),
            ("RGB_NONE_A_INVBAYER", "rgb=NONE alpha=INVBAYER", ""),
            ("RGB_NONE_A_NOISE", "rgb=NONE alpha=NOISE", ""),
            ("RGB_NONE_A_NONE", "rgb=NONE alpha=NONE", ""),
        ),
    )

    override_texture_filtering: bpy.props.BoolProperty(
        name="Override Texture Filtering",
        description="",
    )
    texture_filtering: bpy.props.EnumProperty(
        name="Texture Filtering",
        description="",
        items=(
            ("POINT", "Point", ""),
            ("BILINEAR", "Bilinear", ""),
            ("MEDIAN", "Median", ""),
        ),
        default="BILINEAR",
    )

    override_texture_perspective_correction: bpy.props.BoolProperty(
        name="Override Texture Perspective Correction",
        description="",
    )
    texture_perspective_correction: bpy.props.BoolProperty(
        name="Texture Perspective Correction",
        description="",
        default=True,
    )

    override_alpha_compare: bpy.props.BoolProperty(
        name="Override Alpha Compare",
        description="",
    )
    alpha_compare_threshold: bpy.props.IntProperty(
        name="Alpha Compare Threshold",
        description="",
        default=127,
        min=0,
        max=255,
    )

    override_z_compare: bpy.props.BoolProperty(
        name="Override Z Compare",
        description="",
    )
    z_compare: bpy.props.BoolProperty(
        name="Z Compare",
        description="",
        default=True,
    )

    override_z_update: bpy.props.BoolProperty(
        name="Override Z Update",
        description="",
    )
    z_update: bpy.props.BoolProperty(
        name="Z Update",
        description="",
        default=True,
    )

    override_fixed_z: bpy.props.BoolProperty(
        name="Override Fixed Z",
        description="",
    )
    fixed_z: bpy.props.IntProperty(
        name="Fixed Z",
        description="",
    )
    fixed_z_deltaz: bpy.props.IntProperty(
        name="Fixed Z deltaz",
        description="",
    )


class RDPQMaterialProperties(bpy.types.PropertyGroup):
    texture_: bpy.props.PointerProperty(type=RDPQMaterialTextureProperties)
    combiner_: bpy.props.PointerProperty(type=RDPQMaterialCombinerProperties)
    blender_: bpy.props.PointerProperty(type=RDPQMaterialBlenderProperties)
    override_render_mode_: bpy.props.PointerProperty(
        type=RDPQMaterialOverrideRenderModeProperties
    )

    @property
    def texture(self) -> RDPQMaterialTextureProperties:
        return self.texture_

    @property
    def combiner(self) -> RDPQMaterialCombinerProperties:
        return self.combiner_

    @property
    def blender(self) -> RDPQMaterialBlenderProperties:
        return self.blender_

    @property
    def override_render_mode(self) -> RDPQMaterialOverrideRenderModeProperties:
        return self.override_render_mode_


def is_fast64_available():
    return hasattr(bpy.context.scene, "f3d_type")


def is_fast64_material(mat: bpy.types.Material):
    return getattr(mat, "is_f3d", False)


BLENDER_MUXES_FAST64_MAP = {
    "INPUT": "G_BL_CLR_IN",
    "MEMORY": "G_BL_CLR_MEM",
    "BLEND_COLOR": "G_BL_CLR_BL",
    "FOG_COLOR": "G_BL_CLR_FOG",
    "INPUT_ALPHA": "G_BL_A_IN",
    "FOG_ALPHA": "G_BL_A_FOG",
    "SHADE_ALPHA": "G_BL_A_SHADE",
    "1_MINUS_A": "G_BL_1MA",
    "MEMORY_COVERAGE": "G_BL_A_MEM",
    "1": "G_BL_1",
    "0": "G_BL_0",
}


def rdpq_material_props_to_fast64_props(mat: bpy.types.Material):
    mat_rdpq: RDPQMaterialProperties = mat.libdragon_rdpq
    mat_fast64 = mat.f3d_mat

    # Texture

    # TODO
    mat_rdpq.texture

    # TODO handle one-cycle
    mat_fast64.rdp_settings.g_mdsft_cycletype = "G_CYC_2CYCLE"

    # For controlling the render mode (blender and other properties)
    mat_fast64.rdp_settings.set_rendermode = True
    mat_fast64.rdp_settings.rendermode_advanced_enabled = True

    # Combiner

    mat_fast64.combiner1.A = mat_rdpq.combiner.rgb_A_0
    mat_fast64.combiner1.B = mat_rdpq.combiner.rgb_B_0
    mat_fast64.combiner1.C = mat_rdpq.combiner.rgb_C_0
    mat_fast64.combiner1.D = mat_rdpq.combiner.rgb_D_0

    mat_fast64.combiner1.A_alpha = mat_rdpq.combiner.alpha_A_0
    mat_fast64.combiner1.B_alpha = mat_rdpq.combiner.alpha_B_0
    mat_fast64.combiner1.C_alpha = mat_rdpq.combiner.alpha_C_0
    mat_fast64.combiner1.D_alpha = mat_rdpq.combiner.alpha_D_0

    mat_fast64.combiner2.A = mat_rdpq.combiner.rgb_A_1
    mat_fast64.combiner2.B = mat_rdpq.combiner.rgb_B_1
    mat_fast64.combiner2.C = mat_rdpq.combiner.rgb_C_1
    mat_fast64.combiner2.D = mat_rdpq.combiner.rgb_D_1

    mat_fast64.combiner2.A_alpha = mat_rdpq.combiner.alpha_A_1
    mat_fast64.combiner2.B_alpha = mat_rdpq.combiner.alpha_B_1
    mat_fast64.combiner2.C_alpha = mat_rdpq.combiner.alpha_C_1
    mat_fast64.combiner2.D_alpha = mat_rdpq.combiner.alpha_D_1

    # Blender

    mat_fast64.rdp_settings.blend_p1 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.p_0]
    mat_fast64.rdp_settings.blend_a1 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.a_0]
    mat_fast64.rdp_settings.blend_m1 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.m_0]
    mat_fast64.rdp_settings.blend_b1 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.b_0]

    mat_fast64.rdp_settings.blend_p2 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.p_1]
    mat_fast64.rdp_settings.blend_a2 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.a_1]
    mat_fast64.rdp_settings.blend_m2 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.m_1]
    mat_fast64.rdp_settings.blend_b2 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.b_1]

    mat_fast64.set_blend = True
    mat_fast64.blend_color = mat_rdpq.blender.blend_color
    mat_fast64.set_fog = True
    mat_fast64.fog_color = mat_rdpq.blender.fog_color

    # Overrides

    # TODO all "override" props should check for the override_* bool props
    # and default to a world default if not overriden

    mat_rdpq.override_render_mode.antialias  # TODO
    mat_rdpq.override_render_mode.fog  # TODO
    mat_rdpq.override_render_mode.dithering  # TODO
    mat_fast64.rdp_settings.g_mdsft_text_filt = {
        "POINT": "G_TF_POINT",
        "BILINEAR": "G_TF_BILERP",
        "MEDIAN": "G_TF_AVERAGE",
    }[mat_rdpq.override_render_mode.texture_filtering]
    mat_fast64.rdp_settings.g_mdsft_textpersp = (
        "G_TP_PERSP"
        if mat_rdpq.override_render_mode.texture_perspective_correction
        else "G_TP_NONE"
    )
    mat_rdpq.override_render_mode.alpha_compare_threshold  # TODO
    mat_fast64.rdp_settings.z_cmp = mat_rdpq.override_render_mode.z_compare
    mat_fast64.rdp_settings.z_upd = mat_rdpq.override_render_mode.z_update
    if mat_rdpq.override_render_mode.override_fixed_z:
        mat_fast64.rdp_settings.g_mdsft_zsrcsel = "G_ZS_PRIM"
        mat_fast64.rdp_settings.prim_depth.z = mat_rdpq.override_render_mode.fixed_z
        mat_fast64.rdp_settings.prim_depth.dz = (
            mat_rdpq.override_render_mode.fixed_z_deltaz
        )
    else:
        mat_fast64.rdp_settings.g_mdsft_zsrcsel = "G_ZS_PIXEL"


class RDPQMaterialPropsToFast64Operator(bpy.types.Operator):
    bl_idname = "libdragon_rdpq.rdpq_material_props_to_fast64"
    bl_label = "RDPQ properties to Fast64"

    @classmethod
    def poll(cls, context):
        return (
            hasattr(context, "material")
            and context.material is not None
            and is_fast64_material(context.material)
        )

    def execute(self, context):
        mat = context.material
        assert mat is not None
        rdpq_material_props_to_fast64_props(mat)
        return {"FINISHED"}


@dataclasses.dataclass
class RecursivePropsList:
    props: tuple[str, ...]
    groups: dict[str, "RecursivePropsList"]


LIBDRAGON_RDPQ_PROPS_LIST = RecursivePropsList(
    (),
    {
        "libdragon_rdpq": RecursivePropsList(
            (),
            {
                "texture": RecursivePropsList(
                    (
                        "use_texture",
                        "use_placeholder",
                        "placeholder",
                        "format",
                        "mipmap",
                        "dithering",
                    ),
                    {
                        "s": RecursivePropsList(
                            (
                                "translate",
                                "scale",
                                "repeats_inf",
                                "repeats",
                                "mirror",
                            ),
                            {},
                        ),
                        "t": RecursivePropsList(
                            (
                                "translate",
                                "scale",
                                "repeats_inf",
                                "repeats",
                                "mirror",
                            ),
                            {},
                        ),
                    },
                ),
                "combiner": RecursivePropsList(
                    (
                        "preset",
                        "rgb_A_0",
                        "rgb_B_0",
                        "rgb_C_0",
                        "rgb_D_0",
                        "alpha_A_0",
                        "alpha_B_0",
                        "alpha_C_0",
                        "alpha_D_0",
                        "rgb_A_1",
                        "rgb_B_1",
                        "rgb_C_1",
                        "rgb_D_1",
                        "alpha_A_1",
                        "alpha_B_1",
                        "alpha_C_1",
                        "alpha_D_1",
                    ),
                    {},
                ),
                "blender": RecursivePropsList(
                    (
                        "preset",
                        "p_0",
                        "a_0",
                        "m_0",
                        "b_0",
                        "p_1",
                        "a_1",
                        "m_1",
                        "b_1",
                        "blend_color",
                        "fog_color",
                    ),
                    {},
                ),
                "override_render_mode": RecursivePropsList(
                    (
                        "override_antialias",
                        "antialias",
                        "override_fog",
                        "fog",
                        "override_dithering",
                        "dithering",
                        "override_texture_filtering",
                        "texture_filtering",
                        "override_texture_perspective_correction",
                        "texture_perspective_correction",
                        "override_alpha_compare",
                        "alpha_compare_threshold",
                        "override_z_compare",
                        "z_compare",
                        "override_z_update",
                        "z_update",
                        "override_fixed_z",
                        "fixed_z",
                        "fixed_z_deltaz",
                    ),
                    {},
                ),
            },
        ),
    },
)


def copy_props(f, t, props_list: RecursivePropsList):
    for prop_name in props_list.props:
        setattr(t, prop_name, getattr(f, prop_name))
    for group_name, group_props_list in props_list.groups.items():
        copy_props(getattr(f, group_name), getattr(t, group_name), group_props_list)


def rdpq_material_copy_props(
    from_mat: bpy.types.Material,
    to_mat: bpy.types.Material,
):
    copy_props(from_mat, to_mat, LIBDRAGON_RDPQ_PROPS_LIST)


def rdpq_material_recreate_as_fast64(mat: bpy.types.Material):
    # Create a fast64 material and find it
    keys_before = set(bpy.data.materials.keys())
    bpy.ops.object.create_f3d_mat()
    keys_after = set(bpy.data.materials.keys())
    assert keys_after.issuperset(keys_before)
    keys_added = keys_after - keys_before
    assert len(keys_added) == 1
    (key_added,) = keys_added
    new_mat = bpy.data.materials[key_added]

    # Transfer properties from mat to new_mat and to fast64 properties
    rdpq_material_copy_props(mat, new_mat)
    rdpq_material_props_to_fast64_props(new_mat)

    # Replace mat with new_mat in all slots where mat is used
    for obj in bpy.data.objects:
        for i in range(len(obj.material_slots)):
            if obj.material_slots[i].material == mat:
                obj.material_slots[i].material = new_mat

    mat_name = mat.name
    mat.name = mat.name + " old"
    new_mat.name = mat_name

    # Delete the new material slot fast64 created for new_mat
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.material_slot_remove()


class RDPQMaterialRecreateAsFast64Operator(bpy.types.Operator):
    bl_idname = "libdragon_rdpq.rdpq_material_recreate_as_fast64"
    bl_label = "Recreate RDPQ material as Fast64 material"

    @classmethod
    def poll(cls, context):
        return hasattr(context, "material") and context.material is not None

    def execute(self, context):
        mat = context.material
        assert mat is not None
        rdpq_material_recreate_as_fast64(mat)
        return {"FINISHED"}


def prop_split(layout: bpy.types.UILayout, data, prop_name: str):
    layout.use_property_split = True
    layout.use_property_decorate = False
    layout.prop(data, prop_name)
    layout.use_property_split = False


class RDPQMaterialPanel(bpy.types.Panel):
    bl_idname = "MATERIAL_PT_libdragon_rdpq"
    bl_label = "RDPQ"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return context.material is not None

    def draw(self, context):
        layout = self.layout
        assert layout is not None
        mat = context.material
        assert mat is not None
        mat_rdpq: RDPQMaterialProperties = mat.libdragon_rdpq

        if is_fast64_available():
            if is_fast64_material(mat):
                layout.operator(
                    RDPQMaterialPropsToFast64Operator.bl_idname,
                    text="Sync to Fast64 props",
                )
            else:
                layout.operator(
                    RDPQMaterialRecreateAsFast64Operator.bl_idname,
                    text="Recreate as Fast64 material",
                )

        box = layout.box()
        box.prop(mat_rdpq.texture, "use_texture")
        if mat_rdpq.texture.use_texture:
            row = box.row()
            row.prop(mat_rdpq.texture, "use_placeholder", text="")
            col = row.column()
            col.prop(mat_rdpq.texture, "placeholder")
            col.enabled = mat_rdpq.texture.use_placeholder
            prop_split(box, mat_rdpq.texture, "format")
            prop_split(box, mat_rdpq.texture, "mipmap")
            prop_split(box, mat_rdpq.texture, "dithering")

            box_s = box.box()
            box_s.label(text="S Properties")
            box_s.prop(mat_rdpq.texture.s, "translate")
            box_s.prop(mat_rdpq.texture.s, "scale")

            row = box_s.row()
            row.label(text="Repeats")
            col = row.column()
            col.prop(mat_rdpq.texture.s, "repeats", text="")
            col.enabled = not mat_rdpq.texture.s.repeats_inf
            row.prop(mat_rdpq.texture.s, "repeats_inf", text="Infinite")

            box_s.prop(mat_rdpq.texture.s, "mirror")

            box_t = box.box()
            box_t.label(text="T Properties")
            box_t.prop(mat_rdpq.texture.t, "translate")
            box_t.prop(mat_rdpq.texture.t, "scale")

            row = box_t.row()
            row.label(text="Repeats")
            col = row.column()
            col.prop(mat_rdpq.texture.t, "repeats", text="")
            col.enabled = not mat_rdpq.texture.t.repeats_inf
            row.prop(mat_rdpq.texture.t, "repeats_inf", text="Infinite")

            box_t.prop(mat_rdpq.texture.t, "mirror")

        box = layout.box()
        prop_split(box, mat_rdpq.combiner, "preset")
        if mat_rdpq.combiner.preset in {"CUSTOM_1_PASS", "CUSTOM_2_PASSES"}:
            box.prop(mat_rdpq.combiner, "rgb_A_0")
            box.prop(mat_rdpq.combiner, "rgb_B_0")
            box.prop(mat_rdpq.combiner, "rgb_C_0")
            box.prop(mat_rdpq.combiner, "rgb_D_0")
            box.prop(mat_rdpq.combiner, "alpha_A_0")
            box.prop(mat_rdpq.combiner, "alpha_B_0")
            box.prop(mat_rdpq.combiner, "alpha_C_0")
            box.prop(mat_rdpq.combiner, "alpha_D_0")
        if mat_rdpq.combiner.preset == "CUSTOM_2_PASSES":
            box.prop(mat_rdpq.combiner, "rgb_A_1")
            box.prop(mat_rdpq.combiner, "rgb_B_1")
            box.prop(mat_rdpq.combiner, "rgb_C_1")
            box.prop(mat_rdpq.combiner, "rgb_D_1")
            box.prop(mat_rdpq.combiner, "alpha_A_1")
            box.prop(mat_rdpq.combiner, "alpha_B_1")
            box.prop(mat_rdpq.combiner, "alpha_C_1")
            box.prop(mat_rdpq.combiner, "alpha_D_1")

        box = layout.box()
        prop_split(box, mat_rdpq.blender, "preset")
        if mat_rdpq.blender.preset in {"CUSTOM_1_PASS", "CUSTOM_2_PASSES"}:
            box.prop(mat_rdpq.blender, "p_0")
            box.prop(mat_rdpq.blender, "a_0")
            box.prop(mat_rdpq.blender, "m_0")
            box.prop(mat_rdpq.blender, "b_0")
        if mat_rdpq.blender.preset == "CUSTOM_2_PASSES":
            box.prop(mat_rdpq.blender, "p_1")
            box.prop(mat_rdpq.blender, "a_1")
            box.prop(mat_rdpq.blender, "m_1")
            box.prop(mat_rdpq.blender, "b_1")
        prop_split(box, mat_rdpq.blender, "blend_color")
        prop_split(box, mat_rdpq.blender, "fog_color")

        box = layout.box()

        def prop_override(override_prop_name: str, *props_names: str):
            row = box.row()
            row.prop(mat_rdpq.override_render_mode, override_prop_name, text="")
            col = row.column()
            for prop_name in props_names:
                col.prop(mat_rdpq.override_render_mode, prop_name)
            col.enabled = getattr(mat_rdpq.override_render_mode, override_prop_name)

        prop_override("override_antialias", "antialias")
        prop_override("override_fog", "fog")
        prop_override("override_dithering", "dithering")
        prop_override("override_texture_filtering", "texture_filtering")
        prop_override(
            "override_texture_perspective_correction", "texture_perspective_correction"
        )
        prop_override("override_alpha_compare", "alpha_compare_threshold")
        prop_override("override_z_compare", "z_compare")
        prop_override("override_z_update", "z_update")
        prop_override("override_fixed_z", "fixed_z", "fixed_z_deltaz")


classes = (
    RDPQMaterialTextureAxisProperties,
    RDPQMaterialTextureProperties,
    RDPQMaterialCombinerProperties,
    RDPQMaterialBlenderProperties,
    RDPQMaterialOverrideRenderModeProperties,
    RDPQMaterialProperties,
    RDPQMaterialPropsToFast64Operator,
    RDPQMaterialRecreateAsFast64Operator,
    RDPQMaterialPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Material.libdragon_rdpq = bpy.props.PointerProperty(
        type=RDPQMaterialProperties
    )


def unregister():
    del bpy.types.Material.libdragon_rdpq
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
