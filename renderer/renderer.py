import dataclasses
import enum
from pathlib import Path
import struct
from typing import Optional, Sequence, TYPE_CHECKING, Union

import bpy
import mathutils

if TYPE_CHECKING:
    import gpu

import numpy as np

from .. import rdpq_material_props
from .. import rdpq_world_defaults
from .. import util
from . import magic


@dataclasses.dataclass
class MaterialDataTexAxis:
    dim: int
    translate: float
    scale: int
    repeats_inf: bool
    repeats: float
    mirror: bool


@dataclasses.dataclass
class MaterialDataTex:
    image: bpy.types.Image
    s: MaterialDataTexAxis
    t: MaterialDataTexAxis


class MaterialDataBlendMode(enum.Enum):
    NONE = enum.auto()
    ALPHA = enum.auto()
    ADDITIVE = enum.auto()


@dataclasses.dataclass
class MaterialData:
    tex0: Optional[MaterialDataTex]
    tex1: Optional[MaterialDataTex]
    combiner_words: Sequence[int]
    combiner_reg_k4: float
    combiner_reg_k5: float
    combiner_reg_prim_lod_frac: float
    combiner_reg_env: tuple[float, float, float, float]
    combiner_reg_prim: tuple[float, float, float, float]
    blend_mode: MaterialDataBlendMode
    alpha_compare_threshold: Optional[float]
    z_compare: bool
    z_update: bool


@dataclasses.dataclass
class MeshData:
    model_matrix: mathutils.Matrix
    loop_triangles_loops: np.ndarray
    loops_co: np.ndarray
    loops_normal: np.ndarray
    loops_color: np.ndarray
    loops_uv: Optional[np.ndarray]
    material: Optional[MaterialData]


@dataclasses.dataclass
class SceneData:
    meshes: list[MeshData] = dataclasses.field(default_factory=list)


COMBINER_MAP = {
    "0": magic.COMBINER_0,
    "1": magic.COMBINER_1,
    "ENV": magic.COMBINER_ENV,
    "ENV_ALPHA": magic.COMBINER_ENV_ALPHA,
    "K4": magic.COMBINER_K4,
    "K5": magic.COMBINER_K5,
    "KEYCENTER": magic.COMBINER_KEYCENTER,
    "KEYSCALE": magic.COMBINER_KEYSCALE,
    "LOD_FRAC": magic.COMBINER_LOD_FRAC,
    "NOISE": magic.COMBINER_NOISE,
    "PRIM": magic.COMBINER_PRIM,
    "PRIM_ALPHA": magic.COMBINER_PRIM_ALPHA,
    "PRIM_LOD_FRAC": magic.COMBINER_PRIM_LOD_FRAC,
    "SHADE": magic.COMBINER_SHADE,
    "SHADE_ALPHA": magic.COMBINER_SHADE_ALPHA,
    "TEX0": magic.COMBINER_TEX0,
    "TEX0_ALPHA": magic.COMBINER_TEX0_ALPHA,
    "TEX1": magic.COMBINER_TEX1,
    "TEX1_ALPHA": magic.COMBINER_TEX1_ALPHA,
    "COMBINED": magic.COMBINER_COMBINED,
    "COMBINED_ALPHA": magic.COMBINER_COMBINED_ALPHA,
}


def get_blend_mode(mat_rdpq: rdpq_material_props.RDPQMaterialProperties):
    # TODO for custom 1-pass and 2-passes, try to guess
    if mat_rdpq.blender.preset == "CUSTOM_1_PASS":
        return MaterialDataBlendMode.NONE
    elif mat_rdpq.blender.preset == "CUSTOM_2_PASSES":
        return MaterialDataBlendMode.NONE
    else:
        return {
            "NONE": MaterialDataBlendMode.NONE,
            "MULTIPLY": MaterialDataBlendMode.ALPHA,
            "MULTIPLY_CONST": MaterialDataBlendMode.ALPHA,
            "ADDITIVE": MaterialDataBlendMode.ADDITIVE,
        }[mat_rdpq.blender.preset]


