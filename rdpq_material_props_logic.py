import bpy

from . import util

# Note: don't get the material from the context,
# for example during gltf import context.material is not set.


def on_update_combiner_preset(self, context: bpy.types.Context):
    from . import rdpq_material_props

    assert isinstance(self, rdpq_material_props.RDPQMaterialCombinerProperties)
    mat_rdpq_cb = self
    if mat_rdpq_cb.preset == "FLAT":
        mat_rdpq_cb.rgb_A = "0"
        mat_rdpq_cb.rgb_B = "0"
        mat_rdpq_cb.rgb_C = "0"
        mat_rdpq_cb.rgb_D = "PRIM"
        mat_rdpq_cb.alpha_A = "0"
        mat_rdpq_cb.alpha_B = "0"
        mat_rdpq_cb.alpha_C = "0"
        mat_rdpq_cb.alpha_D = "PRIM"

        mat_rdpq_cb.rgb_A_0 = "0"
        mat_rdpq_cb.rgb_B_0 = "0"
        mat_rdpq_cb.rgb_C_0 = "0"
        mat_rdpq_cb.rgb_D_0 = "PRIM"
        mat_rdpq_cb.alpha_A_0 = "0"
        mat_rdpq_cb.alpha_B_0 = "0"
        mat_rdpq_cb.alpha_C_0 = "0"
        mat_rdpq_cb.alpha_D_0 = "PRIM"

        mat_rdpq_cb.rgb_A_1 = "0"
        mat_rdpq_cb.rgb_B_1 = "0"
        mat_rdpq_cb.rgb_C_1 = "0"
        mat_rdpq_cb.rgb_D_1 = "PRIM"
        mat_rdpq_cb.alpha_A_1 = "0"
        mat_rdpq_cb.alpha_B_1 = "0"
        mat_rdpq_cb.alpha_C_1 = "0"
        mat_rdpq_cb.alpha_D_1 = "PRIM"
    elif mat_rdpq_cb.preset == "SHADE":
        # TODO handle fog
        mat_rdpq_cb.rgb_A = "0"
        mat_rdpq_cb.rgb_B = "0"
        mat_rdpq_cb.rgb_C = "0"
        mat_rdpq_cb.rgb_D = "SHADE"
        mat_rdpq_cb.alpha_A = "0"
        mat_rdpq_cb.alpha_B = "0"
        mat_rdpq_cb.alpha_C = "0"
        mat_rdpq_cb.alpha_D = "SHADE"

        mat_rdpq_cb.rgb_A_0 = "0"
        mat_rdpq_cb.rgb_B_0 = "0"
        mat_rdpq_cb.rgb_C_0 = "0"
        mat_rdpq_cb.rgb_D_0 = "SHADE"
        mat_rdpq_cb.alpha_A_0 = "0"
        mat_rdpq_cb.alpha_B_0 = "0"
        mat_rdpq_cb.alpha_C_0 = "0"
        mat_rdpq_cb.alpha_D_0 = "SHADE"

        mat_rdpq_cb.rgb_A_1 = "0"
        mat_rdpq_cb.rgb_B_1 = "0"
        mat_rdpq_cb.rgb_C_1 = "0"
        mat_rdpq_cb.rgb_D_1 = "SHADE"
        mat_rdpq_cb.alpha_A_1 = "0"
        mat_rdpq_cb.alpha_B_1 = "0"
        mat_rdpq_cb.alpha_C_1 = "0"
        mat_rdpq_cb.alpha_D_1 = "SHADE"
    elif mat_rdpq_cb.preset == "TEX":
        # TODO handle mipmapping / custom image formats
        mat_rdpq_cb.rgb_A = "0"
        mat_rdpq_cb.rgb_B = "0"
        mat_rdpq_cb.rgb_C = "0"
        mat_rdpq_cb.rgb_D = "TEX0"
        mat_rdpq_cb.alpha_A = "0"
        mat_rdpq_cb.alpha_B = "0"
        mat_rdpq_cb.alpha_C = "0"
        mat_rdpq_cb.alpha_D = "TEX0"

        mat_rdpq_cb.rgb_A_0 = "0"
        mat_rdpq_cb.rgb_B_0 = "0"
        mat_rdpq_cb.rgb_C_0 = "0"
        mat_rdpq_cb.rgb_D_0 = "TEX0"
        mat_rdpq_cb.alpha_A_0 = "0"
        mat_rdpq_cb.alpha_B_0 = "0"
        mat_rdpq_cb.alpha_C_0 = "0"
        mat_rdpq_cb.alpha_D_0 = "TEX0"

        mat_rdpq_cb.rgb_A_1 = "0"
        mat_rdpq_cb.rgb_B_1 = "0"
        mat_rdpq_cb.rgb_C_1 = "0"
        mat_rdpq_cb.rgb_D_1 = "COMBINED"
        mat_rdpq_cb.alpha_A_1 = "0"
        mat_rdpq_cb.alpha_B_1 = "0"
        mat_rdpq_cb.alpha_C_1 = "0"
        mat_rdpq_cb.alpha_D_1 = "COMBINED"
    elif mat_rdpq_cb.preset == "TEX_FLAT":
        # TODO handle mipmapping / custom image formats
        mat_rdpq_cb.rgb_A = "TEX0"
        mat_rdpq_cb.rgb_B = "0"
        mat_rdpq_cb.rgb_C = "PRIM"
        mat_rdpq_cb.rgb_D = "0"
        mat_rdpq_cb.alpha_A = "TEX0"
        mat_rdpq_cb.alpha_B = "0"
        mat_rdpq_cb.alpha_C = "PRIM"
        mat_rdpq_cb.alpha_D = "0"

        mat_rdpq_cb.rgb_A_0 = "TEX0"
        mat_rdpq_cb.rgb_B_0 = "0"
        mat_rdpq_cb.rgb_C_0 = "PRIM"
        mat_rdpq_cb.rgb_D_0 = "0"
        mat_rdpq_cb.alpha_A_0 = "TEX0"
        mat_rdpq_cb.alpha_B_0 = "0"
        mat_rdpq_cb.alpha_C_0 = "PRIM"
        mat_rdpq_cb.alpha_D_0 = "0"

        mat_rdpq_cb.rgb_A_1 = "0"
        mat_rdpq_cb.rgb_B_1 = "0"
        mat_rdpq_cb.rgb_C_1 = "0"
        mat_rdpq_cb.rgb_D_1 = "COMBINED"
        mat_rdpq_cb.alpha_A_1 = "0"
        mat_rdpq_cb.alpha_B_1 = "0"
        mat_rdpq_cb.alpha_C_1 = "0"
        mat_rdpq_cb.alpha_D_1 = "COMBINED"
    elif mat_rdpq_cb.preset == "TEX_SHADE":
        # TODO handle mipmapping / custom image formats and fog
        mat_rdpq_cb.rgb_A = "TEX0"
        mat_rdpq_cb.rgb_B = "0"
        mat_rdpq_cb.rgb_C = "SHADE"
        mat_rdpq_cb.rgb_D = "0"
        mat_rdpq_cb.alpha_A = "TEX0"
        mat_rdpq_cb.alpha_B = "0"
        mat_rdpq_cb.alpha_C = "SHADE"
        mat_rdpq_cb.alpha_D = "0"

        mat_rdpq_cb.rgb_A_0 = "TEX0"
        mat_rdpq_cb.rgb_B_0 = "0"
        mat_rdpq_cb.rgb_C_0 = "SHADE"
        mat_rdpq_cb.rgb_D_0 = "0"
        mat_rdpq_cb.alpha_A_0 = "TEX0"
        mat_rdpq_cb.alpha_B_0 = "0"
        mat_rdpq_cb.alpha_C_0 = "SHADE"
        mat_rdpq_cb.alpha_D_0 = "0"

        mat_rdpq_cb.rgb_A_1 = "0"
        mat_rdpq_cb.rgb_B_1 = "0"
        mat_rdpq_cb.rgb_C_1 = "0"
        mat_rdpq_cb.rgb_D_1 = "COMBINED"
        mat_rdpq_cb.alpha_A_1 = "0"
        mat_rdpq_cb.alpha_B_1 = "0"
        mat_rdpq_cb.alpha_C_1 = "0"
        mat_rdpq_cb.alpha_D_1 = "COMBINED"


