bl_info = {
    "name": "libdragon RDPQ materials",
    "version": (0, 0, 1),
    "author": "Dragorn421",
    "location": "Material Properties",
    "description": "RDPQ materials for the libdragon N64 homebrew SDK",
    "category": "Material",
    "blender": (3, 2, 0),
}

import bpy
import bpy.utils


class RDPQMaterialTextureAxisProperties(bpy.types.PropertyGroup):
    translate: bpy.props.FloatProperty()
    scale: bpy.props.IntProperty()
    repeats_inf: bpy.props.BoolProperty()
    repeats: bpy.props.FloatProperty()
    mirror: bpy.props.BoolProperty()


class RDPQMaterialTextureProperties(bpy.types.PropertyGroup):
    use_texture: bpy.props.BoolProperty()
    use_placeholder: bpy.props.BoolProperty()
    placeholder: bpy.props.IntProperty()
    format: bpy.props.EnumProperty(
        items=(
            ("AUTO", "Auto", ""),
            ("I4", "I4", ""),
            ("I8", "I8", ""),
            # TODO fill in
            ("SHQ", "SHQ", ""),
            ("IHQ", "IHQ", ""),
        )
    )
    mipmap: bpy.props.EnumProperty(
        items=(
            ("NONE", "None", ""),
            ("BOX", "Box", ""),
        )
    )
    dithering: bpy.props.EnumProperty(
        items=(
            ("NONE", "None", ""),
            ("RANDOM", "Random", ""),
            ("ORDERED", "Ordered", ""),
        )
    )
    s: bpy.props.PointerProperty(type=RDPQMaterialTextureAxisProperties)
    t: bpy.props.PointerProperty(type=RDPQMaterialTextureAxisProperties)


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


class RDPQMaterialCombinerProperties(bpy.types.PropertyGroup):
    preset: bpy.props.EnumProperty(
        items=(
            ("FLAT", "Flat", ""),
            ("SHADE", "Shade", ""),
            ("TEX", "Tex", ""),
            ("TEX_FLAT", "Tex Flat", ""),
            ("TEX_SHADE", "Tex Shade", ""),
            ("CUSTOM_1_PASS", "Custom 1 Pass", ""),
            ("CUSTOM_2_PASSES", "Custom 2 Passes", ""),
        )
    )

    rgb_A_0: bpy.props.EnumProperty(
        name="RGB A 1",
        description="RGB A Input (First Cycle)",
        items=rgb_A_inputs_items,
    )
    rgb_B_0: bpy.props.EnumProperty(
        name="RGB B 1",
        description="RGB B Input (First Cycle)",
        items=rgb_B_inputs_items,
    )
    rgb_C_0: bpy.props.EnumProperty(
        name="RGB C 1",
        description="RGB C Input (First Cycle)",
        items=rgb_C_inputs_items,
    )
    rgb_D_0: bpy.props.EnumProperty(
        name="RGB D 1",
        description="RGB D Input (First Cycle)",
        items=rgb_D_inputs_items,
    )

    alpha_A_0: bpy.props.EnumProperty(
        name="Alpha A 1",
        description="RGB A Input (First Cycle)",
        items=alpha_A_inputs_items,
    )
    alpha_B_0: bpy.props.EnumProperty(
        name="Alpha B 1",
        description="RGB B Input (First Cycle)",
        items=alpha_B_inputs_items,
    )
    alpha_C_0: bpy.props.EnumProperty(
        name="Alpha C 1",
        description="RGB C Input (First Cycle)",
        items=alpha_C_inputs_items,
    )
    alpha_D_0: bpy.props.EnumProperty(
        name="Alpha D 1",
        description="RGB D Input (First Cycle)",
        items=alpha_D_inputs_items,
    )

    rgb_A_1: bpy.props.EnumProperty(
        name="RGB A 2",
        description="RGB A Input (Second Cycle)",
        items=rgb_A_inputs_items,
    )
    rgb_B_1: bpy.props.EnumProperty(
        name="RGB B 2",
        description="RGB B Input (Second Cycle)",
        items=rgb_B_inputs_items,
    )
    rgb_C_1: bpy.props.EnumProperty(
        name="RGB C 2",
        description="RGB C Input (Second Cycle)",
        items=rgb_C_inputs_items,
    )
    rgb_D_1: bpy.props.EnumProperty(
        name="RGB D 2",
        description="RGB D Input (Second Cycle)",
        items=rgb_D_inputs_items,
    )

    alpha_A_1: bpy.props.EnumProperty(
        name="Alpha A 2",
        description="RGB A Input (Second Cycle)",
        items=alpha_A_inputs_items,
    )
    alpha_B_1: bpy.props.EnumProperty(
        name="Alpha B 2",
        description="RGB B Input (Second Cycle)",
        items=alpha_B_inputs_items,
    )
    alpha_C_1: bpy.props.EnumProperty(
        name="Alpha C 2",
        description="RGB C Input (Second Cycle)",
        items=alpha_C_inputs_items,
    )
    alpha_D_1: bpy.props.EnumProperty(
        name="Alpha D 2",
        description="RGB D Input (Second Cycle)",
        items=alpha_D_inputs_items,
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
        items=(
            ("NONE", "None", ""),
            ("MULTIPLY", "Multiply", ""),
            ("MULTIPLY_CONST", "Multiply Const", ""),
            ("ADDITIVE", "Additive", ""),
            ("CUSTOM_1_PASS", "Custom 1 Pass", ""),
            ("CUSTOM_2_PASSES", "Custom 2 Passes", ""),
        )
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
        subtype="COLOR",
        size=4,
    )
    fog_color: bpy.props.FloatVectorProperty(
        subtype="COLOR",
        size=4,
    )


