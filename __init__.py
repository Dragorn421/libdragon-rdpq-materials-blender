bl_info = {
    "name": "libdragon RDPQ materials",
    "version": (0, 0, 1),
    "author": "Dragorn421",
    "location": "Material Properties",
    "description": "RDPQ materials for the libdragon N64 homebrew SDK",
    "category": "Material",
    "blender": (3, 2, 0),
}

# bl_info docs:
# https://projects.blender.org/blender/blender-developer-docs/src/commit/69734d611d9c90fe51146e76b10b0f36bbcb7214/docs/handbook/addons/addon_meta_info.md

import bpy
import bpy.utils

from . import gltf_extension_common
from . import gltf_extension_export
from . import gltf_extension_import
from . import mkmaterial_export
from .renderer import renderer
from . import rdpq_material_props
from . import rdpq_world_defaults
from . import sync_to_fast64
from . import util

# import glTF2{Export,Import}UserExtension into __init__.py
# to make the extension visible to the glTF addon
from .gltf_extension_export import glTF2ExportUserExtension
from .gltf_extension_import import glTF2ImportUserExtension

if gltf_extension_common.gltf_export_props_use_register_panel:
    from .gltf_extension_common import register_panel
if gltf_extension_common.gltf_export_props_use_draw:
    from .gltf_extension_common import draw
if gltf_extension_common.gltf_export_props_use_importer_draw_import:
    from .gltf_extension_import import draw_import


import importlib

loc = locals()
for n in (
    "gltf_extension_common",
    "gltf_extension_export",
    "gltf_extension_import",
    "mkmaterial_export",
    "mkmaterial_import",
    "rdpq_material_props",
    "rdpq_material_props_logic",
    "sync_to_fast64",
    "util",
):
    if n in loc:
        importlib.reload(loc[n])
    else:
        importlib.import_module(".%s" % n, __package__)


class RDPQWorldProperties(bpy.types.PropertyGroup):
    defaults_: bpy.props.PointerProperty(
        type=rdpq_world_defaults.RDPQWorldDefaultsProperties
    )

    @property
    def defaults(self) -> rdpq_world_defaults.RDPQWorldDefaultsProperties:
        return self.defaults_


class UsePropSplit:
    def __init__(self, layout: bpy.types.UILayout):
        self.layout = layout

    def __enter__(self):
        self.layout.use_property_split = True
        self.layout.use_property_decorate = False

    def __exit__(self, exc_type, exc, tb):
        self.layout.use_property_split = False