def get_material_data(
    world_rdpq_defaults: Union[
        rdpq_world_defaults.RDPQWorldDefaultsProperties,
        rdpq_world_defaults.WORLD_RDPQ_DEFAULTS_DEFAULTS_type,
    ],
    mat: bpy.types.Material,
):
    mat_rdpq = util.LIBDRAGON_RDPQ(mat)

    def handle_texture_axis(
        texture_axis_props: rdpq_material_props.RDPQMaterialTextureAxisProperties,
        dim: int,
    ):
        return MaterialDataTexAxis(
            dim,
            texture_axis_props.translate,
            texture_axis_props.scale,
            texture_axis_props.repeats_inf,
            texture_axis_props.repeats,
            texture_axis_props.mirror,
        )

    def handle_texture(
        texture_props: rdpq_material_props.RDPQMaterialTextureProperties,
    ):
        if texture_props.use_placeholder:
            img = None
            for default_placeholder in world_rdpq_defaults.placeholders:
                if default_placeholder.slot_index == texture_props.placeholder:
                    img = default_placeholder.image
                    # TODO do libdragon placeholders also contain ST information?
                    break
        else:
            img = texture_props.image
        if img is None:
            return None
        s = handle_texture_axis(texture_props.s, img.size[0])
        t = handle_texture_axis(texture_props.t, img.size[1])
        return MaterialDataTex(img, s, t)

    if mat_rdpq.use_texture0:
        tex0 = handle_texture(mat_rdpq.texture0)
    else:
        tex0 = None
    if mat_rdpq.use_texture1:
        tex1 = handle_texture(mat_rdpq.texture1)
    else:
        tex1 = None
    combiner_words = [0, 0, 0, 0]
    for slot, shift, word in (
        (
            mat_rdpq.combiner.rgb_A_0,
            magic.COMBINER_RGB_2A_SUBA_SHIFT,
            magic.COMBINER_RGB_2A_SUBA_WORD,
        ),
        (
            mat_rdpq.combiner.rgb_B_0,
            magic.COMBINER_RGB_2A_SUBB_SHIFT,
            magic.COMBINER_RGB_2A_SUBB_WORD,
        ),
        (
            mat_rdpq.combiner.rgb_C_0,
            magic.COMBINER_RGB_2A_MUL_SHIFT,
            magic.COMBINER_RGB_2A_MUL_WORD,
        ),
        (
            mat_rdpq.combiner.rgb_D_0,
            magic.COMBINER_RGB_2A_ADD_SHIFT,
            magic.COMBINER_RGB_2A_ADD_WORD,
        ),
        (
            mat_rdpq.combiner.rgb_A_1,
            magic.COMBINER_RGB_2B_SUBA_SHIFT,
            magic.COMBINER_RGB_2B_SUBA_WORD,
        ),
        (
            mat_rdpq.combiner.rgb_B_1,
            magic.COMBINER_RGB_2B_SUBB_SHIFT,
            magic.COMBINER_RGB_2B_SUBB_WORD,
        ),
        (
            mat_rdpq.combiner.rgb_C_1,
            magic.COMBINER_RGB_2B_MUL_SHIFT,
            magic.COMBINER_RGB_2B_MUL_WORD,
        ),
        (
            mat_rdpq.combiner.rgb_D_1,
            magic.COMBINER_RGB_2B_ADD_SHIFT,
            magic.COMBINER_RGB_2B_ADD_WORD,
        ),
        (
            mat_rdpq.combiner.alpha_A_0,
            magic.COMBINER_A_2A_SUBA_SHIFT,
            magic.COMBINER_A_2A_SUBA_WORD,
        ),
        (
            mat_rdpq.combiner.alpha_B_0,
            magic.COMBINER_A_2A_SUBB_SHIFT,
            magic.COMBINER_A_2A_SUBB_WORD,
        ),
        (
            mat_rdpq.combiner.alpha_C_0,
            magic.COMBINER_A_2A_MUL_SHIFT,
            magic.COMBINER_A_2A_MUL_WORD,
        ),
        (
            mat_rdpq.combiner.alpha_D_0,
            magic.COMBINER_A_2A_ADD_SHIFT,
            magic.COMBINER_A_2A_ADD_WORD,
        ),
        (
            mat_rdpq.combiner.alpha_A_1,
            magic.COMBINER_A_2B_SUBA_SHIFT,
            magic.COMBINER_A_2B_SUBA_WORD,
        ),
        (
            mat_rdpq.combiner.alpha_B_1,
            magic.COMBINER_A_2B_SUBB_SHIFT,
            magic.COMBINER_A_2B_SUBB_WORD,
        ),
        (
            mat_rdpq.combiner.alpha_C_1,
            magic.COMBINER_A_2B_MUL_SHIFT,
            magic.COMBINER_A_2B_MUL_WORD,
        ),
        (
            mat_rdpq.combiner.alpha_D_1,
            magic.COMBINER_A_2B_ADD_SHIFT,
            magic.COMBINER_A_2B_ADD_WORD,
        ),
    ):
        combiner_words[word] |= COMBINER_MAP[slot] << shift
    combiner_reg_k4 = (
        mat_rdpq.combiner.registers.k4
        if mat_rdpq.combiner.registers.set_k4
        else world_rdpq_defaults.combiner.registers.k4
    )
    combiner_reg_k5 = (
        mat_rdpq.combiner.registers.k5
        if mat_rdpq.combiner.registers.set_k5
        else world_rdpq_defaults.combiner.registers.k5
    )
    combiner_reg_prim_lod_frac = (
        mat_rdpq.combiner.registers.prim_lod_frac
        if mat_rdpq.combiner.registers.set_prim_lod_frac
        else world_rdpq_defaults.combiner.registers.prim_lod_frac
    )
    combiner_reg_env = (
        mat_rdpq.combiner.registers.env
        if mat_rdpq.combiner.registers.set_env
        else world_rdpq_defaults.combiner.registers.env
    )
    combiner_reg_prim = (
        mat_rdpq.combiner.registers.prim
        if mat_rdpq.combiner.registers.set_prim
        else world_rdpq_defaults.combiner.registers.prim
    )
    blend_mode = get_blend_mode(mat_rdpq)
    if mat_rdpq.override_render_mode.override_alpha_compare:
        alpha_compare_threshold_int = (
            mat_rdpq.override_render_mode.alpha_compare_threshold
        )
        if alpha_compare_threshold_int == 0:
            alpha_compare_threshold_int = None
    else:
        if world_rdpq_defaults.render_mode.alpha_compare:
            alpha_compare_threshold_int = (
                world_rdpq_defaults.render_mode.alpha_compare_threshold
            )
            if alpha_compare_threshold_int == 0:
                alpha_compare_threshold_int = None
        else:
            alpha_compare_threshold_int = None
    if alpha_compare_threshold_int is not None:
        alpha_compare_threshold = alpha_compare_threshold_int / 255
    else:
        alpha_compare_threshold = None
    if mat_rdpq.override_render_mode.override_z_compare_and_z_update:
        z_compare = mat_rdpq.override_render_mode.z_compare
        z_update = mat_rdpq.override_render_mode.z_update
    else:
        z_compare = world_rdpq_defaults.render_mode.z_compare
        z_update = world_rdpq_defaults.render_mode.z_update
    mat_data = MaterialData(
        tex0,
        tex1,
        combiner_words,
        combiner_reg_k4,
        combiner_reg_k5,
        combiner_reg_prim_lod_frac,
        combiner_reg_env,
        combiner_reg_prim,
        blend_mode,
        alpha_compare_threshold,
        z_compare,
        z_update,
    )
    return mat_data


