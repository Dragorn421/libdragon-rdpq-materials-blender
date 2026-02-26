import math
import typing
from typing import TYPE_CHECKING

import bpy


if TYPE_CHECKING:
    from . import RDPQSceneProperties, RDPQWorldProperties
    from . import rdpq_material_props

    @typing.overload
    def LIBDRAGON_RDPQ(data: bpy.types.Scene) -> "RDPQSceneProperties": ...
    @typing.overload
    def LIBDRAGON_RDPQ(data: bpy.types.World) -> "RDPQWorldProperties": ...
    @typing.overload
    def LIBDRAGON_RDPQ(
        data: bpy.types.Material,
    ) -> rdpq_material_props.RDPQMaterialProperties: ...


def LIBDRAGON_RDPQ(data):
    return data.libdragon_rdpq



def intlog2(v: int):
    r = round(math.log2(v))
    if 2**r == v:
        return r
    else:
        return None
