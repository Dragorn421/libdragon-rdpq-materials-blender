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
import math
from pathlib import Path
from typing import Optional

import bpy
import bpy.utils


class RDPQWorldDefaultsProperties(bpy.types.PropertyGroup):
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
    texture_perspective_correction: bpy.props.BoolProperty(
        name="Texture Perspective Correction",
        description="",
        default=True,
    )

    alpha_compare: bpy.props.BoolProperty(
        name="Alpha Compare",
        description="",
        default=False,
    )
    alpha_compare_threshold: bpy.props.IntProperty(
        name="Alpha Compare Threshold",
        description="",
        default=127,
        min=0,
        max=255,
    )

    z_compare: bpy.props.BoolProperty(
        name="Z Compare",
        description="",
        default=True,
    )
    z_update: bpy.props.BoolProperty(
        name="Z Update",
        description="",
        default=True,
    )

    fixed_z: bpy.props.BoolProperty(
        name="Fixed Z",
        description="",
    )
    fixed_z_value: bpy.props.IntProperty(
        name="Fixed Z",
        description="",
        min=0,
        max=0x7FFF,
    )
    fixed_z_deltaz: bpy.props.IntProperty(
        name="Fixed Z deltaz",
        description="",
        min=-32768,
        max=32767,
    )


class RDPQWorldProperties(bpy.types.PropertyGroup):
    defaults_: bpy.props.PointerProperty(type=RDPQWorldDefaultsProperties)

    @property
    def defaults(self) -> RDPQWorldDefaultsProperties:
        return self.defaults_


class RDPQMaterialTextureAxisProperties(bpy.types.PropertyGroup):
    translate: bpy.props.FloatProperty(
        name="Translate",
        description="",
        default=0,
        min=-1024,
        max=1024,
    )
    scale: bpy.props.IntProperty(
        name="Scale",
        description="",
        default=0,
        min=-5,
        max=10,
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
        min=0,
        max=1024,
    )
    mirror: bpy.props.BoolProperty(
        name="Mirror",
        description="",
        default=False,
    )


