import dataclasses
from pathlib import Path
from typing import Optional

import bpy
import mathutils

import numpy as np

from .. import util
from . import magic


@dataclasses.dataclass
class MaterialData:
    tex0: Optional[bpy.types.Image]


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


class RDPQMaterialsRenderEngine(bpy.types.RenderEngine):
    bl_idname = "LIBDRAGON_RDPQ_MATERIALS"
    bl_label = "libdragon RDPQ materials"
    bl_use_preview = False

    def __init__(self):
        self.scene_data = SceneData()
        self.shader = None

    def view_update(self, context, depsgraph):
        assert depsgraph is not None

        scene = context.scene
        if scene is None:
            self.scene_data = SceneData()
            return

        meshes: list[MeshData] = []

        for obj in scene.objects:
            if obj.type == "MESH":
                obj_eval = obj.evaluated_get(depsgraph)
                mesh = obj_eval.to_mesh()
                mesh.calc_loop_triangles()
                mesh.calc_normals_split()

                model_matrix = obj.matrix_world

                vertices_co = np.empty((len(mesh.vertices), 3), dtype=np.float32)
                mesh.vertices.foreach_get("co", vertices_co.ravel())

                loop_triangles_loops = np.empty(
                    (len(mesh.loop_triangles), 3), dtype=np.int32
                )
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
                            loops_color = np.empty(
                                (len(mesh.loops), 4), dtype=np.float32
                            )
                            active_color_attribute.data.foreach_get(
                                "color", loops_color.ravel()
                            )
                        elif active_color_attribute.domain == "POINT":
                            vertices_color = np.empty(
                                (len(mesh.vertices), 4), dtype=np.float32
                            )
                            active_color_attribute.data.foreach_get(
                                "color", vertices_color.ravel()
                            )
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

                loop_triangles_material_index = np.empty(
                    len(mesh.loop_triangles), dtype=np.int32
                )
                mesh.loop_triangles.foreach_get(
                    "material_index", loop_triangles_material_index.ravel()
                )

                loops_co = vertices_co[loops_vertex_index, :]

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
                        mat_rdpq = util.LIBDRAGON_RDPQ(mat)
                        tex0 = (
                            mat_rdpq.texture0.image if mat_rdpq.use_texture0 else None
                        )
                        mat_data = MaterialData(tex0)
                    else:
                        mat_data = None

                    # Get the loops indices for the triangles using mat
                    np.equal(loop_triangles_material_index, mat_index, out=mat_mask)
                    mat_triangles_loops = loop_triangles_loops[mat_mask, :]

                    # Get the loops used by the mat-using triangles,
                    # for subsetting the coordinates/normal/color buffers,
                    # and also the triangles loops indices in that subset of triangles.
                    mat_used_loops, mat_triangles_loops_used_loops = np.unique(
                        mat_triangles_loops, return_inverse=True
                    )
                    mat_triangles_loops_used_loops = (
                        mat_triangles_loops_used_loops.reshape(
                            mat_triangles_loops.shape
                        ).astype(np.int32)
                    )

                    meshes.append(
                        MeshData(
                            model_matrix,
                            mat_triangles_loops_used_loops,
                            loops_co[mat_used_loops, :],
                            loops_normal[mat_used_loops, :],
                            loops_color[mat_used_loops, :],
                            (
                                loops_uv[mat_used_loops, :]
                                if loops_uv is not None
                                else None
                            ),
                            mat_data,
                        )
                    )

        self.scene_data = SceneData(meshes)

    def init_shader(self):
        if self.shader is not None:
            return

        import gpu

        magic_glsl = "".join(
            f"#define {_name} {getattr(magic, _name)}\n"
            for _name in dir(magic)
            if not _name.startswith("_")
        )
        vert = (Path(__file__).parent / "shader.vert").read_text()
        frag = (Path(__file__).parent / "shader.frag").read_text()
        shader = gpu.types.GPUShader(magic_glsl + vert, magic_glsl + frag)

        self.shader = shader

    def view_draw(self, context, depsgraph):
        import gpu
        import gpu_extras.batch

        if 0:
            gpu.state.blend_set("ALPHA_PREMULT")
            self.bind_display_space_shader(depsgraph.scene)

        gpu.state.depth_test_set("LESS_EQUAL")
        gpu.state.depth_mask_set(True)

        self.init_shader()
        assert self.shader is not None

        self.shader.bind()
        for mesh in self.scene_data.meshes:
            self.shader.uniform_float(
                "matMVP",
                context.region_data.perspective_matrix @ mesh.model_matrix,
            )
            self.shader.uniform_float(
                "matMV",
                context.region_data.view_matrix @ mesh.model_matrix,
            )

            valid_inputs_flags = 0

            if mesh.material is not None and mesh.material.tex0 is not None:
                valid_inputs_flags |= magic.VALID_IN_TEX0
                self.shader.uniform_sampler(
                    "inTex0", gpu.texture.from_image(mesh.material.tex0)
                )

            content = {
                "inPos": mesh.loops_co,
                "inNormal": mesh.loops_normal,
                "inColor": mesh.loops_color,
            }

            if mesh.loops_uv is not None:
                valid_inputs_flags |= magic.VALID_IN_UV
                content["inUV"] = mesh.loops_uv

            self.shader.uniform_int("inValidInputs", valid_inputs_flags)

            batch: gpu.types.GPUBatch = gpu_extras.batch.batch_for_shader(
                self.shader,
                "TRIS",
                content,
                indices=mesh.loop_triangles_loops,
            )
            batch.draw(self.shader)


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
