import bpy

from . import util


class RDPQWorldDefaultsPlaceholderProperties(bpy.types.PropertyGroup):
    slot_index: bpy.props.IntProperty(
        name="Slot",
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


class RDPQWorldDefaultsCombinerRegistersProperties(bpy.types.PropertyGroup):
    k4: bpy.props.FloatProperty(name="K4", min=0, max=1)
    k5: bpy.props.FloatProperty(name="K5", min=0, max=1)
    # TODO keyscale, keycenter
    prim_lod_frac: bpy.props.FloatProperty(
        name="Prim LOD Frac",
        description="Primitive LOD fraction",
        min=0,
        max=1,
    )
    env: bpy.props.FloatVectorProperty(
        name="Env",
        description="Environment color",
        default=(1, 1, 1, 1),
        min=0,
        max=1,
        subtype="COLOR",
        size=4,
    )
    prim: bpy.props.FloatVectorProperty(
        name="Prim",
        description="Primitive color",
        default=(1, 1, 1, 1),
        min=0,
        max=1,
        subtype="COLOR",
        size=4,
    )


class RDPQWorldDefaultsCombinerProperties(bpy.types.PropertyGroup):
    registers_: bpy.props.PointerProperty(
        type=RDPQWorldDefaultsCombinerRegistersProperties
    )

    @property
    def registers(self) -> RDPQWorldDefaultsCombinerRegistersProperties:
        return self.registers_


class RDPQWorldDefaultsRenderModeProperties(bpy.types.PropertyGroup):
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


class RDPQWorldDefaultsProperties(bpy.types.PropertyGroup):
    placeholders: bpy.props.CollectionProperty(
        type=RDPQWorldDefaultsPlaceholderProperties,
    )

    combiner_: bpy.props.PointerProperty(type=RDPQWorldDefaultsCombinerProperties)
    render_mode_: bpy.props.PointerProperty(type=RDPQWorldDefaultsRenderModeProperties)

    @property
    def combiner(self) -> RDPQWorldDefaultsCombinerProperties:
        return self.combiner_

    @property
    def render_mode(self) -> RDPQWorldDefaultsRenderModeProperties:
        return self.render_mode_


class RDPQWorldDefaultsPlaceholderAddOperator(bpy.types.Operator):
    bl_idname = "libdragon_rdpq.rdpq_world_defaults_placeholder_add"
    bl_label = "Add placeholder to RDPQ world defaults"

    @classmethod
    def poll(cls, context):
        return hasattr(context, "world") and context.world is not None

    def execute(self, context):  # type: ignore
        world = context.world
        assert world is not None
        world_rdpq = util.LIBDRAGON_RDPQ(world)

        world_rdpq.defaults.placeholders.add()

        return {"FINISHED"}


class RDPQWorldDefaultsPlaceholderRemoveOperator(bpy.types.Operator):
    bl_idname = "libdragon_rdpq.rdpq_world_defaults_placeholder_remove"
    bl_label = "Remove placeholder from RDPQ world defaults"

    index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return hasattr(context, "world") and context.world is not None

    def execute(self, context):  # type: ignore
        world = context.world
        assert world is not None
        world_rdpq = util.LIBDRAGON_RDPQ(world)

        world_rdpq.defaults.placeholders.remove(self.index)

        return {"FINISHED"}


class WORLD_RDPQ_DEFAULTS_DEFAULTS_type:
    placeholders = []

    class combiner:
        class registers:
            k4 = 0
            k5 = 0
            prim_lod_frac = 0
            env = (1, 1, 1, 1)
            prim = (1, 1, 1, 1)

    class render_mode:
        antialias = "STANDARD"
        fog = "STANDARD"
        dithering = "RGB_SQUARE_A_SQUARE"
        texture_filtering = "BILINEAR"
        texture_perspective_correction = True
        alpha_compare = False
        alpha_compare_threshold = 127
        z_compare = True
        z_update = True
        fixed_z = False
        fixed_z_value = 0
        fixed_z_deltaz = 0


WORLD_RDPQ_DEFAULTS_DEFAULTS = WORLD_RDPQ_DEFAULTS_DEFAULTS_type()