def get_mesh_data(
    world_rdpq_defaults: Union[
        rdpq_world_defaults.RDPQWorldDefaultsProperties,
        rdpq_world_defaults.WORLD_RDPQ_DEFAULTS_DEFAULTS_type,
    ],
    obj: bpy.types.Object,
    depsgraph: bpy.types.Depsgraph,
):
    meshes: list[MeshData] = []

    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.to_mesh()
    mesh.calc_loop_triangles()
    if bpy.app.version < (4, 1, 0):
        mesh.calc_normals_split()

    model_matrix = obj.matrix_world

    vertices_co = np.empty((len(mesh.vertices), 3), dtype=np.float32)
    mesh.vertices.foreach_get("co", vertices_co.ravel())

    loop_triangles_loops = np.empty((len(mesh.loop_triangles), 3), dtype=np.int32)
    mesh.loop_triangles.foreach_get("loops", loop_triangles_loops.ravel())

    loops_normal = np.empty((len(mesh.loops), 3), dtype=np.float32)
    mesh.loops.foreach_get("normal", loops_normal.ravel())

    loops_vertex_index = np.empty(len(mesh.loops), dtype=np.int32)
    mesh.loops.foreach_get("vertex_index", loops_vertex_index)

    active_color_attribute = mesh.color_attributes.active_color
    if active_color_attribute is None:
        loops_color = np.ones((len(mesh.loops), 4), dtype=np.float32)
    else:
        if active_color_attribute.data_type in {
            "FLOAT_COLOR",
            "BYTE_COLOR",
        }:
            assert isinstance(
                active_color_attribute,
                (
                    bpy.types.FloatColorAttribute,
                    bpy.types.ByteColorAttribute,
                ),
            )
            # Note: for ByteColorAttribute too the color uses floats
            if active_color_attribute.domain == "CORNER":
                loops_color = np.empty((len(mesh.loops), 4), dtype=np.float32)
                active_color_attribute.data.foreach_get("color", loops_color.ravel())
            elif active_color_attribute.domain == "POINT":
                vertices_color = np.empty((len(mesh.vertices), 4), dtype=np.float32)
                active_color_attribute.data.foreach_get("color", vertices_color.ravel())
                loops_color = vertices_color[loops_vertex_index, :]
            else:
                raise NotImplementedError(active_color_attribute.domain)
        else:
            raise NotImplementedError(active_color_attribute.data_type)

    active_uv_layer = mesh.uv_layers.active
    if active_uv_layer is None:
        loops_uv = None
    else:
        loops_uv = np.empty((len(mesh.loops), 2), dtype=np.float32)
        active_uv_layer.data.foreach_get("uv", loops_uv.ravel())

    loop_triangles_material_index = np.empty(len(mesh.loop_triangles), dtype=np.int32)
    mesh.loop_triangles.foreach_get(
        "material_index", loop_triangles_material_index.ravel()
    )

    polygons_hide = np.empty(len(mesh.polygons), np.bool_)
    mesh.polygons.foreach_get("hide", polygons_hide)

    loop_triangles_polygon_index = np.empty(len(mesh.loop_triangles), dtype=np.int32)
    mesh.loop_triangles.foreach_get("polygon_index", loop_triangles_polygon_index)

    loop_triangles_hide = polygons_hide[loop_triangles_polygon_index]

    loops_co = vertices_co[loops_vertex_index, :]

    if bpy.app.version < (4, 1, 0):
        mesh.free_normals_split()
    obj_eval.to_mesh_clear()

    mat_mask = np.empty_like(loop_triangles_material_index, dtype=bool)

    for mat_index in np.unique(loop_triangles_material_index):
        mat_index: int
        if mat_index < len(obj.material_slots):
            mat = obj.material_slots[mat_index].material
        else:
            mat = None

        if mat is not None:
            mat_data = get_material_data(world_rdpq_defaults, mat)
        else:
            mat_data = None

        # Get the loops indices for the triangles using mat
        np.equal(loop_triangles_material_index, mat_index, out=mat_mask)
        mat_mask[loop_triangles_hide] = False  # mask out hidden triangles
        mat_triangles_loops = loop_triangles_loops[mat_mask, :]

        if mat_triangles_loops.shape[0] == 0:
            continue

        # Get the loops used by the mat-using triangles,
        # for subsetting the coordinates/normal/color buffers,
        # and also the triangles loops indices in that subset of triangles.
        mat_used_loops, mat_triangles_loops_used_loops = np.unique(
            mat_triangles_loops, return_inverse=True
        )
        mat_triangles_loops_used_loops = mat_triangles_loops_used_loops.reshape(
            mat_triangles_loops.shape
        ).astype(np.int32)

        meshes.append(
            MeshData(
                model_matrix,
                mat_triangles_loops_used_loops,
                loops_co[mat_used_loops, :],
                loops_normal[mat_used_loops, :],
                loops_color[mat_used_loops, :],
                (loops_uv[mat_used_loops, :] if loops_uv is not None else None),
                mat_data,
            )
        )

    return meshes


