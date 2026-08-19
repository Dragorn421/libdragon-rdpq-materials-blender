import re

import bpy

from . import mkmaterial_export
from . import rdpq_material_props

COMBINER_MUXES_MKMATERIAL_MAP = {
    v: k for k, v in mkmaterial_export.COMBINER_MUXES_MKMATERIAL_MAP.items()
}
# tex0 maps to TEX0 or TEX0_BUG depending on the cycle
COMBINER_MUXES_MKMATERIAL_MAP["tex0"] = "TEX0_OR_TEX0_BUG"
BLENDER_MUXES_MKMATERIAL_MAP = {
    v: k for k, v in mkmaterial_export.BLENDER_MUXES_MKMATERIAL_MAP.items()
}
DITHER_MKMATERIAL_MAP = {
    v: k for k, v in mkmaterial_export.DITHER_MKMATERIAL_MAP.items()
}


PATTERN_RAW_EXPR = re.compile(
    r"(\s*\(\s*([\w.]+)\s*,\s*([\w.]+)\s*,\s*([\w.]+)\s*,\s*([\w.]+)\s*\)(?:\s*,\s*\(\s*([\w.]+)\s*,\s*([\w.]+)\s*,\s*([\w.]+)\s*,\s*([\w.]+)\s*\))?)"
)


def parse_bool(value: str):
    if value in {"true", "1", "True"}:
        return True
    if value in {"false", "0", "False"}:
        return False
    raise ValueError(value)


def parse_color(value: str, allow_alpha: bool):
    tokens = value.split(",")
    if len(tokens) != 3 and len(tokens) != 4:
        raise ValueError(f"invalid color value: {value}")
    if not allow_alpha and len(tokens) == 4:
        raise ValueError(f"invalid rgb-only color value: {value}")
    color = tuple(map(float, tokens))
    if allow_alpha and len(color) < 4:
        color = (*color, 1)
    return color