def on_update_blender_preset(self, context: bpy.types.Context):
    from . import rdpq_material_props

    assert isinstance(self, rdpq_material_props.RDPQMaterialBlenderProperties)
    mat_rdpq_bl = self
    # TODO handle fog
    if mat_rdpq_bl.preset == "NONE":
        # rdpq_mode_blender suggests passing "0 to disable", which corresponds to
        # RDPQ_BLENDER((IN_RGB, IN_ALPHA, IN_RGB, INV_MUX_ALPHA))

        mat_rdpq_bl.p = "IN_RGB"
        mat_rdpq_bl.a = "IN_ALPHA"
        mat_rdpq_bl.q = "IN_RGB"
        mat_rdpq_bl.b = "INV_MUX_ALPHA"

        mat_rdpq_bl.p_0 = "IN_RGB"
        mat_rdpq_bl.a_0 = "IN_ALPHA"
        mat_rdpq_bl.q_0 = "IN_RGB"
        mat_rdpq_bl.b_0 = "INV_MUX_ALPHA"
        mat_rdpq_bl.p_1 = "CYCLE1_RGB"
        mat_rdpq_bl.a_1 = "IN_ALPHA"
        mat_rdpq_bl.q_1 = "CYCLE1_RGB"
        mat_rdpq_bl.b_1 = "INV_MUX_ALPHA"
    elif mat_rdpq_bl.preset == "MULTIPLY":
        # RDPQ_BLENDER((IN_RGB, IN_ALPHA, MEMORY_RGB, INV_MUX_ALPHA))

        mat_rdpq_bl.p = "IN_RGB"
        mat_rdpq_bl.a = "IN_ALPHA"
        mat_rdpq_bl.q = "MEMORY_RGB"
        mat_rdpq_bl.b = "INV_MUX_ALPHA"

        mat_rdpq_bl.p_0 = "IN_RGB"
        mat_rdpq_bl.a_0 = "IN_ALPHA"
        mat_rdpq_bl.q_0 = "IN_RGB"
        mat_rdpq_bl.b_0 = "INV_MUX_ALPHA"

        mat_rdpq_bl.p_1 = "CYCLE1_RGB"
        mat_rdpq_bl.a_1 = "IN_ALPHA"
        mat_rdpq_bl.q_1 = "MEMORY_RGB"
        mat_rdpq_bl.b_1 = "INV_MUX_ALPHA"
    elif mat_rdpq_bl.preset == "MULTIPLY_CONST":
        # RDPQ_BLENDER((IN_RGB, FOG_ALPHA, MEMORY_RGB, INV_MUX_ALPHA))

        mat_rdpq_bl.p = "IN_RGB"
        mat_rdpq_bl.a = "FOG_ALPHA"
        mat_rdpq_bl.q = "MEMORY_RGB"
        mat_rdpq_bl.b = "INV_MUX_ALPHA"

        mat_rdpq_bl.p_0 = "IN_RGB"
        mat_rdpq_bl.a_0 = "IN_ALPHA"
        mat_rdpq_bl.q_0 = "IN_RGB"
        mat_rdpq_bl.b_0 = "INV_MUX_ALPHA"

        mat_rdpq_bl.p_1 = "CYCLE1_RGB"
        mat_rdpq_bl.a_1 = "FOG_ALPHA"
        mat_rdpq_bl.q_1 = "MEMORY_RGB"
        mat_rdpq_bl.b_1 = "INV_MUX_ALPHA"
    elif mat_rdpq_bl.preset == "ADDITIVE":
        # RDPQ_BLENDER((IN_RGB, IN_ALPHA, MEMORY_RGB, ONE))

        mat_rdpq_bl.p = "IN_RGB"
        mat_rdpq_bl.a = "IN_ALPHA"
        mat_rdpq_bl.q = "MEMORY_RGB"
        mat_rdpq_bl.b = "1"

        mat_rdpq_bl.p_0 = "IN_RGB"
        mat_rdpq_bl.a_0 = "IN_ALPHA"
        mat_rdpq_bl.q_0 = "IN_RGB"
        mat_rdpq_bl.b_0 = "INV_MUX_ALPHA"

        mat_rdpq_bl.p_1 = "CYCLE1_RGB"
        mat_rdpq_bl.a_1 = "IN_ALPHA"
        mat_rdpq_bl.q_1 = "MEMORY_RGB"
        mat_rdpq_bl.b_1 = "1"