def draw_mesh(
    mesh: MeshData,
    shader: "gpu.types.GPUShader",
    proj_view_mtx: mathutils.Matrix,
    view_mtx: mathutils.Matrix,
):
    import gpu
    import gpu_extras.batch

    valid_inputs_flags = 0

    if mesh.material is not None:
        mat = mesh.material
        if mat.tex0 is not None:
            valid_inputs_flags |= magic.VALID_IN_TEX0 | magic.VALID_IN_TEX0_ST
            shader.uniform_sampler("inTex0", gpu.texture.from_image(mat.tex0.image))
            tex0_s_dim = mat.tex0.s.dim
            tex0_s_translate = mat.tex0.s.translate
            tex0_s_scale = mat.tex0.s.scale
            tex0_s_repeats = mat.tex0.s.repeats
            tex0_s_flags = 0
            if mat.tex0.s.repeats_inf:
                tex0_s_flags |= magic.TEX_ST_FLAG_REPEATS_INF
            if mat.tex0.s.mirror:
                tex0_s_flags |= magic.TEX_ST_FLAG_MIRROR
            tex0_t_dim = mat.tex0.t.dim
            tex0_t_translate = mat.tex0.t.translate
            tex0_t_scale = mat.tex0.t.scale
            tex0_t_repeats = mat.tex0.t.repeats
            tex0_t_flags = 0
            if mat.tex0.t.repeats_inf:
                tex0_t_flags |= magic.TEX_ST_FLAG_REPEATS_INF
            if mat.tex0.t.mirror:
                tex0_t_flags |= magic.TEX_ST_FLAG_MIRROR
        else:
            tex0_s_dim = 0
            tex0_s_translate = 0
            tex0_s_scale = 0
            tex0_s_repeats = 0
            tex0_s_flags = 0
            tex0_t_dim = 0
            tex0_t_translate = 0
            tex0_t_scale = 0
            tex0_t_repeats = 0
            tex0_t_flags = 0
        if mat.tex1 is not None:
            valid_inputs_flags |= magic.VALID_IN_TEX1 | magic.VALID_IN_TEX1_ST
            shader.uniform_sampler("inTex1", gpu.texture.from_image(mat.tex1.image))
            tex1_s_dim = mat.tex1.s.dim
            tex1_s_translate = mat.tex1.s.translate
            tex1_s_scale = mat.tex1.s.scale
            tex1_s_repeats = mat.tex1.s.repeats
            tex1_s_flags = 0
            if mat.tex1.s.repeats_inf:
                tex1_s_flags |= magic.TEX_ST_FLAG_REPEATS_INF
            if mat.tex1.s.mirror:
                tex1_s_flags |= magic.TEX_ST_FLAG_MIRROR
            tex1_t_dim = mat.tex1.t.dim
            tex1_t_translate = mat.tex1.t.translate
            tex1_t_scale = mat.tex1.t.scale
            tex1_t_repeats = mat.tex1.t.repeats
            tex1_t_flags = 0
            if mat.tex1.t.repeats_inf:
                tex1_t_flags |= magic.TEX_ST_FLAG_REPEATS_INF
            if mat.tex1.t.mirror:
                tex1_t_flags |= magic.TEX_ST_FLAG_MIRROR
        else:
            tex1_s_dim = 0
            tex1_s_translate = 0
            tex1_s_scale = 0
            tex1_s_repeats = 0
            tex1_s_flags = 0
            tex1_t_dim = 0
            tex1_t_translate = 0
            tex1_t_scale = 0
            tex1_t_repeats = 0
            tex1_t_flags = 0
        valid_inputs_flags |= (
            magic.VALID_IN_COMBINER
            | magic.VALID_IN_COMBINER_REG_K4
            | magic.VALID_IN_COMBINER_REG_K5
            | magic.VALID_IN_COMBINER_REG_PRIM_LOD_FRAC
            | magic.VALID_IN_COMBINER_REG_ENV
            | magic.VALID_IN_COMBINER_REG_PRIM
        )
        combiner_words = mat.combiner_words
        combiner_reg_k4 = mat.combiner_reg_k4
        combiner_reg_k5 = mat.combiner_reg_k5
        combiner_reg_prim_lod_frac = mat.combiner_reg_prim_lod_frac
        combiner_reg_env = mat.combiner_reg_env
        combiner_reg_prim = mat.combiner_reg_prim
        blend_mode = {
            MaterialDataBlendMode.NONE: "NONE",
            MaterialDataBlendMode.ALPHA: "ALPHA",
            MaterialDataBlendMode.ADDITIVE: "ADDITIVE",
        }[mat.blend_mode]
        general_flags = 0
        alpha_compare_threshold = mat.alpha_compare_threshold
        if alpha_compare_threshold is not None:
            general_flags |= magic.GENERAL_FLAG_ALPHA_COMPARE
        else:
            alpha_compare_threshold = 0
        z_compare = mat.z_compare
        z_update = mat.z_update
    else:
        tex0_s_dim = 0
        tex0_s_translate = 0
        tex0_s_scale = 0
        tex0_s_repeats = 0
        tex0_s_flags = 0
        tex0_t_dim = 0
        tex0_t_translate = 0
        tex0_t_scale = 0
        tex0_t_repeats = 0
        tex0_t_flags = 0
        tex1_s_dim = 0
        tex1_s_translate = 0
        tex1_s_scale = 0
        tex1_s_repeats = 0
        tex1_s_flags = 0
        tex1_t_dim = 0
        tex1_t_translate = 0
        tex1_t_scale = 0
        tex1_t_repeats = 0
        tex1_t_flags = 0
        combiner_words = (0, 0, 0, 0)
        combiner_reg_k4 = 0
        combiner_reg_k5 = 0
        combiner_reg_prim_lod_frac = 0
        combiner_reg_env = (1, 1, 1, 1)
        combiner_reg_prim = (1, 1, 1, 1)
        blend_mode = "NONE"
        alpha_compare_threshold = 0
        general_flags = 0
        z_compare = True
        z_update = True

    content = {
        "inPos": mesh.loops_co,
        "inNormal": mesh.loops_normal,
        "inColor": mesh.loops_color,
    }

    if mesh.loops_uv is not None:
        valid_inputs_flags |= magic.VALID_IN_UV
        content["inUV"] = mesh.loops_uv

    data = struct.pack(
        (
            "16f"  # matMVP
            "16f"  # matMV
            "4i"  # combiner
            "4f"  # combinerRegEnv
            "4f"  # combinerRegPrim
            "f"  # combinerRegK4
            "f"  # combinerRegK5
            "f"  # combinerRegPrimLODFrac
            "i"  # tex0SDim
            "f"  # tex0STranslate
            "i"  # tex0SScale
            "f"  # tex0SRepeats
            "i"  # tex0SFlags
            "i"  # tex0TDim
            "f"  # tex0TTranslate
            "i"  # tex0TScale
            "f"  # tex0TRepeats
            "i"  # tex0TFlags
            "i"  # tex1SDim
            "f"  # tex1STranslate
            "i"  # tex1SScale
            "f"  # tex1SRepeats
            "i"  # tex1SFlags
            "i"  # tex1TDim
            "f"  # tex1TTranslate
            "i"  # tex1TScale
            "f"  # tex1TRepeats
            "i"  # tex1TFlags
            "f"  # alphaCompareThreshold
            "i"  # generalFlags
            "i"  # validInputs
            "8x"
        ),
        *np.array(proj_view_mtx @ mesh.model_matrix).T.ravel(),
        *np.array(view_mtx @ mesh.model_matrix).T.ravel(),
        *combiner_words,
        *combiner_reg_env,
        *combiner_reg_prim,
        combiner_reg_k4,
        combiner_reg_k5,
        combiner_reg_prim_lod_frac,
        tex0_s_dim,
        tex0_s_translate,
        tex0_s_scale,
        tex0_s_repeats,
        tex0_s_flags,
        tex0_t_dim,
        tex0_t_translate,
        tex0_t_scale,
        tex0_t_repeats,
        tex0_t_flags,
        tex1_s_dim,
        tex1_s_translate,
        tex1_s_scale,
        tex1_s_repeats,
        tex1_s_flags,
        tex1_t_dim,
        tex1_t_translate,
        tex1_t_scale,
        tex1_t_repeats,
        tex1_t_flags,
        alpha_compare_threshold,
        general_flags,
        valid_inputs_flags,
    )
    ubo = gpu.types.GPUUniformBuf(data)
    shader.uniform_block("inState", ubo)

    batch: gpu.types.GPUBatch = gpu_extras.batch.batch_for_shader(
        shader,
        "TRIS",
        content,
        indices=mesh.loop_triangles_loops,
    )
    gpu.state.blend_set(blend_mode)
    gpu.state.depth_test_set("LESS_EQUAL" if z_compare else "NONE")
    gpu.state.depth_mask_set(z_update)
    # TODO add backface culling option
    gpu.state.face_culling_set("NONE")
    batch.draw(shader)