class RDPQMaterialOverrideRenderModeProperties(bpy.types.PropertyGroup):
    override_antialias: bpy.props.BoolProperty()
    antialias: bpy.props.EnumProperty(
        items=(
            ("NONE", "None", ""),
            ("STANDARD", "Standard", ""),
            ("REDUCED", "Reduced", ""),
        )
    )

    override_fog: bpy.props.BoolProperty()
    fog: bpy.props.EnumProperty(
        items=(
            ("NONE", "None", ""),
            ("STANDARD", "Standard", ""),
            ("CUSTOM", "Custom", ""),
        )
    )

    override_dithering: bpy.props.BoolProperty()
    dithering: bpy.props.EnumProperty(
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
        )
    )

    override_texture_filtering: bpy.props.BoolProperty()
    texture_filtering: bpy.props.EnumProperty(
        items=(
            ("POINT", "Point", ""),
            ("BILINEAR", "Bilinear", ""),
            ("MEDIAN", "Median", ""),
        )
    )

    override_texture_perspective_correction: bpy.props.BoolProperty()
    texture_perspective_correction: bpy.props.BoolProperty()

    override_alpha_compare: bpy.props.BoolProperty()
    alpha_compare_threshold: bpy.props.IntProperty()

    override_z_compare: bpy.props.BoolProperty()
    z_compare: bpy.props.BoolProperty()

    override_z_update: bpy.props.BoolProperty()
    z_update: bpy.props.BoolProperty()

    override_fixed_z: bpy.props.BoolProperty()
    fixed_z: bpy.props.IntProperty()
    fixed_z_deltaz: bpy.props.IntProperty()


class RDPQMaterialProperties(bpy.types.PropertyGroup):
    texture: bpy.props.PointerProperty(type=RDPQMaterialTextureProperties)
    combiner: bpy.props.PointerProperty(type=RDPQMaterialCombinerProperties)
    blender: bpy.props.PointerProperty(type=RDPQMaterialBlenderProperties)
    override_render_mode: bpy.props.PointerProperty(
        type=RDPQMaterialOverrideRenderModeProperties
    )


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

        box = layout.box()
        box.prop(mat_rdpq.texture, "use_texture")
        if mat_rdpq.texture.use_texture:
            box.prop(mat_rdpq.texture, "use_placeholder")
            if mat_rdpq.texture.use_placeholder:
                box.prop(mat_rdpq.texture, "placeholder")
            box.prop(mat_rdpq.texture, "format")
            box.prop(mat_rdpq.texture, "mipmap")
            box.prop(mat_rdpq.texture, "dithering")
            box_s = box.box()
            box_s.prop(mat_rdpq.texture.s, "translate")
            box_s.prop(mat_rdpq.texture.s, "scale")
            box_s.prop(mat_rdpq.texture.s, "repeats_inf")
            box_s.prop(mat_rdpq.texture.s, "repeats")
            box_s.prop(mat_rdpq.texture.s, "mirror")
            box_t = box.box()
            box_t.prop(mat_rdpq.texture.t, "translate")
            box_t.prop(mat_rdpq.texture.t, "scale")
            box_t.prop(mat_rdpq.texture.t, "repeats_inf")
            box_t.prop(mat_rdpq.texture.t, "repeats")
            box_t.prop(mat_rdpq.texture.t, "mirror")

        box = layout.box()
        box.prop(mat_rdpq.combiner, "preset")
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
        box.prop(mat_rdpq.blender, "preset")
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
        box.prop(mat_rdpq.blender, "blend_color")
        box.prop(mat_rdpq.blender, "fog_color")

        box = layout.box()
        box.prop(mat_rdpq.override_render_mode, "override_antialias")
        if mat_rdpq.override_render_mode.override_antialias:
            box.prop(mat_rdpq.override_render_mode, "antialias")
        box.prop(mat_rdpq.override_render_mode, "override_texture_filtering")
        if mat_rdpq.override_render_mode.override_texture_filtering:
            box.prop(mat_rdpq.override_render_mode, "texture_filtering")
        box.prop(
            mat_rdpq.override_render_mode, "override_texture_perspective_correction"
        )
        if mat_rdpq.override_render_mode.override_texture_perspective_correction:
            box.prop(mat_rdpq.override_render_mode, "texture_perspective_correction")
        box.prop(mat_rdpq.override_render_mode, "override_alpha_compare")
        if mat_rdpq.override_render_mode.override_alpha_compare:
            box.prop(mat_rdpq.override_render_mode, "alpha_compare_threshold")
        box.prop(mat_rdpq.override_render_mode, "override_z_compare")
        if mat_rdpq.override_render_mode.override_z_compare:
            box.prop(mat_rdpq.override_render_mode, "z_compare")
        box.prop(mat_rdpq.override_render_mode, "override_z_update")
        if mat_rdpq.override_render_mode.override_z_update:
            box.prop(mat_rdpq.override_render_mode, "z_update")
        box.prop(mat_rdpq.override_render_mode, "override_fixed_z")
        if mat_rdpq.override_render_mode.override_fixed_z:
            box.prop(mat_rdpq.override_render_mode, "fixed_z")
            box.prop(mat_rdpq.override_render_mode, "fixed_z_deltaz")


classes = (
    RDPQMaterialTextureAxisProperties,
    RDPQMaterialTextureProperties,
    RDPQMaterialCombinerProperties,
    RDPQMaterialBlenderProperties,
    RDPQMaterialOverrideRenderModeProperties,
    RDPQMaterialProperties,
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