class RDPQMaterialTextureProperties(bpy.types.PropertyGroup):
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
    image: bpy.props.PointerProperty(
        type=bpy.types.Image,
        name="Image",
        description="",
    )
    format: bpy.props.EnumProperty(
        name="Format",
        description="",
        items=(
            ("AUTO", "Auto", ""),
            ("RGBA16", "RGBA16", ""),
            ("RGBA32", "RGBA32", ""),
            ("CI4", "CI4", ""),
            ("CI8", "CI8", ""),
            ("IA4", "IA4", ""),
            ("IA8", "IA8", ""),
            ("IA16", "IA16", ""),
            ("I4", "I4", ""),
            ("I8", "I8", ""),
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


# One-cycle combiner slots

COMB1_RGB_SUBA_ITEMS = (
    ("TEX0", "TEX0", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("1", "1", ""),
    ("NOISE", "NOISE", ""),
    ("0", "0", ""),
)
COMB1_RGB_SUBB_ITEMS = (
    ("TEX0", "TEX0", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("KEYCENTER", "KEYCENTER", ""),
    ("K4", "K4", ""),
    ("0", "0", ""),
)
COMB1_RGB_MUL_ITEMS = (
    ("TEX0", "TEX0", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("KEYSCALE", "KEYSCALE", ""),
    ("TEX0_ALPHA", "TEX0_ALPHA", ""),
    ("PRIM_ALPHA", "PRIM_ALPHA", ""),
    ("SHADE_ALPHA", "SHADE_ALPHA", ""),
    ("ENV_ALPHA", "ENV_ALPHA", ""),
    ("LOD_FRAC", "LOD_FRAC", ""),
    ("PRIM_LOD_FRAC", "PRIM_LOD_FRAC", ""),
    ("K5", "K5", ""),
    ("0", "0", ""),
)
COMB1_RGB_ADD_ITEMS = (
    ("TEX0", "TEX0", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("1", "1", ""),
    ("0", "0", ""),
)

COMB1_ALPHA_ADDSUB_ITEMS = (
    ("TEX0", "TEX0", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("1", "1", ""),
    ("0", "0", ""),
)
COMB1_ALPHA_MUL_ITEMS = (
    ("LOD_FRAC", "LOD_FRAC", ""),
    ("TEX0", "TEX0", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("PRIM_LOD_FRAC", "PRIM_LOD_FRAC", ""),
    ("0", "0", ""),
)

# Two-cycle combiner slots

COMB2A_RGB_SUBA_ITEMS = (
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("1", "1", ""),
    ("NOISE", "NOISE", ""),
    ("0", "0", ""),
)
COMB2A_RGB_SUBB_ITEMS = (
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("KEYCENTER", "KEYCENTER", ""),
    ("K4", "K4", ""),
    ("0", "0", ""),
)
COMB2A_RGB_MUL_ITEMS = (
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("KEYSCALE", "KEYSCALE", ""),
    ("TEX0_ALPHA", "TEX0_ALPHA", ""),
    ("TEX1_ALPHA", "TEX1_ALPHA", ""),
    ("PRIM_ALPHA", "PRIM_ALPHA", ""),
    ("SHADE_ALPHA", "SHADE_ALPHA", ""),
    ("ENV_ALPHA", "ENV_ALPHA", ""),
    ("LOD_FRAC", "LOD_FRAC", ""),
    ("PRIM_LOD_FRAC", "PRIM_LOD_FRAC", ""),
    ("K5", "K5", ""),
    ("0", "0", ""),
)
COMB2A_RGB_ADD_ITEMS = (
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("1", "1", ""),
    ("0", "0", ""),
)

COMB2A_ALPHA_ADDSUB_ITEMS = (
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("1", "1", ""),
    ("0", "0", ""),
)
COMB2A_ALPHA_MUL_ITEMS = (
    ("LOD_FRAC", "LOD_FRAC", ""),
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("PRIM_LOD_FRAC", "PRIM_LOD_FRAC", ""),
    ("0", "0", ""),
)

COMB2B_RGB_SUBA_ITEMS = (
    ("COMBINED", "COMBINED", ""),
    ("TEX1", "TEX1", ""),
    ("TEX0_BUG", "TEX0_BUG", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("1", "1", ""),
    ("NOISE", "NOISE", ""),
    ("0", "0", ""),
)
COMB2B_RGB_SUBB_ITEMS = (
    ("COMBINED", "COMBINED", ""),
    ("TEX1", "TEX1", ""),
    ("TEX0_BUG", "TEX0_BUG", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("KEYCENTER", "KEYCENTER", ""),
    ("K4", "K4", ""),
    ("0", "0", ""),
)
COMB2B_RGB_MUL_ITEMS = (
    ("COMBINED", "COMBINED", ""),
    ("TEX1", "TEX1", ""),
    ("TEX0_BUG", "TEX0_BUG", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("KEYSCALE", "KEYSCALE", ""),
    ("COMBINED_ALPHA", "COMBINED_ALPHA", ""),
    ("TEX1_ALPHA", "TEX1_ALPHA", ""),
    ("TEX0_ALPHA", "TEX0_ALPHA", ""),
    ("PRIM_ALPHA", "PRIM_ALPHA", ""),
    ("SHADE_ALPHA", "SHADE_ALPHA", ""),
    ("ENV_ALPHA", "ENV_ALPHA", ""),
    ("LOD_FRAC", "LOD_FRAC", ""),
    ("PRIM_LOD_FRAC", "PRIM_LOD_FRAC", ""),
    ("K5", "K5", ""),
    ("0", "0", ""),
)
COMB2B_RGB_ADD_ITEMS = (
    ("COMBINED", "COMBINED", ""),
    ("TEX1", "TEX1", ""),
    ("TEX0_BUG", "TEX0_BUG", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("1", "1", ""),
    ("0", "0", ""),
)

COMB2B_ALPHA_ADDSUB_ITEMS = (
    ("COMBINED", "COMBINED", ""),
    ("TEX1", "TEX1", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("1", "1", ""),
    ("0", "0", ""),
)
COMB2B_ALPHA_MUL_ITEMS = (
    ("LOD_FRAC", "LOD_FRAC", ""),
    ("TEX1", "TEX1", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("PRIM_LOD_FRAC", "PRIM_LOD_FRAC", ""),
    ("0", "0", ""),
)


def on_update_combiner_preset(self, context: bpy.types.Context):
    mat = context.material
    assert mat is not None
    mat_rdpq: RDPQMaterialProperties = mat.libdragon_rdpq
    if mat_rdpq.combiner.preset == "FLAT":
        mat_rdpq.combiner.rgb_A = "0"
        mat_rdpq.combiner.rgb_B = "0"
        mat_rdpq.combiner.rgb_C = "0"
        mat_rdpq.combiner.rgb_D = "PRIM"
        mat_rdpq.combiner.alpha_A = "0"
        mat_rdpq.combiner.alpha_B = "0"
        mat_rdpq.combiner.alpha_C = "0"
        mat_rdpq.combiner.alpha_D = "PRIM"

        mat_rdpq.combiner.rgb_A_0 = "0"
        mat_rdpq.combiner.rgb_B_0 = "0"
        mat_rdpq.combiner.rgb_C_0 = "0"
        mat_rdpq.combiner.rgb_D_0 = "PRIM"
        mat_rdpq.combiner.alpha_A_0 = "0"
        mat_rdpq.combiner.alpha_B_0 = "0"
        mat_rdpq.combiner.alpha_C_0 = "0"
        mat_rdpq.combiner.alpha_D_0 = "PRIM"

        mat_rdpq.combiner.rgb_A_1 = "0"
        mat_rdpq.combiner.rgb_B_1 = "0"
        mat_rdpq.combiner.rgb_C_1 = "0"
        mat_rdpq.combiner.rgb_D_1 = "PRIM"
        mat_rdpq.combiner.alpha_A_1 = "0"
        mat_rdpq.combiner.alpha_B_1 = "0"
        mat_rdpq.combiner.alpha_C_1 = "0"
        mat_rdpq.combiner.alpha_D_1 = "PRIM"
    elif mat_rdpq.combiner.preset == "SHADE":
        # TODO handle fog
        mat_rdpq.combiner.rgb_A = "0"
        mat_rdpq.combiner.rgb_B = "0"
        mat_rdpq.combiner.rgb_C = "0"
        mat_rdpq.combiner.rgb_D = "SHADE"
        mat_rdpq.combiner.alpha_A = "0"
        mat_rdpq.combiner.alpha_B = "0"
        mat_rdpq.combiner.alpha_C = "0"
        mat_rdpq.combiner.alpha_D = "SHADE"

        mat_rdpq.combiner.rgb_A_0 = "0"
        mat_rdpq.combiner.rgb_B_0 = "0"
        mat_rdpq.combiner.rgb_C_0 = "0"
        mat_rdpq.combiner.rgb_D_0 = "SHADE"
        mat_rdpq.combiner.alpha_A_0 = "0"
        mat_rdpq.combiner.alpha_B_0 = "0"
        mat_rdpq.combiner.alpha_C_0 = "0"
        mat_rdpq.combiner.alpha_D_0 = "SHADE"

        mat_rdpq.combiner.rgb_A_1 = "0"
        mat_rdpq.combiner.rgb_B_1 = "0"
        mat_rdpq.combiner.rgb_C_1 = "0"
        mat_rdpq.combiner.rgb_D_1 = "SHADE"
        mat_rdpq.combiner.alpha_A_1 = "0"
        mat_rdpq.combiner.alpha_B_1 = "0"
        mat_rdpq.combiner.alpha_C_1 = "0"
        mat_rdpq.combiner.alpha_D_1 = "SHADE"
    elif mat_rdpq.combiner.preset == "TEX":
        # TODO handle mipmapping / custom image formats
        mat_rdpq.combiner.rgb_A = "0"
        mat_rdpq.combiner.rgb_B = "0"
        mat_rdpq.combiner.rgb_C = "0"
        mat_rdpq.combiner.rgb_D = "TEX0"
        mat_rdpq.combiner.alpha_A = "0"
        mat_rdpq.combiner.alpha_B = "0"
        mat_rdpq.combiner.alpha_C = "0"
        mat_rdpq.combiner.alpha_D = "TEX0"

        mat_rdpq.combiner.rgb_A_0 = "0"
        mat_rdpq.combiner.rgb_B_0 = "0"
        mat_rdpq.combiner.rgb_C_0 = "0"
        mat_rdpq.combiner.rgb_D_0 = "TEX0"
        mat_rdpq.combiner.alpha_A_0 = "0"
        mat_rdpq.combiner.alpha_B_0 = "0"
        mat_rdpq.combiner.alpha_C_0 = "0"
        mat_rdpq.combiner.alpha_D_0 = "TEX0"

        mat_rdpq.combiner.rgb_A_1 = "0"
        mat_rdpq.combiner.rgb_B_1 = "0"
        mat_rdpq.combiner.rgb_C_1 = "0"
        mat_rdpq.combiner.rgb_D_1 = "COMBINED"
        mat_rdpq.combiner.alpha_A_1 = "0"
        mat_rdpq.combiner.alpha_B_1 = "0"
        mat_rdpq.combiner.alpha_C_1 = "0"
        mat_rdpq.combiner.alpha_D_1 = "COMBINED"
    elif mat_rdpq.combiner.preset == "TEX_FLAT":
        # TODO handle mipmapping / custom image formats
        mat_rdpq.combiner.rgb_A = "TEX0"
        mat_rdpq.combiner.rgb_B = "0"
        mat_rdpq.combiner.rgb_C = "PRIM"
        mat_rdpq.combiner.rgb_D = "0"
        mat_rdpq.combiner.alpha_A = "TEX0"
        mat_rdpq.combiner.alpha_B = "0"
        mat_rdpq.combiner.alpha_C = "PRIM"
        mat_rdpq.combiner.alpha_D = "0"

        mat_rdpq.combiner.rgb_A_0 = "TEX0"
        mat_rdpq.combiner.rgb_B_0 = "0"
        mat_rdpq.combiner.rgb_C_0 = "PRIM"
        mat_rdpq.combiner.rgb_D_0 = "0"
        mat_rdpq.combiner.alpha_A_0 = "TEX0"
        mat_rdpq.combiner.alpha_B_0 = "0"
        mat_rdpq.combiner.alpha_C_0 = "PRIM"
        mat_rdpq.combiner.alpha_D_0 = "0"

        mat_rdpq.combiner.rgb_A_1 = "0"
        mat_rdpq.combiner.rgb_B_1 = "0"
        mat_rdpq.combiner.rgb_C_1 = "0"
        mat_rdpq.combiner.rgb_D_1 = "COMBINED"
        mat_rdpq.combiner.alpha_A_1 = "0"
        mat_rdpq.combiner.alpha_B_1 = "0"
        mat_rdpq.combiner.alpha_C_1 = "0"
        mat_rdpq.combiner.alpha_D_1 = "COMBINED"
    elif mat_rdpq.combiner.preset == "TEX_SHADE":
        # TODO handle mipmapping / custom image formats and fog
        mat_rdpq.combiner.rgb_A = "TEX0"
        mat_rdpq.combiner.rgb_B = "0"
        mat_rdpq.combiner.rgb_C = "SHADE"
        mat_rdpq.combiner.rgb_D = "0"
        mat_rdpq.combiner.alpha_A = "TEX0"
        mat_rdpq.combiner.alpha_B = "0"
        mat_rdpq.combiner.alpha_C = "SHADE"
        mat_rdpq.combiner.alpha_D = "0"

        mat_rdpq.combiner.rgb_A_0 = "TEX0"
        mat_rdpq.combiner.rgb_B_0 = "0"
        mat_rdpq.combiner.rgb_C_0 = "SHADE"
        mat_rdpq.combiner.rgb_D_0 = "0"
        mat_rdpq.combiner.alpha_A_0 = "TEX0"
        mat_rdpq.combiner.alpha_B_0 = "0"
        mat_rdpq.combiner.alpha_C_0 = "SHADE"
        mat_rdpq.combiner.alpha_D_0 = "0"

        mat_rdpq.combiner.rgb_A_1 = "0"
        mat_rdpq.combiner.rgb_B_1 = "0"
        mat_rdpq.combiner.rgb_C_1 = "0"
        mat_rdpq.combiner.rgb_D_1 = "COMBINED"
        mat_rdpq.combiner.alpha_A_1 = "0"
        mat_rdpq.combiner.alpha_B_1 = "0"
        mat_rdpq.combiner.alpha_C_1 = "0"
        mat_rdpq.combiner.alpha_D_1 = "COMBINED"


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
        update=on_update_combiner_preset,
    )

    # One-cycle

    rgb_A: bpy.props.EnumProperty(
        name="RGB A",
        description="RGB A Input",
        items=COMB1_RGB_SUBA_ITEMS,
    )
    rgb_B: bpy.props.EnumProperty(
        name="RGB B",
        description="RGB B Input",
        items=COMB1_RGB_SUBB_ITEMS,
    )
    rgb_C: bpy.props.EnumProperty(
        name="RGB C",
        description="RGB C Input",
        items=COMB1_RGB_MUL_ITEMS,
    )
    rgb_D: bpy.props.EnumProperty(
        name="RGB D",
        description="RGB D Input",
        items=COMB1_RGB_ADD_ITEMS,
    )

    alpha_A: bpy.props.EnumProperty(
        name="Alpha A",
        description="RGB A Input",
        items=COMB1_ALPHA_ADDSUB_ITEMS,
    )
    alpha_B: bpy.props.EnumProperty(
        name="Alpha B",
        description="RGB B Input",
        items=COMB1_ALPHA_ADDSUB_ITEMS,
    )
    alpha_C: bpy.props.EnumProperty(
        name="Alpha C",
        description="RGB C Input",
        items=COMB1_ALPHA_MUL_ITEMS,
    )
    alpha_D: bpy.props.EnumProperty(
        name="Alpha D",
        description="RGB D Input",
        items=COMB1_ALPHA_ADDSUB_ITEMS,
    )

    # Two-cycle

    # First Cycle

    rgb_A_0: bpy.props.EnumProperty(
        name="RGB A 1",
        description="RGB A Input (First Cycle)",
        items=COMB2A_RGB_SUBA_ITEMS,
    )
    rgb_B_0: bpy.props.EnumProperty(
        name="RGB B 1",
        description="RGB B Input (First Cycle)",
        items=COMB2A_RGB_SUBB_ITEMS,
    )
    rgb_C_0: bpy.props.EnumProperty(
        name="RGB C 1",
        description="RGB C Input (First Cycle)",
        items=COMB2A_RGB_MUL_ITEMS,
    )
    rgb_D_0: bpy.props.EnumProperty(
        name="RGB D 1",
        description="RGB D Input (First Cycle)",
        items=COMB2A_RGB_ADD_ITEMS,
    )

    alpha_A_0: bpy.props.EnumProperty(
        name="Alpha A 1",
        description="Alpha A Input (First Cycle)",
        items=COMB2A_ALPHA_ADDSUB_ITEMS,
    )
    alpha_B_0: bpy.props.EnumProperty(
        name="Alpha B 1",
        description="Alpha B Input (First Cycle)",
        items=COMB2A_ALPHA_ADDSUB_ITEMS,
    )
    alpha_C_0: bpy.props.EnumProperty(
        name="Alpha C 1",
        description="Alpha C Input (First Cycle)",
        items=COMB2A_ALPHA_MUL_ITEMS,
    )
    alpha_D_0: bpy.props.EnumProperty(
        name="Alpha D 1",
        description="Alpha D Input (First Cycle)",
        items=COMB2A_ALPHA_ADDSUB_ITEMS,
    )

    # Second Cycle

    rgb_A_1: bpy.props.EnumProperty(
        name="RGB A 2",
        description="RGB A Input (Second Cycle)",
        items=COMB2B_RGB_SUBA_ITEMS,
    )
    rgb_B_1: bpy.props.EnumProperty(
        name="RGB B 2",
        description="RGB B Input (Second Cycle)",
        items=COMB2B_RGB_SUBB_ITEMS,
    )
    rgb_C_1: bpy.props.EnumProperty(
        name="RGB C 2",
        description="RGB C Input (Second Cycle)",
        items=COMB2B_RGB_MUL_ITEMS,
    )
    rgb_D_1: bpy.props.EnumProperty(
        name="RGB D 2",
        description="RGB D Input (Second Cycle)",
        items=COMB2B_RGB_ADD_ITEMS,
    )

    alpha_A_1: bpy.props.EnumProperty(
        name="Alpha A 2",
        description="Alpha A Input (Second Cycle)",
        items=COMB2B_ALPHA_ADDSUB_ITEMS,
    )
    alpha_B_1: bpy.props.EnumProperty(
        name="Alpha B 2",
        description="Alpha B Input (Second Cycle)",
        items=COMB2B_ALPHA_ADDSUB_ITEMS,
    )
    alpha_C_1: bpy.props.EnumProperty(
        name="Alpha C 2",
        description="Alpha C Input (Second Cycle)",
        items=COMB2B_ALPHA_MUL_ITEMS,
    )
    alpha_D_1: bpy.props.EnumProperty(
        name="Alpha D 2",
        description="Alpha D Input (Second Cycle)",
        items=COMB2B_ALPHA_ADDSUB_ITEMS,
    )


BLEND1_A_ITEMS = (
    ("IN_RGB", "IN_RGB", ""),
    ("MEMORY_RGB", "MEMORY_RGB", ""),
    ("BLEND_RGB", "BLEND_RGB", ""),
    ("FOG_RGB", "FOG_RGB", ""),
)
BLEND1_B1_ITEMS = (
    ("IN_ALPHA", "IN_ALPHA", ""),
    ("FOG_ALPHA", "FOG_ALPHA", ""),
    ("SHADE_ALPHA", "SHADE_ALPHA", ""),
    ("0", "0", ""),
)
BLEND1_B2_ITEMS = (
    ("INV_MUX_ALPHA", "INV_MUX_ALPHA", ""),
    ("MEMORY_CVG", "MEMORY_CVG", ""),
    ("1", "1", ""),
    ("0", "0", ""),
)

BLEND2A_A_ITEMS = (
    ("IN_RGB", "IN_RGB", ""),
    ("BLEND_RGB", "BLEND_RGB", ""),
    ("FOG_RGB", "FOG_RGB", ""),
)
BLEND2A_B1_ITEMS = (
    ("IN_ALPHA", "IN_ALPHA", ""),
    ("FOG_ALPHA", "FOG_ALPHA", ""),
    ("SHADE_ALPHA", "SHADE_ALPHA", ""),
    ("0", "0", ""),
)
BLEND2A_B2_ITEMS = (("INV_MUX_ALPHA", "INV_MUX_ALPHA", ""),)
BLEND2B_A_ITEMS = (
    ("CYCLE1_RGB", "CYCLE1_RGB", ""),
    ("MEMORY_RGB", "MEMORY_RGB", ""),
    ("BLEND_RGB", "BLEND_RGB", ""),
    ("FOG_RGB", "FOG_RGB", ""),
)
BLEND2B_B1_ITEMS = (
    ("IN_ALPHA", "IN_ALPHA", ""),
    ("FOG_ALPHA", "FOG_ALPHA", ""),
    ("SHADE_ALPHA", "SHADE_ALPHA", ""),
    ("0", "0", ""),
)
BLEND2B_B2_ITEMS = (
    ("INV_MUX_ALPHA", "INV_MUX_ALPHA", ""),
    ("MEMORY_CVG", "MEMORY_CVG", ""),
    ("1", "1", ""),
    ("0", "0", ""),
)


def on_update_blender_preset(self, context: bpy.types.Context):
    mat = context.material
    assert mat is not None
    mat_rdpq: RDPQMaterialProperties = mat.libdragon_rdpq
    # TODO handle fog
    if mat_rdpq.blender.preset == "NONE":
        # rdpq_mode_blender suggests passing "0 to disable", which corresponds to
        # RDPQ_BLENDER((IN_RGB, IN_ALPHA, IN_RGB, INV_MUX_ALPHA))

        mat_rdpq.blender.p = "IN_RGB"
        mat_rdpq.blender.a = "IN_ALPHA"
        mat_rdpq.blender.q = "IN_RGB"
        mat_rdpq.blender.b = "INV_MUX_ALPHA"

        mat_rdpq.blender.p_0 = "IN_RGB"
        mat_rdpq.blender.a_0 = "IN_ALPHA"
        mat_rdpq.blender.q_0 = "IN_RGB"
        mat_rdpq.blender.b_0 = "INV_MUX_ALPHA"
        mat_rdpq.blender.p_1 = "CYCLE1_RGB"
        mat_rdpq.blender.a_1 = "IN_ALPHA"
        mat_rdpq.blender.q_1 = "CYCLE1_RGB"
        mat_rdpq.blender.b_1 = "INV_MUX_ALPHA"
    elif mat_rdpq.blender.preset == "MULTIPLY":
        # RDPQ_BLENDER((IN_RGB, IN_ALPHA, MEMORY_RGB, INV_MUX_ALPHA))

        mat_rdpq.blender.p = "IN_RGB"
        mat_rdpq.blender.a = "IN_ALPHA"
        mat_rdpq.blender.q = "MEMORY_RGB"
        mat_rdpq.blender.b = "INV_MUX_ALPHA"

        mat_rdpq.blender.p_0 = "IN_RGB"
        mat_rdpq.blender.a_0 = "IN_ALPHA"
        mat_rdpq.blender.q_0 = "IN_RGB"
        mat_rdpq.blender.b_0 = "INV_MUX_ALPHA"

        mat_rdpq.blender.p_1 = "CYCLE1_RGB"
        mat_rdpq.blender.a_1 = "IN_ALPHA"
        mat_rdpq.blender.q_1 = "MEMORY_RGB"
        mat_rdpq.blender.b_1 = "INV_MUX_ALPHA"
    elif mat_rdpq.blender.preset == "MULTIPLY_CONST":
        # RDPQ_BLENDER((IN_RGB, FOG_ALPHA, MEMORY_RGB, INV_MUX_ALPHA))

        mat_rdpq.blender.p = "IN_RGB"
        mat_rdpq.blender.a = "FOG_ALPHA"
        mat_rdpq.blender.q = "MEMORY_RGB"
        mat_rdpq.blender.b = "INV_MUX_ALPHA"

        mat_rdpq.blender.p_0 = "IN_RGB"
        mat_rdpq.blender.a_0 = "IN_ALPHA"
        mat_rdpq.blender.q_0 = "IN_RGB"
        mat_rdpq.blender.b_0 = "INV_MUX_ALPHA"

        mat_rdpq.blender.p_1 = "CYCLE1_RGB"
        mat_rdpq.blender.a_1 = "FOG_ALPHA"
        mat_rdpq.blender.q_1 = "MEMORY_RGB"
        mat_rdpq.blender.b_1 = "INV_MUX_ALPHA"
    elif mat_rdpq.blender.preset == "ADDITIVE":
        # RDPQ_BLENDER((IN_RGB, IN_ALPHA, MEMORY_RGB, ONE))

        mat_rdpq.blender.p = "IN_RGB"
        mat_rdpq.blender.a = "IN_ALPHA"
        mat_rdpq.blender.q = "MEMORY_RGB"
        mat_rdpq.blender.b = "1"

        mat_rdpq.blender.p_0 = "IN_RGB"
        mat_rdpq.blender.a_0 = "IN_ALPHA"
        mat_rdpq.blender.q_0 = "IN_RGB"
        mat_rdpq.blender.b_0 = "INV_MUX_ALPHA"

        mat_rdpq.blender.p_1 = "CYCLE1_RGB"
        mat_rdpq.blender.a_1 = "IN_ALPHA"
        mat_rdpq.blender.q_1 = "MEMORY_RGB"
        mat_rdpq.blender.b_1 = "1"


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
        update=on_update_blender_preset,
    )

    # One-cycle muxes
    p: bpy.props.EnumProperty(
        name="P",
        description="Blender input P",
        items=BLEND1_A_ITEMS,
    )
    a: bpy.props.EnumProperty(
        name="A",
        description="Blender input A (first cycle)",
        items=BLEND1_B1_ITEMS,
    )
    q: bpy.props.EnumProperty(
        name="Q",
        description="Blender input Q (first cycle)",
        items=BLEND1_A_ITEMS,
    )
    b: bpy.props.EnumProperty(
        name="B",
        description="Blender input B (first cycle)",
        items=BLEND1_B2_ITEMS,
    )

    # Two-cycle muxes
    # First cycle
    p_0: bpy.props.EnumProperty(
        name="P1",
        description="Blender input P (first cycle)",
        items=BLEND2A_A_ITEMS,
    )
    a_0: bpy.props.EnumProperty(
        name="A1",
        description="Blender input A (first cycle)",
        items=BLEND2A_B1_ITEMS,
    )
    q_0: bpy.props.EnumProperty(
        name="Q1",
        description="Blender input Q (first cycle)",
        items=BLEND2A_A_ITEMS,
    )
    b_0: bpy.props.EnumProperty(
        name="B1",
        description="Blender input B (first cycle)",
        items=BLEND2A_B2_ITEMS,
    )
    # Second cycle
    p_1: bpy.props.EnumProperty(
        name="P2",
        description="Blender input P (second cycle)",
        items=BLEND2B_A_ITEMS,
    )
    a_1: bpy.props.EnumProperty(
        name="A2",
        description="Blender input A (second cycle)",
        items=BLEND2B_B1_ITEMS,
    )
    q_1: bpy.props.EnumProperty(
        name="Q2",
        description="Blender input Q (second cycle)",
        items=BLEND2B_A_ITEMS,
    )
    b_1: bpy.props.EnumProperty(
        name="B2",
        description="Blender input B (second cycle)",
        items=BLEND2B_B2_ITEMS,
    )

    blend_color: bpy.props.FloatVectorProperty(
        name="Blend Color",
        description="",
        default=(1, 1, 1),
        min=0,
        max=1,
        subtype="COLOR",
        size=3,
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


SYNCED_MATERIALS: dict[bpy.types.Material, object] = {}


def start_auto_sync_to_fast64(mat: bpy.types.Material):
    mat_rdpq: RDPQMaterialProperties = mat.libdragon_rdpq
    assert mat not in SYNCED_MATERIALS
    owner = object()
    SYNCED_MATERIALS[mat] = owner
    try:
        msgbus_sync_rdpq_material_props_to_fast64_props(owner, mat)
    except:
        mat_rdpq.auto_sync_to_fast64 = False
        raise


def on_update_auto_sync_to_fast64(self, context: bpy.types.Context):
    mat = context.material
    assert mat is not None
    mat_rdpq: RDPQMaterialProperties = mat.libdragon_rdpq

    if mat_rdpq.auto_sync_to_fast64:
        scene = bpy.context.scene
        assert scene is not None
        world = scene.world
        assert world is not None  # Prop is drawn disabled if there is no world
        start_auto_sync_to_fast64(mat)
        rdpq_material_props_to_fast64_props(mat, world)
    else:
        assert mat in SYNCED_MATERIALS
        owner = SYNCED_MATERIALS[mat]
        bpy.msgbus.clear_by_owner(owner)
        del SYNCED_MATERIALS[mat]


@bpy.app.handlers.persistent
def handler_load_post_start_materials_auto_sync_to_fast64():
    for mat in bpy.data.materials.values():
        assert mat is not None
        mat_rdpq: RDPQMaterialProperties = mat.libdragon_rdpq
        if mat_rdpq.auto_sync_to_fast64:
            start_auto_sync_to_fast64(mat)


class RDPQMaterialProperties(bpy.types.PropertyGroup):
    auto_sync_to_fast64: bpy.props.BoolProperty(
        name="Auto Sync To Fast64",
        description=(
            "Automatically set Fast64 material properties"
            " based on the libdragon RDPQ material properties"
        ),
        update=on_update_auto_sync_to_fast64,
    )

    use_texture0: bpy.props.BoolProperty(
        name="Use Texture 0",
        description="",
        default=True,
    )
    use_texture1: bpy.props.BoolProperty(
        name="Use Texture 1",
        description="",
        default=False,
    )
    texture0_: bpy.props.PointerProperty(type=RDPQMaterialTextureProperties)
    texture1_: bpy.props.PointerProperty(type=RDPQMaterialTextureProperties)
    combiner_: bpy.props.PointerProperty(type=RDPQMaterialCombinerProperties)
    blender_: bpy.props.PointerProperty(type=RDPQMaterialBlenderProperties)
    override_render_mode_: bpy.props.PointerProperty(
        type=RDPQMaterialOverrideRenderModeProperties
    )

    @property
    def texture0(self) -> RDPQMaterialTextureProperties:
        return self.texture0_

    @property
    def texture1(self) -> RDPQMaterialTextureProperties:
        return self.texture1_

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
    "IN_RGB": "G_BL_CLR_IN",
    "CYCLE1_RGB": "G_BL_CLR_IN",
    "MEMORY_RGB": "G_BL_CLR_MEM",
    "BLEND_RGB": "G_BL_CLR_BL",
    "FOG_RGB": "G_BL_CLR_FOG",
    "IN_ALPHA": "G_BL_A_IN",
    "FOG_ALPHA": "G_BL_A_FOG",
    "SHADE_ALPHA": "G_BL_A_SHADE",
    "INV_MUX_ALPHA": "G_BL_1MA",
    "MEMORY_CVG": "G_BL_A_MEM",
    "1": "G_BL_1",
    "0": "G_BL_0",
}

COMBINER_0_MUXES_FAST64_MAP = {
    "TEX0": "TEXEL0",
    "TEX1": "TEXEL1",
    "PRIM": "PRIMITIVE",
    "SHADE": "SHADE",
    "ENV": "ENVIRONMENT",
    "1": "1",
    "NOISE": "NOISE",
    "0": "0",
    "CENTER": "CENTER",
    "K4": "K4",
    "SCALE": "SCALE",
    "TEX0_ALPHA": "TEXEL0_ALPHA",
    "TEX1_ALPHA": "TEXEL1_ALPHA",
    "PRIM_ALPHA": "PRIMITIVE_ALPHA",
    "SHADE_ALPHA": "SHADE_ALPHA",
    "ENV_ALPHA": "ENV_ALPHA",
    "LOD_FRACTION": "LOD_FRACTION",
    "PRIM_LOD_FRAC": "PRIM_LOD_FRAC",
    "K5": "K5",
}
COMBINER_1_MUXES_FAST64_MAP = COMBINER_0_MUXES_FAST64_MAP.copy()
del COMBINER_1_MUXES_FAST64_MAP["TEX0"]
del COMBINER_1_MUXES_FAST64_MAP["TEX1"]
COMBINER_1_MUXES_FAST64_MAP.update(
    {
        "COMBINED": "COMBINED",
        "TEX0_BUG": "TEXEL1",
        "TEX1": "TEXEL0",
    }
)


def intlog2(v: int):
    r = round(math.log2(v))
    if 2**r == v:
        return r
    else:
        return None


def rdpq_material_props_to_fast64_props(
    mat: bpy.types.Material, world: Optional[bpy.types.World]
):
    if world is None:
        raise NotImplementedError()  # TODO

    mat_rdpq: RDPQMaterialProperties = mat.libdragon_rdpq
    mat_fast64 = mat.f3d_mat
    world_rdpq: RDPQWorldProperties = world.libdragon_rdpq

    # Texture

    def handle_texture_axis_props(
        texture_axis_props: RDPQMaterialTextureAxisProperties,
        tex_axis_fast64_props,
        image_axis_len: int | None,
    ):
        tex_axis_fast64_props.clamp = not texture_axis_props.repeats_inf
        tex_axis_fast64_props.mirror = texture_axis_props.mirror
        if image_axis_len is None:
            tex_axis_fast64_props.low = 0
            tex_axis_fast64_props.high = 0
            tex_axis_fast64_props.mask = 0
        else:
            # TODO low and high computation may be wrong
            translate = texture_axis_props.translate
            if translate < 0:
                translate %= image_axis_len
            tex_axis_fast64_props.low = translate
            tex_axis_fast64_props.high = (
                translate
                + (
                    image_axis_len
                    * (
                        1
                        if texture_axis_props.repeats_inf
                        else texture_axis_props.repeats
                    )
                )
                - 1
            )
            # TODO what if dimension is not a power of 2?
            image_axis_len_intlog2 = intlog2(image_axis_len)
            tex_axis_fast64_props.mask = (
                0 if image_axis_len_intlog2 is None else image_axis_len_intlog2
            )
        tex_axis_fast64_props.shift = texture_axis_props.scale

    def handle_texture_props(
        texture_props: RDPQMaterialTextureProperties, tex_fast64_props
    ):
        tex_fast64_props.tex_set = not texture_props.use_placeholder
        tex_fast64_props.tex = texture_props.image
        texture_format = texture_props.format
        if texture_format == "AUTO":
            # TODO invoke mksprite to guess a format?
            texture_format = "RGBA16"
        if texture_format == "SHQ":
            # TODO
            texture_format = "RGBA16"
        if texture_format == "IHQ":
            # TODO
            texture_format = "RGBA16"
        tex_fast64_props.tex_format = texture_format
        tex_fast64_props.ci_format = "RGBA16"
        tex_fast64_props.autoprop = False
        handle_texture_axis_props(
            texture_props.s,
            tex_fast64_props.S,
            None if texture_props.image is None else texture_props.image.size[0],
        )
        handle_texture_axis_props(
            texture_props.t,
            tex_fast64_props.T,
            None if texture_props.image is None else texture_props.image.size[1],
        )

    if mat_rdpq.use_texture0:
        handle_texture_props(mat_rdpq.texture0, mat_fast64.tex0)
    if mat_rdpq.use_texture1:
        handle_texture_props(mat_rdpq.texture1, mat_fast64.tex1)

    # TODO handle one-cycle
    mat_fast64.rdp_settings.g_mdsft_cycletype = "G_CYC_2CYCLE"

    # For controlling the render mode (blender and other properties)
    mat_fast64.rdp_settings.set_rendermode = True
    mat_fast64.rdp_settings.rendermode_advanced_enabled = True

    # Combiner

    mat_fast64.combiner1.A = COMBINER_0_MUXES_FAST64_MAP[mat_rdpq.combiner.rgb_A_0]
    mat_fast64.combiner1.B = COMBINER_0_MUXES_FAST64_MAP[mat_rdpq.combiner.rgb_B_0]
    mat_fast64.combiner1.C = COMBINER_0_MUXES_FAST64_MAP[mat_rdpq.combiner.rgb_C_0]
    mat_fast64.combiner1.D = COMBINER_0_MUXES_FAST64_MAP[mat_rdpq.combiner.rgb_D_0]

    mat_fast64.combiner1.A_alpha = COMBINER_0_MUXES_FAST64_MAP[
        mat_rdpq.combiner.alpha_A_0
    ]
    mat_fast64.combiner1.B_alpha = COMBINER_0_MUXES_FAST64_MAP[
        mat_rdpq.combiner.alpha_B_0
    ]
    mat_fast64.combiner1.C_alpha = COMBINER_0_MUXES_FAST64_MAP[
        mat_rdpq.combiner.alpha_C_0
    ]
    mat_fast64.combiner1.D_alpha = COMBINER_0_MUXES_FAST64_MAP[
        mat_rdpq.combiner.alpha_D_0
    ]

    mat_fast64.combiner2.A = COMBINER_1_MUXES_FAST64_MAP[mat_rdpq.combiner.rgb_A_1]
    mat_fast64.combiner2.B = COMBINER_1_MUXES_FAST64_MAP[mat_rdpq.combiner.rgb_B_1]
    mat_fast64.combiner2.C = COMBINER_1_MUXES_FAST64_MAP[mat_rdpq.combiner.rgb_C_1]
    mat_fast64.combiner2.D = COMBINER_1_MUXES_FAST64_MAP[mat_rdpq.combiner.rgb_D_1]

    mat_fast64.combiner2.A_alpha = COMBINER_1_MUXES_FAST64_MAP[
        mat_rdpq.combiner.alpha_A_1
    ]
    mat_fast64.combiner2.B_alpha = COMBINER_1_MUXES_FAST64_MAP[
        mat_rdpq.combiner.alpha_B_1
    ]
    mat_fast64.combiner2.C_alpha = COMBINER_1_MUXES_FAST64_MAP[
        mat_rdpq.combiner.alpha_C_1
    ]
    mat_fast64.combiner2.D_alpha = COMBINER_1_MUXES_FAST64_MAP[
        mat_rdpq.combiner.alpha_D_1
    ]

    # Blender

    # TODO handle one-cycle props

    mat_fast64.rdp_settings.blend_p1 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.p_0]
    mat_fast64.rdp_settings.blend_a1 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.a_0]
    mat_fast64.rdp_settings.blend_m1 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.q_0]
    mat_fast64.rdp_settings.blend_b1 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.b_0]

    mat_fast64.rdp_settings.blend_p2 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.p_1]
    mat_fast64.rdp_settings.blend_a2 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.a_1]
    mat_fast64.rdp_settings.blend_m2 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.q_1]
    mat_fast64.rdp_settings.blend_b2 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.b_1]

    # blend_color is set below
    mat_fast64.set_fog = True
    mat_fast64.fog_color = mat_rdpq.blender.fog_color

    # Overrides

    # TODO
    if mat_rdpq.override_render_mode.override_antialias:
        mat_rdpq.override_render_mode.antialias
    else:
        world_rdpq.defaults.antialias

    # TODO
    if mat_rdpq.override_render_mode.override_fog:
        mat_rdpq.override_render_mode.fog
    else:
        world_rdpq.defaults.fog

    (
        mat_fast64.rdp_settings.g_mdsft_rgb_dither,
        mat_fast64.rdp_settings.g_mdsft_alpha_dither,
    ) = {
        # TODO check these mappings are correct (I guessed)
        "RGB_SQUARE_A_SQUARE": ("G_CD_MAGICSQ", "G_AD_PATTERN"),
        "RGB_SQUARE_A_INVSQUARE": ("G_CD_MAGICSQ", "G_AD_NOTPATTERN"),
        "RGB_SQUARE_A_NOISE": ("G_CD_MAGICSQ", "G_AD_NOISE"),
        "RGB_SQUARE_A_NONE": ("G_CD_MAGICSQ", "G_AD_DISABLE"),
        "RGB_BAYER_A_BAYER": ("G_CD_BAYER", "G_AD_PATTERN"),
        "RGB_BAYER_A_INVBAYER": ("G_CD_BAYER", "G_AD_NOTPATTERN"),
        "RGB_BAYER_A_NOISE": ("G_CD_BAYER", "G_AD_NOISE"),
        "RGB_BAYER_A_NONE": ("G_CD_BAYER", "G_AD_DISABLE"),
        "RGB_NOISE_A_SQUARE": ("G_CD_NOISE", "G_AD_PATTERN"),
        "RGB_NOISE_A_INVSQUARE": ("G_CD_NOISE", "G_AD_NOTPATTERN"),
        "RGB_NOISE_A_NOISE": ("G_CD_NOISE", "G_AD_NOISE"),
        "RGB_NOISE_A_NONE": ("G_CD_NOISE", "G_AD_DISABLE"),
        "RGB_NONE_A_BAYER": ("G_CD_DISABLE", "G_AD_PATTERN"),
        "RGB_NONE_A_INVBAYER": ("G_CD_DISABLE", "G_AD_NOTPATTERN"),
        "RGB_NONE_A_NOISE": ("G_CD_DISABLE", "G_AD_NOISE"),
        "RGB_NONE_A_NONE": ("G_CD_DISABLE", "G_AD_DISABLE"),
    }[
        (
            mat_rdpq.override_render_mode.dithering
            if mat_rdpq.override_render_mode.override_dithering
            else world_rdpq.defaults.dithering
        )
    ]

    mat_fast64.rdp_settings.g_mdsft_text_filt = {
        "POINT": "G_TF_POINT",
        "BILINEAR": "G_TF_BILERP",
        "MEDIAN": "G_TF_AVERAGE",
    }[
        (
            mat_rdpq.override_render_mode.texture_filtering
            if mat_rdpq.override_render_mode.override_texture_filtering
            else world_rdpq.defaults.texture_filtering
        )
    ]

    mat_fast64.rdp_settings.g_mdsft_textpersp = (
        "G_TP_PERSP"
        if (
            mat_rdpq.override_render_mode.texture_perspective_correction
            if mat_rdpq.override_render_mode.override_texture_perspective_correction
            else world_rdpq.defaults.texture_perspective_correction
        )
        else "G_TP_NONE"
    )

    if mat_rdpq.override_render_mode.override_alpha_compare:
        mat_fast64.rdp_settings.g_mdsft_alpha_compare = "G_AC_THRESHOLD"
        alpha_compare_threshold = mat_rdpq.override_render_mode.alpha_compare_threshold
    else:
        if world_rdpq.defaults.alpha_compare:
            mat_fast64.rdp_settings.g_mdsft_alpha_compare = "G_AC_THRESHOLD"
            alpha_compare_threshold = world_rdpq.defaults.alpha_compare_threshold
        else:
            mat_fast64.rdp_settings.g_mdsft_alpha_compare = "G_AC_NONE"
            alpha_compare_threshold = None

    mat_fast64.set_blend = True
    mat_fast64.blend_color = (
        *mat_rdpq.blender.blend_color,
        1 if alpha_compare_threshold is None else (alpha_compare_threshold / 255),
    )

    mat_fast64.rdp_settings.z_cmp = (
        mat_rdpq.override_render_mode.z_compare
        if mat_rdpq.override_render_mode.override_z_compare
        else world_rdpq.defaults.z_compare
    )

    mat_fast64.rdp_settings.z_upd = (
        mat_rdpq.override_render_mode.z_update
        if mat_rdpq.override_render_mode.override_z_update
        else world_rdpq.defaults.z_update
    )

    if mat_rdpq.override_render_mode.override_fixed_z:
        mat_fast64.rdp_settings.g_mdsft_zsrcsel = "G_ZS_PRIM"
        mat_fast64.rdp_settings.prim_depth.z = mat_rdpq.override_render_mode.fixed_z
        mat_fast64.rdp_settings.prim_depth.dz = (
            mat_rdpq.override_render_mode.fixed_z_deltaz
        )
    else:
        if world_rdpq.defaults.fixed_z:
            mat_fast64.rdp_settings.g_mdsft_zsrcsel = "G_ZS_PRIM"
            mat_fast64.rdp_settings.prim_depth.z = world_rdpq.defaults.fixed_z_value
            mat_fast64.rdp_settings.prim_depth.dz = world_rdpq.defaults.fixed_z_deltaz
        else:
            mat_fast64.rdp_settings.g_mdsft_zsrcsel = "G_ZS_PIXEL"

    # Other

    mat_fast64.rdp_settings.g_shade_smooth = True
    mat_fast64.rdp_settings.g_lighting = False
    mat_fast64.rdp_settings.g_cull_front = False
    mat_fast64.rdp_settings.g_cull_back = True
    mat_fast64.rdp_settings.g_zbuffer = True
    mat_fast64.rdp_settings.g_shade = True


QUEUED_UPDATES = set()


def msgbus_sync_rdpq_material_props_to_fast64_props(
    owner: object,
    mat: bpy.types.Material,
):

    def sync_callback():
        if mat in QUEUED_UPDATES:
            return
        scene = bpy.context.scene
        if scene is None:
            return
        world = scene.world
        if world is None:
            return

        def delayed_callback():
            QUEUED_UPDATES.discard(mat)
            with bpy.context.temp_override(material=mat):
                rdpq_material_props_to_fast64_props(mat, world)

        QUEUED_UPDATES.add(mat)
        bpy.app.timers.register(delayed_callback, first_interval=0.2)

    def sync_subscribe(thing: bpy.types.bpy_struct, props_list: RecursivePropsList):
        for prop_name in props_list.props:
            bpy.msgbus.subscribe_rna(
                key=thing.path_resolve(prop_name, False),
                owner=owner,
                args=(),
                notify=sync_callback,
            )
        for group_prop_name, group_prop_list in props_list.groups.items():
            sync_subscribe(getattr(thing, group_prop_name), group_prop_list)

    sync_subscribe(mat, LIBDRAGON_RDPQ_PROPS_LIST)


class RDPQMaterialPropsToFast64Operator(bpy.types.Operator):
    bl_idname = "libdragon_rdpq.rdpq_material_props_to_fast64"
    bl_label = "RDPQ properties to Fast64"

    @classmethod
    def poll(cls, context):
        return (
            hasattr(context, "material")
            and context.material is not None
            and is_fast64_material(context.material)
            and context.scene is not None
            and context.scene.world is not None
        )

    def execute(self, context):
        mat = context.material
        assert mat is not None
        assert context.scene is not None
        world = context.scene.world
        assert world is not None
        rdpq_material_props_to_fast64_props(mat, world)
        return {"FINISHED"}


@dataclasses.dataclass
class RecursivePropsList:
    props: tuple[str, ...]
    groups: dict[str, "RecursivePropsList"]


LIBDRAGON_RDPQ_TEXTURE_AXIS_PROPS_LIST = RecursivePropsList(
    (
        "translate",
        "scale",
        "repeats_inf",
        "repeats",
        "mirror",
    ),
    {},
)
LIBDRAGON_RDPQ_TEXTURE_PROPS_LIST = RecursivePropsList(
    (
        "use_placeholder",
        "placeholder",
        "image",
        "format",
        "mipmap",
        "dithering",
    ),
    {
        "s": LIBDRAGON_RDPQ_TEXTURE_AXIS_PROPS_LIST,
        "t": LIBDRAGON_RDPQ_TEXTURE_AXIS_PROPS_LIST,
    },
)
LIBDRAGON_RDPQ_PROPS_LIST = RecursivePropsList(
    (),
    {
        "libdragon_rdpq": RecursivePropsList(
            (
                # "auto_sync_to_fast64",  # left out on purpose
                "use_texture0",
                "use_texture1",
            ),
            {
                "texture0": LIBDRAGON_RDPQ_TEXTURE_PROPS_LIST,
                "combiner": RecursivePropsList(
                    (
                        "preset",
                        "rgb_A",
                        "rgb_B",
                        "rgb_C",
                        "rgb_D",
                        "alpha_A",
                        "alpha_B",
                        "alpha_C",
                        "alpha_D",
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
                        "p",
                        "a",
                        "q",
                        "b",
                        "p_0",
                        "a_0",
                        "q_0",
                        "b_0",
                        "p_1",
                        "a_1",
                        "q_1",
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


def rdpq_material_recreate_as_fast64(
    mat: bpy.types.Material, world: Optional[bpy.types.World]
):
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
    rdpq_material_props_to_fast64_props(new_mat, world)

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
        return (
            hasattr(context, "material")
            and context.material is not None
            and context.scene is not None
            and context.scene.world is not None
        )

    def execute(self, context):
        mat = context.material
        assert mat is not None
        assert context.scene is not None
        world = context.scene.world
        assert world is not None
        rdpq_material_recreate_as_fast64(mat, world)
        return {"FINISHED"}


def prop_split(layout: bpy.types.UILayout, data, prop_name: str):
    layout.use_property_split = True
    layout.use_property_decorate = False
    layout.prop(data, prop_name)
    layout.use_property_split = False


class RDPQWorldPanel(bpy.types.Panel):
    bl_label = "RDPQ Defaults"
    bl_idname = "WORLD_PT_libdragon_rdpq"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "world"

    @classmethod
    def poll(cls, context):
        return context.world is not None

    def draw(self, context):
        layout = self.layout
        assert layout is not None
        world = context.world
        assert world is not None
        world_rdpq: RDPQWorldProperties = world.libdragon_rdpq

        layout.prop(world_rdpq.defaults, "antialias")
        layout.prop(world_rdpq.defaults, "fog")
        layout.prop(world_rdpq.defaults, "dithering")
        layout.prop(world_rdpq.defaults, "texture_filtering")
        layout.prop(world_rdpq.defaults, "texture_perspective_correction")

        row = layout.row()
        row.prop(world_rdpq.defaults, "alpha_compare", text="")
        col = row.column()
        col.prop(world_rdpq.defaults, "alpha_compare_threshold")
        col.enabled = world_rdpq.defaults.alpha_compare

        layout.prop(world_rdpq.defaults, "z_compare")
        layout.prop(world_rdpq.defaults, "z_update")

        row = layout.row()
        row.prop(world_rdpq.defaults, "fixed_z")
        col = row.column()
        col.prop(world_rdpq.defaults, "fixed_z_value")
        col.prop(world_rdpq.defaults, "fixed_z_deltaz")
        col.enabled = world_rdpq.defaults.fixed_z


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
                if mat_rdpq.auto_sync_to_fast64:
                    layout.prop(mat_rdpq, "auto_sync_to_fast64")
                else:
                    row = layout.row()
                    if context.scene is None or context.scene.world is None:
                        col = row.column()
                        col.prop(mat_rdpq, "auto_sync_to_fast64")
                        col.enabled = False
                    else:
                        row.prop(mat_rdpq, "auto_sync_to_fast64")
                    row.operator(
                        RDPQMaterialPropsToFast64Operator.bl_idname,
                        text="Sync to Fast64 props",
                    )
                    if context.scene is None or context.scene.world is None:
                        layout.label(text="Scene has no world!", icon="ERROR")
            else:
                layout.operator(
                    RDPQMaterialRecreateAsFast64Operator.bl_idname,
                    text="Recreate as Fast64 material",
                )

        def prop_texture(
            box: bpy.types.UILayout,
            texture_props: RDPQMaterialTextureProperties,
        ):
            row = box.row()
            row.prop(texture_props, "use_placeholder", text="")
            col = row.column()
            col.prop(texture_props, "placeholder")
            col.enabled = texture_props.use_placeholder

            box.template_ID(texture_props, "image", new="image.new", open="image.open")
            prop_split(box, texture_props, "format")
            prop_split(box, texture_props, "mipmap")
            prop_split(box, texture_props, "dithering")

            box_s = box.box()
            box_s.label(text="S Properties")
            box_s.prop(texture_props.s, "translate")
            box_s.prop(texture_props.s, "scale")

            row = box_s.row()
            row.label(text="Repeats")
            col = row.column()
            col.prop(texture_props.s, "repeats", text="")
            col.enabled = not texture_props.s.repeats_inf
            row.prop(texture_props.s, "repeats_inf", text="Infinite")

            box_s.prop(texture_props.s, "mirror")

            box_t = box.box()
            box_t.label(text="T Properties")
            box_t.prop(texture_props.t, "translate")
            box_t.prop(texture_props.t, "scale")

            row = box_t.row()
            row.label(text="Repeats")
            col = row.column()
            col.prop(texture_props.t, "repeats", text="")
            col.enabled = not texture_props.t.repeats_inf
            row.prop(texture_props.t, "repeats_inf", text="Infinite")

            box_t.prop(texture_props.t, "mirror")

        box = layout.box()
        box.prop(mat_rdpq, "use_texture0")
        if mat_rdpq.use_texture0:
            prop_texture(box, mat_rdpq.texture0)
            box = layout.box()
            box.prop(mat_rdpq, "use_texture1")
            if mat_rdpq.use_texture1:
                prop_texture(box, mat_rdpq.texture1)

        box = layout.box()
        prop_split(box, mat_rdpq.combiner, "preset")
        if mat_rdpq.combiner.preset == "CUSTOM_1_PASS":
            box.prop(mat_rdpq.combiner, "rgb_A")
            box.prop(mat_rdpq.combiner, "rgb_B")
            box.prop(mat_rdpq.combiner, "rgb_C")
            box.prop(mat_rdpq.combiner, "rgb_D")
            box.prop(mat_rdpq.combiner, "alpha_A")
            box.prop(mat_rdpq.combiner, "alpha_B")
            box.prop(mat_rdpq.combiner, "alpha_C")
            box.prop(mat_rdpq.combiner, "alpha_D")
        if mat_rdpq.combiner.preset == "CUSTOM_2_PASSES":
            box.prop(mat_rdpq.combiner, "rgb_A_0")
            box.prop(mat_rdpq.combiner, "rgb_B_0")
            box.prop(mat_rdpq.combiner, "rgb_C_0")
            box.prop(mat_rdpq.combiner, "rgb_D_0")
            box.prop(mat_rdpq.combiner, "alpha_A_0")
            box.prop(mat_rdpq.combiner, "alpha_B_0")
            box.prop(mat_rdpq.combiner, "alpha_C_0")
            box.prop(mat_rdpq.combiner, "alpha_D_0")
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
        if mat_rdpq.blender.preset == "CUSTOM_1_PASS":
            box.prop(mat_rdpq.blender, "p")
            box.prop(mat_rdpq.blender, "a")
            box.prop(mat_rdpq.blender, "q")
            box.prop(mat_rdpq.blender, "b")
        if mat_rdpq.blender.preset == "CUSTOM_2_PASSES":
            box.prop(mat_rdpq.blender, "p_0")
            box.prop(mat_rdpq.blender, "a_0")
            box.prop(mat_rdpq.blender, "q_0")
            box.prop(mat_rdpq.blender, "b_0")
            box.prop(mat_rdpq.blender, "p_1")
            box.prop(mat_rdpq.blender, "a_1")
            box.prop(mat_rdpq.blender, "q_1")
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


COMBINER_MUXES_MKMATERIAL_MAP = {
    "COMBINED": "combined",
    "COMBINED_ALPHA": "combined.a",
    "TEX0": "tex0",
    "TEX0_BUG": "tex0",
    "TEX1": "tex1",
    "SHADE": "shade",
    "PRIM": "prim",
    "ENV": "env",
    "NOISE": "noise",
    "1": "1",
    "0": "0",
    "K4": "k4",
    "K5": "k5",
    "TEX0_ALPHA": "tex0.a",
    "TEX1_ALPHA": "tex1.a",
    "SHADE_ALPHA": "shade.a",
    "PRIM_ALPHA": "prim.a",
    "ENV_ALPHA": "env.a",
    "LOD_FRAC": "lod_frac",
    "PRIM_LOD_FRAC": "prim_lod_frac",
    "KEYCENTER": "keycenter",
    "KEYSCALE": "keyscale",
}


def rdpq_material_properties_to_dict(mat_rdpq: RDPQMaterialProperties):
    mat_data = {}

    def handle_texture_axis(
        tex_i: int, axis: str, texture_axis_props: RDPQMaterialTextureAxisProperties
    ):
        mat_data.update(
            {
                f"tex{tex_i}.{axis}.translate": str(texture_axis_props.translate),
                f"tex{tex_i}.{axis}.scale": str(texture_axis_props.scale),
                f"tex{tex_i}.{axis}.repeats": (
                    "inf"
                    if texture_axis_props.repeats_inf
                    else str(texture_axis_props.repeats)
                ),
                f"tex{tex_i}.{axis}.mirror": str(texture_axis_props.mirror),
            }
        )

    def handle_texture(tex_i: int, texture_props: RDPQMaterialTextureProperties):
        if texture_props.image is not None:
            # TODO the image name is not the right thing to use here
            mat_data[f"tex{tex_i}.name"] = texture_props.image.name
        mat_data.update(
            {
                f"tex{tex_i}.fmt": texture_props.format,
                f"tex{tex_i}.mipmap": texture_props.mipmap.lower(),
                f"tex{tex_i}.dithering": texture_props.dithering,
            }
        )
        handle_texture_axis(tex_i, "s", texture_props.s)
        handle_texture_axis(tex_i, "t", texture_props.t)

    if mat_rdpq.use_texture0:
        handle_texture(0, mat_rdpq.texture0)
    if mat_rdpq.use_texture1:
        handle_texture(1, mat_rdpq.texture1)

    map = COMBINER_MUXES_MKMATERIAL_MAP

    if mat_rdpq.combiner.preset == "CUSTOM_1_PASS":
        combiner_rgb = (
            f"({map[mat_rdpq.combiner.rgb_A]},{map[mat_rdpq.combiner.rgb_B]},"
            f"{map[mat_rdpq.combiner.rgb_C]},{map[mat_rdpq.combiner.rgb_D]})"
        )
        combiner_alpha = (
            f"({map[mat_rdpq.combiner.alpha_A]},{map[mat_rdpq.combiner.alpha_B]},"
            f"{map[mat_rdpq.combiner.alpha_C]},{map[mat_rdpq.combiner.alpha_D]})"
        )
    elif mat_rdpq.combiner.preset == "CUSTOM_2_PASSES":
        combiner_rgb = (
            f"({map[mat_rdpq.combiner.rgb_A_0]},{map[mat_rdpq.combiner.rgb_B_0]},"
            f"{map[mat_rdpq.combiner.rgb_C_0]},{map[mat_rdpq.combiner.rgb_D_0]})"
            ","
            f"({map[mat_rdpq.combiner.rgb_A_1]},{map[mat_rdpq.combiner.rgb_B_1]},"
            f"{map[mat_rdpq.combiner.rgb_C_1]},{map[mat_rdpq.combiner.rgb_D_1]})"
        )
        combiner_alpha = (
            f"({map[mat_rdpq.combiner.alpha_A_0]},{map[mat_rdpq.combiner.alpha_B_0]},"
            f"{map[mat_rdpq.combiner.alpha_C_0]},{map[mat_rdpq.combiner.alpha_D_0]})"
            ","
            f"({map[mat_rdpq.combiner.alpha_A_1]},{map[mat_rdpq.combiner.alpha_B_1]},"
            f"{map[mat_rdpq.combiner.alpha_C_1]},{map[mat_rdpq.combiner.alpha_D_1]})"
        )
    else:
        combiner_rgb, combiner_alpha = {
            "FLAT": (
                "(0,0,0,prim)",
                "(0,0,0,prim)",
            ),
            "SHADE": (
                "(0,0,0,shade)",
                "(0,0,0,shade)",
            ),
            "TEX": (
                "(0,0,0,tex0)",
                "(0,0,0,tex0)",
            ),
            "TEX_FLAT": (
                "(tex0,0,prim,0)",
                "(tex0,0,prim,0)",
            ),
            "TEX_SHADE": (
                "(tex0,0,shade,0)",
                "(tex0,0,shade,0)",
            ),
        }[mat_rdpq.combiner.preset]

    mat_data.update(
        {
            "combiner.rgb.raw": combiner_rgb,
            "combiner.alpha.raw": combiner_alpha,
        }
    )

    if mat_rdpq.blender.preset == "CUSTOM_1_PASS":
        raise NotImplementedError()
    elif mat_rdpq.blender.preset == "CUSTOM_2_PASSES":
        raise NotImplementedError()
    else:
        mat_data["blender.mode"] = mat_rdpq.blender.preset.lower()
        if mat_rdpq.blender.preset == "MULTIPLY_CONST":
            mat_data["blender.const"] = str(mat_rdpq.blender.fog_color[3])

    if mat_rdpq.override_render_mode.override_antialias:
        mat_data["rm.antialias"] = mat_rdpq.override_render_mode.antialias.lower()
    if mat_rdpq.override_render_mode.override_fog:
        mat_data["rm.fog"] = mat_rdpq.override_render_mode.fog.lower()
    if mat_rdpq.override_render_mode.override_dithering:
        mat_data["rm.dither.rgb"], mat_data["rm.dither.alpha"] = {
            "RGB_SQUARE_A_SQUARE": ("square", "square"),
            "RGB_SQUARE_A_INVSQUARE": ("square", "invsquare"),
            "RGB_SQUARE_A_NOISE": ("square", "noise"),
            "RGB_SQUARE_A_NONE": ("square", "none"),
            "RGB_BAYER_A_BAYER": ("bayer", "bayer"),
            "RGB_BAYER_A_INVBAYER": ("bayer", "invbayer"),
            "RGB_BAYER_A_NOISE": ("bayer", "noise"),
            "RGB_BAYER_A_NONE": ("bayer", "none"),
            "RGB_NOISE_A_SQUARE": ("noise", "square"),
            "RGB_NOISE_A_INVSQUARE": ("noise", "invsquare"),
            "RGB_NOISE_A_NOISE": ("noise", "noise"),
            "RGB_NOISE_A_NONE": ("noise", "none"),
            "RGB_NONE_A_BAYER": ("none", "bayer"),
            "RGB_NONE_A_INVBAYER": ("none", "invbayer"),
            "RGB_NONE_A_NOISE": ("none", "noise"),
            "RGB_NONE_A_NONE": ("none", "none"),
        }[(mat_rdpq.override_render_mode.dithering)]
    if mat_rdpq.override_render_mode.override_texture_filtering:
        mat_data["rm.filtering"] = (
            mat_rdpq.override_render_mode.texture_filtering.lower()
        )
    if mat_rdpq.override_render_mode.override_texture_perspective_correction:
        mat_data["rm.perspective"] = str(
            mat_rdpq.override_render_mode.texture_perspective_correction
        )
    if mat_rdpq.override_render_mode.override_alpha_compare:
        mat_data["rm.alpha_compare"] = str(
            mat_rdpq.override_render_mode.alpha_compare_threshold
        )
    # mat_data["rm.zmode"]  # TODO
    if mat_rdpq.override_render_mode.override_fixed_z:
        mat_data["rm.z_override"] = str(mat_rdpq.override_render_mode.fixed_z)
        mat_data["rm.deltaz_override"] = str(
            mat_rdpq.override_render_mode.fixed_z_deltaz
        )

    return mat_data


class RDPQMaterialExportOperator(bpy.types.Operator):
    bl_idname = "libdragon_rdpq.rdpq_material_export"
    bl_label = "Export RDPQ material"

    out_file: bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        return hasattr(context, "material") and context.material is not None

    def execute(self, context):
        mat = context.material
        assert mat is not None
        mat_rdpq: RDPQMaterialProperties = mat.libdragon_rdpq

        mat_data = rdpq_material_properties_to_dict(mat_rdpq)

        import json

        mat_library_json = json.dumps({mat.name: mat_data}, indent=0)

        Path(self.out_file).write_text(mat_library_json)

        return {"FINISHED"}


# https://github.com/KhronosGroup/glTF-Blender-IO/blob/main/example-addons/example_gltf_exporter_extension

glTF_extension_name = "EXT_libdragon_rdpq_materials_jmat"


class glTF2ExportUserExtension:

    def __init__(self):
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension

        self.Extension = Extension
        self.properties = bpy.context.scene.libdragon_rdpq.gltf_extension

    def gather_material_hook(
        self,
        gltf2_material: "io_scene_gltf2.io.com.gltf2_io.Material",
        blender_material: bpy.types.Material,
        export_settings,
    ):
        gltf2_material.extensions[glTF_extension_name] = (
            rdpq_material_properties_to_dict(blender_material.libdragon_rdpq)
        )


class glTFExtensionProperties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name=bl_info["name"],
        description="Include this extension in the exported glTF file.",
        default=True,
    )


def draw_gltf_extension_props(context: bpy.types.Context, layout: bpy.types.UILayout):
    layout.use_property_split = False
    layout.prop(context.scene.libdragon_rdpq.gltf_extension, "enabled")


class RDPQSceneProperties(bpy.types.PropertyGroup):
    gltf_extension: bpy.props.PointerProperty(type=glTFExtensionProperties)


classes = (
    glTFExtensionProperties,
    RDPQSceneProperties,
    RDPQWorldDefaultsProperties,
    RDPQWorldProperties,
    RDPQMaterialTextureAxisProperties,
    RDPQMaterialTextureProperties,
    RDPQMaterialCombinerProperties,
    RDPQMaterialBlenderProperties,
    RDPQMaterialOverrideRenderModeProperties,
    RDPQMaterialProperties,
    RDPQMaterialPropsToFast64Operator,
    RDPQMaterialRecreateAsFast64Operator,
    RDPQMaterialExportOperator,
    RDPQWorldPanel,
    RDPQMaterialPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.libdragon_rdpq = bpy.props.PointerProperty(type=RDPQSceneProperties)
    bpy.types.Material.libdragon_rdpq = bpy.props.PointerProperty(
        type=RDPQMaterialProperties
    )
    bpy.types.World.libdragon_rdpq = bpy.props.PointerProperty(type=RDPQWorldProperties)
    bpy.app.handlers.load_post.append(
        handler_load_post_start_materials_auto_sync_to_fast64
    )
    bpy.app.timers.register(
        lambda: handler_load_post_start_materials_auto_sync_to_fast64()
    )

    from io_scene_gltf2 import exporter_extension_layout_draw

    exporter_extension_layout_draw["libdragon RDPQ materials"] = (
        draw_gltf_extension_props
    )


def unregister():
    from io_scene_gltf2 import exporter_extension_layout_draw

    del exporter_extension_layout_draw["libdragon RDPQ materials"]

    try:
        bpy.app.handlers.load_post.remove(
            handler_load_post_start_materials_auto_sync_to_fast64
        )
    except ValueError:
        pass
    del bpy.types.Scene.libdragon_rdpq
    del bpy.types.Material.libdragon_rdpq
    del bpy.types.World.libdragon_rdpq
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