class RDPQMaterialsRenderEngine(bpy.types.RenderEngine):
    bl_idname = "LIBDRAGON_RDPQ_MATERIALS"
    bl_label = "libdragon RDPQ materials"
    bl_use_preview = True
    bl_use_gpu_context = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_data = SceneData()
        self.shader = None

    def render(self, depsgraph: bpy.types.Depsgraph):
        if not self.is_preview:
            return

        scene = depsgraph.scene
        assert scene is not None

        if scene.world is not None:
            world_rdpq_defaults = util.LIBDRAGON_RDPQ(scene.world).defaults
        else:
            world_rdpq_defaults = rdpq_world_defaults.WORLD_RDPQ_DEFAULTS_DEFAULTS

        scale = scene.render.resolution_percentage / 100
        width = int(scene.render.resolution_x * scale)
        height = int(scene.render.resolution_y * scale)

        # For preview renders, Blender passes in a mock scene with a bunch of mesh
        # objects and other stuff. We find the material being previewed by looking in
        # one of those mesh objects.
        obj = scene.objects.get("preview_flat")
        if obj is None:
            print(
                "[RDPQMaterialsRenderEngine] "
                "did not find preview_flat object in the mock scene"
            )
            return

        mat = obj.material_slots[obj.data.polygons[0].material_index].material
        if mat is None:
            print(
                "[RDPQMaterialsRenderEngine] "
                "did not find material on the preview_flat object in the mock scene"
            )
            return

        import gpu

        offscreen = gpu.types.GPUOffScreen(width, height, format="RGBA8")

        self.init_shader()
        assert self.shader is not None

        with offscreen.bind():
            gpu.state.viewport_set(0, 0, width, height)

            gpu.matrix.load_matrix(mathutils.Matrix.Identity(4))
            gpu.matrix.load_projection_matrix(mathutils.Matrix.Identity(4))

            fb = gpu.state.active_framebuffer_get()
            fb: gpu.types.GPUFrameBuffer
            fb.clear(color=(0.1, 0.1, 0.1, 1), depth=1)

            mat_data = get_material_data(world_rdpq_defaults, mat)

            # Draw a full-viewport plane
            # y ^
            #   |
            #   +--> x
            #
            #   0--3
            #   |  |
            #   1--2
            draw_mesh(
                MeshData(
                    mathutils.Matrix.Identity(4),
                    np.array(
                        ((0, 1, 3), (3, 1, 2)),
                        dtype=np.int32,
                    ),
                    np.array(
                        ((-1, 1, 0), (-1, -1, 0), (1, -1, 0), (1, 1, 0)),
                        dtype=np.float32,
                    ),
                    np.array(
                        ((0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1)),
                        dtype=np.float32,
                    ),
                    np.array(
                        ((1, 1, 1, 1), (1, 1, 1, 1), (1, 1, 1, 1), (1, 1, 1, 1)),
                        dtype=np.float32,
                    ),
                    np.array(
                        ((0, 1), (0, 0), (1, 0), (1, 1)),
                        dtype=np.float32,
                    ),
                    mat_data,
                ),
                self.shader,
                mathutils.Matrix.Identity(4),
                mathutils.Matrix.Identity(4),
            )

        pixel_data = offscreen.texture_color.read()
        try:
            # This works in Blender 3.2.2 (and possibly later versions)
            # (at least on my system/install)
            pixels = np.frombuffer(pixel_data, dtype=np.uint8).astype(np.float32) / 255
        except BufferError:
            # In Blender 5.0.1 (and possible earlier versions) (at least on my
            # system/install), the following error happens:
            # BufferError: memoryview: underlying buffer is not C-contiguous
            pixels = None
        if pixels is None:
            pixels = np.empty(pixel_data.dimensions, dtype=np.float32)
            for y in range(height):
                for x in range(width):
                    pixels[y][x] = pixel_data[y][x]
            pixels /= 255

        result = self.begin_result(0, 0, width, height)
        layer = result.layers[0].passes["Combined"]
        layer.rect = pixels.reshape(-1, 4)
        self.end_result(result)

    def view_update(self, context, depsgraph):
        assert depsgraph is not None

        scene = context.scene
        if scene is None:
            self.scene_data = SceneData()
            return

        if scene.world is not None:
            world_rdpq_defaults = util.LIBDRAGON_RDPQ(scene.world).defaults
        else:
            world_rdpq_defaults = rdpq_world_defaults.WORLD_RDPQ_DEFAULTS_DEFAULTS

        meshes: list[MeshData] = []

        for obj in scene.objects:
            if obj.type == "MESH" and obj.visible_get():
                meshes.extend(get_mesh_data(world_rdpq_defaults, obj, depsgraph))

        self.scene_data = SceneData(meshes)

    def init_shader(self):
        if self.shader is not None:
            return

        import gpu

        vert = (Path(__file__).parent / "shader.vert").read_text()
        frag = (Path(__file__).parent / "shader.frag").read_text()

        shader_info = gpu.types.GPUShaderCreateInfo()
        for name in dir(magic):
            if not name.startswith("_"):
                v = getattr(magic, name)
                shader_info.define(name, str(v))
        shader_info.typedef_source(
            "struct state_struct {"
            " mat4 matMVP;"
            " mat4 matMV;"
            " ivec4 combiner;"
            " vec4 combinerRegEnv;"
            " vec4 combinerRegPrim;"
            " float combinerRegK4;"
            " float combinerRegK5;"
            " float combinerRegPrimLODFrac;"
            " int   tex0SDim;"
            " float tex0STranslate;"
            " int   tex0SScale;"
            " float tex0SRepeats;"
            " int   tex0SFlags;"
            " int   tex0TDim;"
            " float tex0TTranslate;"
            " int   tex0TScale;"
            " float tex0TRepeats;"
            " int   tex0TFlags;"
            " int   tex1SDim;"
            " float tex1STranslate;"
            " int   tex1SScale;"
            " float tex1SRepeats;"
            " int   tex1SFlags;"
            " int   tex1TDim;"
            " float tex1TTranslate;"
            " int   tex1TScale;"
            " float tex1TRepeats;"
            " int   tex1TFlags;"
            " float alphaCompareThreshold;"
            " int generalFlags;"
            " int validInputs;"
            "};"
        )
        shader_info.uniform_buf(0, "state_struct", "inState")

        shader_info.vertex_in(0, "VEC3", "inPos")
        shader_info.vertex_in(1, "VEC3", "inNormal")
        shader_info.vertex_in(2, "VEC4", "inColor")
        shader_info.vertex_in(3, "VEC2", "inUV")

        shader_info.sampler(0, "FLOAT_2D", "inTex0")
        shader_info.sampler(1, "FLOAT_2D", "inTex1")

        vert_out = gpu.types.GPUStageInterfaceInfo("my_interface")
        vert_out.smooth("VEC4", "shadeColor")
        vert_out.smooth("VEC2", "uv")
        shader_info.vertex_out(vert_out)

        shader_info.fragment_out(0, "VEC4", "FragColor")

        shader_info.vertex_source(vert)
        shader_info.fragment_source(frag)
        shader = gpu.shader.create_from_info(shader_info)

        self.shader = shader

    def view_draw(self, context, depsgraph):
        import gpu
        import gpu_extras.batch

        if 0:
            self.bind_display_space_shader(depsgraph.scene)

        self.init_shader()
        assert self.shader is not None

        self.shader.bind()
        for mesh in self.scene_data.meshes:
            draw_mesh(
                mesh,
                self.shader,
                context.region_data.perspective_matrix,
                context.region_data.view_matrix,
            )


def get_compatible_panels():
    exclude_panels = {
        "VIEWLAYER_PT_filter",
        "VIEWLAYER_PT_layer_passes",
    }

    include_panels = {
        "EEVEE_MATERIAL_PT_context_material",
    }

    panels = []
    for panel in bpy.types.Panel.__subclasses__():
        if (
            "BLENDER_RENDER" in getattr(panel, "COMPAT_ENGINES", ())
            or panel.__name__ in include_panels
        ):
            if panel.__name__ not in exclude_panels:
                panels.append(panel)

    return panels
