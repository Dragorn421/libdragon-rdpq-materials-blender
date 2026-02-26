import bpy

from . import export_to_mkmaterial
from . import util


# https://github.com/KhronosGroup/glTF-Blender-IO/blob/main/example-addons/example_gltf_exporter_extension

glTF_extension_name = "EXT_libdragon_rdpq_materials_jmat"


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
        gltf2_material.extensions[glTF_extension_name] = (
            export_to_mkmaterial.rdpq_material_properties_to_dict(
                util.LIBDRAGON_RDPQ(blender_material)
            )
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