SHADER_NODE_TEX_IMAGE_NAME = "libdragon RDPQ materials for face texture selection"


# This function ensures there is an active texture image shader node with the current
# material's image in the material's nodes.  This makes "face texture selection" work,
# the feature that switches the image in the UV editor based on the currently active
# face in edit mode.
def on_update_texture_image(self, context: bpy.types.Context):
    from . import rdpq_material_props

    assert isinstance(self, rdpq_material_props.RDPQMaterialTextureProperties)
    mat = self.id_data
    assert isinstance(mat, bpy.types.Material)

    image = None
    if mat is not None:
        mat_rdpq = util.LIBDRAGON_RDPQ(mat)
        if mat_rdpq.use_texture0:
            image = mat_rdpq.texture0.image
        if image is None and mat_rdpq.use_texture1:
            image = mat_rdpq.texture1.image

    if mat.node_tree is None:
        mat.node_tree = bpy.data.node_groups.new(mat.name, "ShaderNodeTree")  # type: ignore
    assert mat.node_tree is not None
    node = mat.node_tree.nodes.get(SHADER_NODE_TEX_IMAGE_NAME)
    if node is not None and not isinstance(node, bpy.types.ShaderNodeTexImage):
        node.name = "_" + SHADER_NODE_TEX_IMAGE_NAME
        node = None
    if node is None:
        node = mat.node_tree.nodes.new("ShaderNodeTexImage")
        assert isinstance(node, bpy.types.ShaderNodeTexImage)
        node.name = SHADER_NODE_TEX_IMAGE_NAME
    node.image = image
    mat.node_tree.nodes.active = node
