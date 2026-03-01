import bpy

from . import export_to_mkmaterial
from . import util


# https://github.com/KhronosGroup/glTF-Blender-IO/blob/main/example-addons/example_gltf_exporter_extension

glTF_extension_name = "EXT_libdragon_rdpq_materials_jmat"


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

    # glTF addon 4.2.83
    from io_scene_gltf2.blender.exp.material import (  # type: ignore
        gltf2_blender_gather_texture_info,
        gltf2_blender_search_node_tree,
    )

    saved_use_nodes = blender_material.use_nodes
    nodes = None
    temp_node = None
    try:
        blender_material.use_nodes = True

        # It seems that the node_tree can never be None (Blender 4.2.11)
        assert blender_material.node_tree is not None

        nodes = blender_material.node_tree.nodes

        temp_node = nodes.new("ShaderNodeTexImage")
        assert isinstance(temp_node, bpy.types.ShaderNodeTexImage)
        temp_node.image = blender_image

        gltf_socket = gltf2_blender_search_node_tree.NodeSocket(
            temp_node.outputs[0],
            [blender_material.node_tree],
        )
        texture_info, _, _, _ = gltf2_blender_gather_texture_info.gather_texture_info(
            gltf_socket,
            (gltf_socket,),
            export_settings,
        )
    finally:
        if nodes is not None and temp_node is not None:
            nodes.remove(temp_node)
        blender_material.use_nodes = saved_use_nodes

    return texture_info


class glTF2ExportUserExtension:

    def __init__(self):
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension  # type: ignore

        self.Extension = Extension
        scene = bpy.context.scene
        assert scene is not None
        self.properties = util.LIBDRAGON_RDPQ(scene).gltf_extension

    def gather_material_hook(
        self,
        gltf2_material: "io_scene_gltf2.io.com.gltf2_io.Material",  # type: ignore
        blender_material: bpy.types.Material,
        export_settings,
    ):
        jmat = export_to_mkmaterial.rdpq_material_properties_to_dict(
            util.LIBDRAGON_RDPQ(blender_material)
        )
        textures_workaround_data = {}
        for i in (0, 1):
            if f"tex{i}.name" in jmat:
                gathered_texture_info = export_standalone_image(
                    blender_material,
                    bpy.data.images[jmat[f"tex{i}.name"]],
                    export_settings,
                )

                # I can't reproduce it but I had glTF rename the images once.
                # In general this should just be the same name as the blender image / tex{i}.name
                jmat[f"tex{i}.name"] = gathered_texture_info.index.source.name

                # So that the gltf addon will actually export the texture
                textures_workaround_data[f"tex{i}.texture"] = gathered_texture_info
        gltf2_material.extensions[glTF_extension_name] = jmat
        if textures_workaround_data:
            gltf2_material.extensions[glTF_extension_name + "_textures_workaround"] = (
                textures_workaround_data
            )


class glTFExtensionProperties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name="libdragon RDPQ materials",
        description="Include this extension in the exported glTF file.",
        default=True,
    )


def draw_gltf_extension_props(context: bpy.types.Context, layout: bpy.types.UILayout):
    layout.use_property_split = False
    scene = context.scene
    assert scene is not None
    layout.prop(util.LIBDRAGON_RDPQ(scene).gltf_extension, "enabled")