def prop_split(layout: bpy.types.UILayout, data, prop_name: str):
    with UsePropSplit(layout):
        layout.prop(data, prop_name)


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
        world_rdpq = util.LIBDRAGON_RDPQ(world)
        wdcr = world_rdpq.defaults.combiner.registers
        wdbr = world_rdpq.defaults.blender.registers
        wdrm = world_rdpq.defaults.render_mode

        layout.prop(wdcr, "k4")
        layout.prop(wdcr, "k5")
        layout.prop(wdcr, "prim_lod_frac")
        layout.prop(wdcr, "env")
        layout.prop(wdcr, "prim")

        layout.prop(wdbr, "blend_color_rgb")
        layout.prop(wdbr, "fog_color_rgb")
        layout.prop(wdbr, "fog_color_alpha")

        layout.prop(wdrm, "antialias")
        layout.prop(wdrm, "fog")
        layout.prop(wdrm, "dithering")
        layout.prop(wdrm, "texture_filtering")
        layout.prop(wdrm, "texture_perspective_correction")

        row = layout.row()
        row.prop(wdrm, "alpha_compare", text="")
        col = row.column()
        col.prop(wdrm, "alpha_compare_threshold")
        col.enabled = wdrm.alpha_compare

        layout.prop(wdrm, "z_compare")
        layout.prop(wdrm, "z_update")

        row = layout.row()
        row.prop(wdrm, "fixed_z")
        col = row.column()
        col.prop(wdrm, "fixed_z_value")
        col.prop(wdrm, "fixed_z_deltaz")
        col.enabled = wdrm.fixed_z

        box = layout.box()
        box.label(text="Placeholders")
        set_placeholders: set[int] = set()
        for i, placeholder in enumerate(world_rdpq.defaults.placeholders):
            split = box.row().split(factor=0.3)
            split.prop(placeholder, "slot_index")
            row = split.row()
            if placeholder.slot_index in set_placeholders:
                row.label(text="Duplicate slot")
            else:
                set_placeholders.add(placeholder.slot_index)
                row.prop(placeholder, "image")
            row.operator(
                rdpq_world_defaults.RDPQWorldDefaultsPlaceholderRemoveOperator.bl_idname,
                text="",
                icon="REMOVE",
            ).index = i
        box.operator(
            rdpq_world_defaults.RDPQWorldDefaultsPlaceholderAddOperator.bl_idname,
            text="Add Placeholder",
            icon="ADD",
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
        mat_rdpq = util.LIBDRAGON_RDPQ(mat)

        if sync_to_fast64.is_fast64_available():
            if sync_to_fast64.is_fast64_material(mat):
                if mat_rdpq.auto_sync_to_fast64:
                    layout.prop(mat_rdpq, "auto_sync_to_fast64")
                else:
                    row = layout.row()
                    if context.scene is None:
                        col = row.column()
                        col.prop(mat_rdpq, "auto_sync_to_fast64")
                        col.enabled = False
                    else:
                        row.prop(mat_rdpq, "auto_sync_to_fast64")
                    row.operator(
                        sync_to_fast64.RDPQMaterialPropsToFast64Operator.bl_idname,
                        text="Sync to Fast64 props",
                    )
            else:
                layout.operator(
                    sync_to_fast64.RDPQMaterialRecreateAsFast64Operator.bl_idname,
                    text="Recreate as Fast64 material",
                )

        def prop_texture(
            box: bpy.types.UILayout,
            texture_props: rdpq_material_props.RDPQMaterialTextureProperties,
        ):
            row = box.row()
            row.prop(texture_props, "use_placeholder", text="")
            col = row.column()
            col.prop(texture_props, "placeholder")
            col.enabled = texture_props.use_placeholder

            if not texture_props.use_placeholder:
                box.template_ID(
                    texture_props, "image", new="image.new", open="image.open"
                )
                prop_split(box, texture_props, "format")
                prop_split(box, texture_props, "mipmap")
                prop_split(box, texture_props, "dithering")

            # TODO do libdragon placeholders also contain ST information?
            # aka should ST props only be drawn if not a placeholder?

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

        def prop_combiner_register(set_prop, prop):
            row = box.row()
            row.prop(mat_rdpq.combiner.registers, set_prop, text="")
            col = row.column()
            col.prop(mat_rdpq.combiner.registers, prop)
            col.enabled = getattr(mat_rdpq.combiner.registers, set_prop)

        prop_combiner_register("set_k4", "k4")
        prop_combiner_register("set_k5", "k5")
        prop_combiner_register("set_prim_lod_frac", "prim_lod_frac")
        prop_combiner_register("set_env", "env")
        prop_combiner_register("set_prim", "prim")

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
        if mat_rdpq.blender.preset == "MULTIPLY_CONST":
            with UsePropSplit(box):
                box.prop(mat_rdpq.blender.registers, "fog_color_alpha", text="Const")

        def prop_blender_register(set_prop, prop):
            row = box.row()
            row.prop(mat_rdpq.blender.registers, set_prop, text="")
            col = row.column()
            col.prop(mat_rdpq.blender.registers, prop)
            col.enabled = getattr(mat_rdpq.blender.registers, set_prop)

        prop_blender_register("set_blend_color_rgb", "blend_color_rgb")
        prop_blender_register("set_fog_color_rgb", "fog_color_rgb")
        if mat_rdpq.blender.preset != "MULTIPLY_CONST":
            prop_blender_register("set_fog_color_alpha", "fog_color_alpha")

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
        prop_override("override_z_compare_and_z_update", "z_compare", "z_update")
        prop_override("override_fixed_z", "fixed_z", "fixed_z_deltaz")


class RDPQSceneProperties(bpy.types.PropertyGroup):
    gltf_extension_export: bpy.props.PointerProperty(
        type=gltf_extension_export.glTFExtensionExportProperties
    )
    gltf_extension_import: bpy.props.PointerProperty(
        type=gltf_extension_import.glTFExtensionImportProperties
    )


classes = (
    gltf_extension_export.glTFExtensionExportProperties,
    gltf_extension_import.glTFExtensionImportProperties,
    RDPQSceneProperties,
    rdpq_world_defaults.RDPQWorldDefaultsPlaceholderProperties,
    rdpq_world_defaults.RDPQWorldDefaultsCombinerRegistersProperties,
    rdpq_world_defaults.RDPQWorldDefaultsCombinerProperties,
    rdpq_world_defaults.RDPQWorldDefaultsBlenderRegistersProperties,
    rdpq_world_defaults.RDPQWorldDefaultsBlenderProperties,
    rdpq_world_defaults.RDPQWorldDefaultsRenderModeProperties,
    rdpq_world_defaults.RDPQWorldDefaultsProperties,
    RDPQWorldProperties,
    rdpq_material_props.RDPQMaterialTextureAxisProperties,
    rdpq_material_props.RDPQMaterialTextureProperties,
    rdpq_material_props.RDPQMaterialCombinerRegistersProperties,
    rdpq_material_props.RDPQMaterialCombinerProperties,
    rdpq_material_props.RDPQMaterialBlenderRegistersProperties,
    rdpq_material_props.RDPQMaterialBlenderProperties,
    rdpq_material_props.RDPQMaterialOverrideRenderModeProperties,
    rdpq_material_props.RDPQMaterialProperties,
    sync_to_fast64.RDPQMaterialPropsToFast64Operator,
    sync_to_fast64.RDPQMaterialRecreateAsFast64Operator,
    mkmaterial_export.RDPQMaterialExportOperator,
    rdpq_world_defaults.RDPQWorldDefaultsPlaceholderAddOperator,
    rdpq_world_defaults.RDPQWorldDefaultsPlaceholderRemoveOperator,
    RDPQWorldPanel,
    RDPQMaterialPanel,
    renderer.RDPQMaterialsRenderEngine,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.libdragon_rdpq = (  # type: ignore
        bpy.props.PointerProperty(type=RDPQSceneProperties)
    )
    bpy.types.Material.libdragon_rdpq = (  # type: ignore
        bpy.props.PointerProperty(type=rdpq_material_props.RDPQMaterialProperties)
    )
    bpy.types.World.libdragon_rdpq = (  # type: ignore
        bpy.props.PointerProperty(type=RDPQWorldProperties)
    )
    bpy.app.handlers.load_post.append(
        sync_to_fast64.handler_load_post_start_materials_auto_sync_to_fast64
    )
    bpy.app.timers.register(
        lambda: sync_to_fast64.handler_load_post_start_materials_auto_sync_to_fast64()
    )

    if gltf_extension_common.gltf_export_props_use_exporter_extension_layout_draw:
        from io_scene_gltf2 import exporter_extension_layout_draw  # type: ignore

        exporter_extension_layout_draw["libdragon RDPQ materials"] = (
            gltf_extension_export.draw_gltf_extension_props
        )

    for panel in renderer.get_compatible_panels():
        panel.COMPAT_ENGINES.add(renderer.RDPQMaterialsRenderEngine.bl_idname)


def unregister():
    for panel in renderer.get_compatible_panels():
        if renderer.RDPQMaterialsRenderEngine.bl_idname in panel.COMPAT_ENGINES:
            panel.COMPAT_ENGINES.remove(renderer.RDPQMaterialsRenderEngine.bl_idname)

    if gltf_extension_common.gltf_export_props_use_exporter_extension_layout_draw:
        from io_scene_gltf2 import exporter_extension_layout_draw  # type: ignore

        del exporter_extension_layout_draw["libdragon RDPQ materials"]

    try:
        bpy.app.handlers.load_post.remove(
            sync_to_fast64.handler_load_post_start_materials_auto_sync_to_fast64
        )
    except ValueError:
        pass
    del bpy.types.Scene.libdragon_rdpq  # type: ignore
    del bpy.types.Material.libdragon_rdpq  # type: ignore
    del bpy.types.World.libdragon_rdpq  # type: ignore
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