def rdpq_material_properties_from_dict(
    mat_rdpq: rdpq_material_props.RDPQMaterialProperties,
    mat_data: dict,
    mat_textures: dict[int, bpy.types.Image],
):
    # textures

    def handle_texture_axis(
        tex_i: int,
        axis: str,
        texture_axis_props: rdpq_material_props.RDPQMaterialTextureAxisProperties,
    ):
        texture_axis_props.translate = float(
            mat_data.get(f"tex{tex_i}.{axis}.translate", "0")
        )
        texture_axis_props.scale = int(mat_data.get(f"tex{tex_i}.{axis}.scale", "0"))
        repeats = mat_data.get(f"tex{tex_i}.{axis}.repeats", "1")
        texture_axis_props.repeats_inf = repeats == "inf"
        if repeats != "inf":
            texture_axis_props.repeats = float(repeats)
        texture_axis_props.mirror = parse_bool(
            mat_data.get(f"tex{tex_i}.{axis}.mirror", "false")
        )

    def handle_texture(tex_i: int):
        if tex_i in mat_textures:
            setattr(mat_rdpq, f"use_texture{tex_i}", True)
            texture_props: rdpq_material_props.RDPQMaterialTextureProperties = getattr(
                mat_rdpq, f"texture{tex_i}"
            )
            texture_props.image = mat_textures[tex_i]
            texture_props.format = mat_data.get(f"tex{tex_i}.fmt", "AUTO")
            texture_props.mipmap = mat_data.get(f"tex{tex_i}.mipmap", "NONE")
            texture_props.dithering = mat_data.get(f"tex{tex_i}.dithering", "NONE")
            handle_texture_axis(tex_i, "s", texture_props.s)
            handle_texture_axis(tex_i, "t", texture_props.t)
        else:
            setattr(mat_rdpq, f"use_texture{tex_i}", False)

    handle_texture(0)
    handle_texture(1)

    # combiner

    if "combiner.rgb" in mat_data or "combiner.alpha" in mat_data:
        raise NotImplementedError("combexpr expressions not implemented")

    combiner_rgb = mat_data.get("combiner.rgb.raw")
    combiner_alpha = mat_data.get("combiner.alpha.raw")

    if combiner_rgb is not None:
        match = PATTERN_RAW_EXPR.fullmatch(combiner_rgb)
        if match is None:
            raise Exception(f"bad combiner.rgb.raw: {combiner_rgb}")
        rgb_0 = match.groups()[1:5]
        rgb_1 = match.groups()[5:9]
        if all(_rgb_X_1 is None for _rgb_X_1 in rgb_1):
            rgb_1 = None
    else:
        rgb_0 = ("0", "0", "0", "tex0")
        rgb_1 = None

    if combiner_alpha is not None:
        match = PATTERN_RAW_EXPR.fullmatch(combiner_alpha)
        if match is None:
            raise Exception(f"bad combiner.alpha.raw: {combiner_alpha}")
        alpha_0 = match.groups()[1:5]
        alpha_1 = match.groups()[5:9]
        if all(_alpha_X_1 is None for _alpha_X_1 in alpha_1):
            alpha_1 = None
    else:
        alpha_0 = ("0", "0", "0", "tex0")
        alpha_1 = None

    def fixup_combiner_tex0(rgb_n: tuple[str, ...], tex0_repl):
        return tuple(
            tex0_repl if _rgb_X_n == "TEX0_OR_TEX0_BUG" else _rgb_X_n
            for _rgb_X_n in rgb_n
        )

    map = COMBINER_MUXES_MKMATERIAL_MAP
    rgb_0 = tuple(map[_rgb_X_0] for _rgb_X_0 in rgb_0)
    rgb_0 = fixup_combiner_tex0(rgb_0, "TEX0")
    if rgb_1 is not None:
        rgb_1 = tuple(map[_rgb_X_1] for _rgb_X_1 in rgb_1)
        rgb_1 = fixup_combiner_tex0(rgb_1, "TEX0_BUG")
    alpha_0 = tuple(map[_alpha_X_0] for _alpha_X_0 in alpha_0)
    alpha_0 = fixup_combiner_tex0(alpha_0, "TEX0")
    if alpha_1 is not None:
        alpha_1 = tuple(map[_alpha_X_1] for _alpha_X_1 in alpha_1)

    two_cycle_combiner = rgb_1 is not None or alpha_1 is not None
    if two_cycle_combiner:
        if rgb_1 is None:
            rgb_1 = ("0", "0", "0", "COMBINED")
        if alpha_1 is None:
            alpha_1 = ("0", "0", "0", "COMBINED")

    # TODO detect combiner presets

    if two_cycle_combiner:
        assert rgb_1 is not None
        assert alpha_1 is not None
        mat_rdpq.combiner.preset = "CUSTOM_2_PASSES"
        mat_rdpq.combiner.rgb_A_0 = rgb_0[0]
        mat_rdpq.combiner.rgb_B_0 = rgb_0[1]
        mat_rdpq.combiner.rgb_C_0 = rgb_0[2]
        mat_rdpq.combiner.rgb_D_0 = rgb_0[3]
        mat_rdpq.combiner.alpha_A_0 = alpha_0[0]
        mat_rdpq.combiner.alpha_B_0 = alpha_0[1]
        mat_rdpq.combiner.alpha_C_0 = alpha_0[2]
        mat_rdpq.combiner.alpha_D_0 = alpha_0[3]
        mat_rdpq.combiner.rgb_A_1 = rgb_1[0]
        mat_rdpq.combiner.rgb_B_1 = rgb_1[1]
        mat_rdpq.combiner.rgb_C_1 = rgb_1[2]
        mat_rdpq.combiner.rgb_D_1 = rgb_1[3]
        mat_rdpq.combiner.alpha_A_1 = alpha_1[0]
        mat_rdpq.combiner.alpha_B_1 = alpha_1[1]
        mat_rdpq.combiner.alpha_C_1 = alpha_1[2]
        mat_rdpq.combiner.alpha_D_1 = alpha_1[3]
    else:
        mat_rdpq.combiner.preset = "CUSTOM_1_PASS"
        mat_rdpq.combiner.rgb_A = rgb_0[0]
        mat_rdpq.combiner.rgb_B = rgb_0[1]
        mat_rdpq.combiner.rgb_C = rgb_0[2]
        mat_rdpq.combiner.rgb_D = rgb_0[3]
        mat_rdpq.combiner.alpha_A = alpha_0[0]
        mat_rdpq.combiner.alpha_B = alpha_0[1]
        mat_rdpq.combiner.alpha_C = alpha_0[2]
        mat_rdpq.combiner.alpha_D = alpha_0[3]

    # combiner registers

    k4 = mat_data.get("combiner.reg.k4")
    mat_rdpq.combiner.registers.set_k4 = k4 is not None
    if k4 is not None:
        mat_rdpq.combiner.registers.k4 = float(k4)

    k5 = mat_data.get("combiner.reg.k5")
    mat_rdpq.combiner.registers.set_k5 = k5 is not None
    if k5 is not None:
        mat_rdpq.combiner.registers.k5 = float(k5)

    prim_lod_frac = mat_data.get("combiner.reg.prim_lod_frac")
    mat_rdpq.combiner.registers.set_prim_lod_frac = prim_lod_frac is not None
    if prim_lod_frac is not None:
        mat_rdpq.combiner.registers.prim_lod_frac = float(prim_lod_frac)

    env = mat_data.get("combiner.reg.env")
    mat_rdpq.combiner.registers.set_env = env is not None
    if env is not None:
        mat_rdpq.combiner.registers.env = parse_color(env, True)

    prim = mat_data.get("combiner.reg.prim")
    mat_rdpq.combiner.registers.set_prim = prim is not None
    if prim is not None:
        mat_rdpq.combiner.registers.prim = parse_color(prim, True)

    # blender

    blender_mode = mat_data.get("blender.mode")
    blender_mode_raw = mat_data.get("blender.mode.raw")

    if blender_mode is not None and blender_mode_raw is not None:
        raise Exception("Cannot set both blender.mode and blender.mode.raw")

    if blender_mode_raw is not None:
        match = PATTERN_RAW_EXPR.fullmatch(blender_mode_raw)
        if match is None:
            raise Exception(f"bad blender.mode.raw: {blender_mode_raw}")
        blender_0 = match.groups()[1:5]
        blender_1 = match.groups()[5:9]
        if all(_blender_X_1 is None for _blender_X_1 in blender_1):
            blender_1 = None

        map = BLENDER_MUXES_MKMATERIAL_MAP
        blender_0 = tuple(map[_blender_X_0] for _blender_X_0 in blender_0)
        if blender_1 is not None:
            blender_1 = tuple(map[_blender_X_1] for _blender_X_1 in blender_1)

        two_cycle_blender = blender_1 is not None

        mat_rdpq.blender.preset = (
            "CUSTOM_2_PASSES" if two_cycle_blender else "CUSTOM_1_PASS"
        )
        if two_cycle_blender:
            mat_rdpq.blender.p_0 = blender_0[0]
            mat_rdpq.blender.a_0 = blender_0[1]
            mat_rdpq.blender.q_0 = blender_0[2]
            mat_rdpq.blender.b_0 = blender_0[3]
            mat_rdpq.blender.p_1 = blender_1[0]
            mat_rdpq.blender.a_1 = blender_1[1]
            mat_rdpq.blender.q_1 = blender_1[2]
            mat_rdpq.blender.b_1 = blender_1[3]
        else:
            mat_rdpq.blender.p = blender_0[0]
            mat_rdpq.blender.a = blender_0[1]
            mat_rdpq.blender.q = blender_0[2]
            mat_rdpq.blender.b = blender_0[3]
    elif blender_mode is not None:
        blender_mode = blender_mode.upper()
        mat_rdpq.blender.preset = blender_mode
        if blender_mode == "MULTIPLY_CONST":
            blender_const = mat_data.get("blender.const")
            if blender_const is None:
                raise Exception(
                    "Must set blender.const when blender.mode is multiply_const"
                )
            mat_rdpq.blender.registers.fog_color_alpha = float(blender_const)

    # blender registers

    blend_rgb = mat_data.get("blender.reg.blend.rgb")
    mat_rdpq.blender.registers.set_blend_color_rgb = blend_rgb is not None
    if blend_rgb is not None:
        mat_rdpq.blender.registers.blend_color_rgb = parse_color(blend_rgb, False)

    fog_rgb = mat_data.get("blender.reg.fog.rgb")
    mat_rdpq.blender.registers.set_fog_color_rgb = fog_rgb is not None
    if fog_rgb is not None:
        mat_rdpq.blender.registers.fog_color_rgb = parse_color(fog_rgb, False)

    fog_alpha = mat_data.get("blender.reg.fog.alpha")
    if blender_mode == "MULTIPLY_CONST" and fog_alpha is not None:
        raise Exception(
            "Cannot set blender.reg.fog.alpha when blender.mode is multiply_const"
        )
    mat_rdpq.blender.registers.set_fog_color_alpha = fog_alpha is not None
    if fog_alpha is not None:
        mat_rdpq.blender.registers.fog_color_alpha = float(fog_alpha)

    # render mode overrides

    antialias = mat_data.get("rm.antialias")
    mat_rdpq.override_render_mode.override_antialias = antialias is not None
    if antialias is not None:
        mat_rdpq.override_render_mode.antialias = antialias.upper()

    fog = mat_data.get("rm.fog")
    mat_rdpq.override_render_mode.override_fog = fog is not None
    if fog is not None:
        mat_rdpq.override_render_mode.fog = fog.upper()

    dither_rgb = mat_data.get("rm.dither.rgb")
    dither_alpha = mat_data.get("rm.dither.alpha")
    if dither_rgb is None and dither_alpha is None:
        mat_rdpq.override_render_mode.override_dithering = False
    else:
        if dither_rgb is None or dither_alpha is None:
            raise Exception(
                "rm.dither.rgb and rm.dither.alpha must be both set or neither"
            )
        mat_rdpq.override_render_mode.override_dithering = True
        mat_rdpq.override_render_mode.dithering = DITHER_MKMATERIAL_MAP[
            (dither_rgb, dither_alpha)
        ]

    texture_filtering = mat_data.get("rm.filtering")
    mat_rdpq.override_render_mode.override_texture_filtering = (
        texture_filtering is not None
    )
    if texture_filtering is not None:
        mat_rdpq.override_render_mode.texture_filtering = texture_filtering.upper()

    texture_perspective_correction = mat_data.get("rm.perspective")
    mat_rdpq.override_render_mode.override_texture_perspective_correction = (
        texture_perspective_correction is not None
    )
    if texture_perspective_correction is not None:
        mat_rdpq.override_render_mode.texture_perspective_correction = parse_bool(
            texture_perspective_correction
        )

    alpha_compare = mat_data.get("rm.alpha_compare")
    mat_rdpq.override_render_mode.override_alpha_compare = alpha_compare is not None
    if alpha_compare is not None:
        mat_rdpq.override_render_mode.alpha_compare_threshold = int(alpha_compare)

    zmode = mat_data.get("rm.zmode")
    mat_rdpq.override_render_mode.override_z_compare_and_z_update = zmode is not None
    if zmode is not None:
        (
            mat_rdpq.override_render_mode.z_compare,
            mat_rdpq.override_render_mode.z_update,
        ) = {
            "none": (False, False),
            "compare": (True, False),
            "update": (False, True),
            "compare+update": (True, True),
        }[
            zmode
        ]

    z_override = mat_data.get("rm.z_override")
    deltaz_override = mat_data.get("rm.deltaz_override")
    if z_override is None and deltaz_override is None:
        mat_rdpq.override_render_mode.override_fixed_z = False
    else:
        if z_override is None or deltaz_override is None:
            raise Exception(
                "rm.z_override and rm.deltaz_override must be both set or neither"
            )
        mat_rdpq.override_render_mode.override_fixed_z = True
        mat_rdpq.override_render_mode.fixed_z = int(z_override)
        mat_rdpq.override_render_mode.fixed_z_deltaz = int(deltaz_override)
