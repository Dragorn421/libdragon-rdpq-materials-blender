import bpy

from . import util


def on_update_combiner_preset(self, context: bpy.types.Context):
    mat = context.material
    assert mat is not None
    mat_rdpq = util.LIBDRAGON_RDPQ(mat)
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



def on_update_blender_preset(self, context: bpy.types.Context):
    mat = context.material
    assert mat is not None
    mat_rdpq = util.LIBDRAGON_RDPQ(mat)
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


