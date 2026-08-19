import bpy

from . import gltf_extension_common
from . import mkmaterial_export
from . import util

if gltf_extension_common.gltf_export_props_use_register_panel:

    class GLTF_PT_RDPQPanel(bpy.types.Panel):

        bl_space_type = "FILE_BROWSER"
        bl_region_type = "TOOL_PROPS"
        bl_label = "libdragon RDPQ materials"
        bl_parent_id = "GLTF_PT_export_user_extensions"
        bl_options = {"DEFAULT_CLOSED"}

        @classmethod
        def poll(cls, context):
            sfile = context.space_data
            assert isinstance(sfile, bpy.types.SpaceFileBrowser)
            operator = sfile.active_operator
            assert operator is not None
            return operator.bl_idname == "EXPORT_SCENE_OT_gltf"

        def draw(self, context):
            assert self.layout is not None
            draw_gltf_extension_props(context, self.layout)


# https://github.com/KhronosGroup/glTF-Blender-IO/blob/main/example-addons/example_gltf_exporter_extension


def export_standalone_image(
    blender_material: bpy.types.Material,
    blender_image: bpy.types.Image,
    export_settings,
):
    """Export a blender Image to a glTF TextureInfo.

    This is done by creating a temporary image texture node in the material's node
    tree, and passing that node to internal glTF code.

    Note the returned TextureInfo needs to be referenced in the glTF data
    (e.g. in the material extensions dict) for it to be present in the output glTF
    """
    assert gltf_extension_common.glTF2_addon_ver is not None

    if gltf_extension_common.glTF2_addon_ver >= (4, 3, 12):
        # https://github.com/KhronosGroup/glTF-Blender-IO/commits/8db37273b5d9819d8e0d964874d77ff3268537fa/
        from io_scene_gltf2.blender.exp.material import (  # type: ignore
            texture_info as gltf2_blender_gather_texture_info,
        )
    elif gltf_extension_common.glTF2_addon_ver >= (3, 5, 8):
        # https://github.com/KhronosGroup/glTF-Blender-IO/commits/5c52c313bcadb4703eb34ec6d5b51d1e47c60089/
        from io_scene_gltf2.blender.exp.material import (  # type: ignore
            gltf2_blender_gather_texture_info,
        )
    else:
        from io_scene_gltf2.blender.exp import (  # type: ignore
            gltf2_blender_gather_texture_info,
        )

    saved_use_nodes = blender_material.use_nodes
    nodes = None
    temp_node = None
    temp_shader_node = None
    try:
        blender_material.use_nodes = True

        node_tree = blender_material.node_tree

        # It seems that the node_tree can never be None (Blender 4.2.11)
        assert node_tree is not None

        nodes = node_tree.nodes

        temp_node = nodes.new("ShaderNodeTexImage")
        temp_shader_node = nodes.new("ShaderNodeBsdfDiffuse")
        assert isinstance(temp_node, bpy.types.ShaderNodeTexImage)
        assert isinstance(temp_shader_node, bpy.types.ShaderNodeBsdfDiffuse)
        node_tree.links.new(temp_shader_node.inputs[0], temp_node.outputs[0])
        temp_node.image = blender_image

        # Older versions of the gltf addon require passing in an input socket
        gltf_socket = temp_shader_node.inputs[0]

        if gltf_extension_common.glTF2_addon_ver >= (3, 3, 27):
            # https://github.com/KhronosGroup/glTF-Blender-IO/commits/c7e0b79bd73597da0783b36f2417e74db219716b/

            if gltf_extension_common.glTF2_addon_ver >= (4, 3, 12):
                # https://github.com/KhronosGroup/glTF-Blender-IO/commits/8db37273b5d9819d8e0d964874d77ff3268537fa/
                from io_scene_gltf2.blender.exp.material import (  # type: ignore
                    search_node_tree as gltf2_blender_search_node_tree,
                )
            else:
                from io_scene_gltf2.blender.exp.material import (  # type: ignore
                    gltf2_blender_search_node_tree,
                )

            gltf_socket = gltf2_blender_search_node_tree.NodeSocket(
                gltf_socket,
                [node_tree],
            )

        res = gltf2_blender_gather_texture_info.gather_texture_info(
            gltf_socket,
            (gltf_socket,),
            export_settings,
        )
        texture_info = res[0]
    finally:
        if nodes is not None and temp_node is not None:
            nodes.remove(temp_node)
        if nodes is not None and temp_shader_node is not None:
            nodes.remove(temp_shader_node)
        blender_material.use_nodes = saved_use_nodes

    return texture_info


class glTF2ExportUserExtension:

    def __init__(self):
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension  # type: ignore

        self.Extension = Extension
        scene = bpy.context.scene
        assert scene is not None
        self.properties = util.LIBDRAGON_RDPQ(scene).gltf_extension_export

    def gather_material_hook(
        self,
        gltf2_material: "io_scene_gltf2.io.com.gltf2_io.Material",  # type: ignore
        blender_material: bpy.types.Material,
        export_settings,
    ):
        scene = bpy.context.scene
        assert scene is not None
        if not util.LIBDRAGON_RDPQ(scene).gltf_extension_export.enabled:
            return
        jmat, mat_textures = mkmaterial_export.rdpq_material_properties_to_dict(
            util.LIBDRAGON_RDPQ(blender_material)
        )
        for i in (0, 1):
            if i in mat_textures:
                gathered_texture_info = export_standalone_image(
                    blender_material,
                    mat_textures[i],
                    export_settings,
                )

                # gathered_texture_info.index.source is a gltf2_io.Image
                # Later on in the gltf export process, it will be picked up by the gltf
                # exporter as "child of root" data and appended to the list of images
                # in the gltf output.  Additionally texN.source will be set to the
                # corresponding index in the images array.
                jmat[f"tex{i}.source"] = gathered_texture_info.index.source
        gltf2_material.extensions[gltf_extension_common.glTF_extension_name] = jmat


class glTFExtensionExportProperties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name="libdragon RDPQ materials",
        description="Include this extension in the exported glTF file.",
        default=True,
    )


def draw_gltf_extension_props(context: bpy.types.Context, layout: bpy.types.UILayout):
    layout.use_property_split = False
    scene = context.scene
    assert scene is not None
    layout.prop(util.LIBDRAGON_RDPQ(scene).gltf_extension_export, "enabled")
