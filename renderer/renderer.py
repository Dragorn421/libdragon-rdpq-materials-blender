import dataclasses
from pathlib import Path

import bpy
import mathutils

import numpy as np


@dataclasses.dataclass
class MeshData:
    model_matrix: mathutils.Matrix
    loop_triangles_loops: np.ndarray
    loops_co: np.ndarray
    loops_normal: np.ndarray


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

                loops_co = vertices_co[loops_vertex_index, :]

                mesh.free_normals_split()
                obj_eval.to_mesh_clear()

                meshes.append(
                    MeshData(
                        obj.matrix_world,
                        loop_triangles_loops,
                        loops_co,
                        loops_normal,
                    )
                )

        self.scene_data = SceneData(meshes)

    def init_shader(self):
        if self.shader is not None:
            return

        import gpu

        vert = (Path(__file__).parent / "shader.vert").read_text()
        frag = (Path(__file__).parent / "shader.frag").read_text()
        shader = gpu.types.GPUShader(vert, frag)

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
        self.shader.uniform_float("color", (1, 1, 0, 1))
        for mesh in self.scene_data.meshes:
            self.shader.uniform_float(
                "matMVP",
                context.region_data.perspective_matrix @ mesh.model_matrix,
            )
            self.shader.uniform_float(
                "matMV",
                context.region_data.view_matrix @ mesh.model_matrix,
            )
            batch: gpu.types.GPUBatch = gpu_extras.batch.batch_for_shader(
                self.shader,
                "TRIS",
                {"inPos": mesh.loops_co, "inNormal": mesh.loops_normal},
                indices=mesh.loop_triangles_loops,
            )
            batch.draw(self.shader)
