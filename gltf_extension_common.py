import bpy
import addon_utils

glTF_extension_name = "EXT_libdragon_rdpq_materials_jmat"

glTF2_addon_ver = None

for mod in addon_utils.modules():  # type: ignore
    if mod.__name__ == "io_scene_gltf2":
        glTF2_addon_ver = mod.bl_info["version"]
        break


# from io_scene_gltf2 import exporter_extension_layout_draw
# https://github.com/KhronosGroup/glTF-Blender-IO/commits/49b56804049c4724c89f6be49ea8382c0b63f9da/
gltf_export_props_use_exporter_extension_layout_draw = (
    glTF2_addon_ver is not None and glTF2_addon_ver >= (4, 4, 36)
)
# from io_scene_gltf2 import exporter_extension_layout_draw
# https://github.com/KhronosGroup/glTF-Blender-IO/commits/49b56804049c4724c89f6be49ea8382c0b63f9da/
gltf_export_props_use_importer_draw_import = (
    glTF2_addon_ver is not None and glTF2_addon_ver >= (4, 3, 13)
)
# def draw()
# https://github.com/KhronosGroup/glTF-Blender-IO/commits/fae512b1981493794ccafb4b187f9ada3c5d3b1f/
gltf_export_props_use_draw = (
    glTF2_addon_ver is not None
    and glTF2_addon_ver < (4, 4, 36)
    and glTF2_addon_ver >= (4, 2, 40)
)
# def register_panel()
gltf_export_props_use_register_panel = (
    glTF2_addon_ver is not None and glTF2_addon_ver < (4, 2, 40)
)

# Used by old versions of the gltf addon

if gltf_export_props_use_draw:

    def draw(context: bpy.types.Context, layout):
        from . import gltf_extension_export
        from . import gltf_extension_import

        if not isinstance(context.space_data, bpy.types.SpaceFileBrowser):
            return
        if context.space_data.active_operator is None:
            return
        if context.space_data.active_operator.bl_idname == "EXPORT_SCENE_OT_gltf":
            gltf_extension_export.draw_gltf_extension_props(context, layout)
        if context.space_data.active_operator.bl_idname == "IMPORT_SCENE_OT_gltf":
            gltf_extension_import.draw_import(context, layout)


if gltf_export_props_use_register_panel:

    # https://github.com/KhronosGroup/glTF-Blender-IO/blob/3ade756cba3d9631b77cf002462b4315562e1869/example-addons/example_gltf_exporter_extension/__init__.py#L43
    def register_panel():
        from . import gltf_extension_export
        from . import gltf_extension_import

        for cls in (
            gltf_extension_export.GLTF_PT_RDPQPanel,
            gltf_extension_import.GLTF_PT_RDPQImportPanel,
        ):
            try:
                bpy.utils.register_class(cls)
            except Exception:
                pass
        return unregister_panel

    def unregister_panel():
        from . import gltf_extension_export
        from . import gltf_extension_import

        for cls in (
            gltf_extension_export.GLTF_PT_RDPQPanel,
            gltf_extension_import.GLTF_PT_RDPQImportPanel,
        ):
            try:
                bpy.utils.unregister_class(cls)
            except Exception:
                pass
