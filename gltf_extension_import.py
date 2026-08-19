import bpy

from . import gltf_extension_common
from . import util

if gltf_extension_common.gltf_export_props_use_register_panel:

    class GLTF_PT_RDPQImportPanel(bpy.types.Panel):

        bl_space_type = "FILE_BROWSER"
        bl_region_type = "TOOL_PROPS"
        bl_label = "libdragon RDPQ materials"
        bl_parent_id = "GLTF_PT_import_user_extensions"
        bl_options = {"DEFAULT_CLOSED"}

        @classmethod
        def poll(cls, context):
            sfile = context.space_data
            assert isinstance(sfile, bpy.types.SpaceFileBrowser)
            operator = sfile.active_operator
            assert operator is not None
            return operator.bl_idname == "IMPORT_SCENE_OT_gltf"

        def draw(self, context):
            assert self.layout is not None
            draw_import(context, self.layout)


def create_blender_image(gltf, image_index):
    assert gltf_extension_common.glTF2_addon_ver is not None

    if gltf_extension_common.glTF2_addon_ver >= (4, 3, 12):
        # https://github.com/KhronosGroup/glTF-Blender-IO/commits/8db37273b5d9819d8e0d964874d77ff3268537fa/
        from io_scene_gltf2.blender.imp.image import BlenderImage  # type: ignore
    else:
        from io_scene_gltf2.blender.imp.gltf2_blender_image import BlenderImage  # type: ignore

    BlenderImage.create(gltf, image_index)


class glTF2ImportUserExtension:

    def __init__(self):
        scene = bpy.context.scene
        assert scene is not None
        self.properties = util.LIBDRAGON_RDPQ(scene).gltf_extension_import

    def gather_import_material_after_hook(
        self,
        gltf_material,
        vertex_color,
        blender_mat: bpy.types.Material,
        gltf,
    ):
        scene = bpy.context.scene
        assert scene is not None
        if not util.LIBDRAGON_RDPQ(scene).gltf_extension_import.enabled:
            return
        jmat = gltf_material.extensions.get(gltf_extension_common.glTF_extension_name)
        if jmat is None:
            return
        mat_rdpq = util.LIBDRAGON_RDPQ(blender_mat)
        image_index = jmat.get("tex0.source")
        if image_index is not None:
            gltf_image = gltf.data.images[image_index]
            if gltf_image.blender_image_name is None:
                create_blender_image(gltf, image_index)
            assert isinstance(gltf_image.blender_image_name, str)
            blender_image = bpy.data.images[gltf_image.blender_image_name]
            mat_rdpq.texture0.image = blender_image
            mat_rdpq.texture0.s.repeats_inf = True
            mat_rdpq.texture0.t.repeats_inf = True


class glTFExtensionImportProperties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name="libdragon RDPQ materials",
        description="Use this extension from the imported glTF file.",
        default=True,
    )


def draw_import(context: bpy.types.Context, layout: bpy.types.UILayout):
    layout.use_property_split = False
    scene = context.scene
    assert scene is not None
    layout.prop(util.LIBDRAGON_RDPQ(scene).gltf_extension_import, "enabled")
