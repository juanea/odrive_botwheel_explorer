"""Minisforum UM890 Pro mounting bracket for the ODrive BotWheel Explorer RevB.

Print orientation: Z up, standing flat on its base (Z=0 on build plate).
Material: ABS (final, 100% infill) / PETG (prototyping), 0.4 mm nozzle.
Check: cad model dfm "$ID" --process printing --technology fdm --material abs --nozzle 0.4 --build-volume 256x256x260
"""

import build123d as bd
from bd_materials import plastics
from bd_materials.processes import fdm
from cad import model

from params import (
    LAYER_HEIGHT_MM,
    M4_INSERT_HOLE_DEPTH,
    M4_INSERT_HOLE_DIA,
    M5_CLEARANCE_DIA,
    PC_BRACKET_HEIGHT,
    PC_BRACKET_M5_X,
    PC_BRACKET_M5_Y,
    PC_BRACKET_TAB_THICKNESS,
    STL_INNER_X,
    STL_INNER_Y,
    STL_M4_HOLE_SPACING,
    STL_OUTER_X,
    STL_OUTER_Y,
)

# Tunable parameters (plain literals so they can be tuned in the viewer)
STANDOFF_H = model.param("standoff_height", 12.0, min=8.0, max=25.0, unit="mm")
M4_BORE = model.param("m4_insert_bore", 5.6, min=4.2, max=6.2, unit="mm")
M5_BORE = model.param("m5_clearance_bore", 5.4, min=5.1, max=5.8, unit="mm")


def build_pc_bracket():
    """Return the UM890 Pro mounting bracket oriented for FDM printing (+Z up)."""
    # Main rectangular frame matching UM890_PRO_table_mount_v3_lip.stl outer footprint
    # Outer: 136.0 x 131.92 mm, Inner ventilation opening: 95.0 x 75.0 mm
    outer_x = STL_OUTER_X
    outer_y = STL_OUTER_Y
    corner_r = 4.0

    # 1. Main elevated frame (Z = 0 to STANDOFF_H)
    with bd.BuildSketch(bd.Plane.XY) as frame_sk:
        bd.RectangleRounded(outer_x, outer_y, corner_r)
        bd.RectangleRounded(STL_INNER_X, STL_INNER_Y, 3.0, mode=bd.Mode.SUBTRACT)
    frame = bd.extrude(frame_sk.sketch, STANDOFF_H)

    # 2. Four M5 mounting tabs at X = +/-90 mm, Y = +/-30 mm (Z = 0 to TAB_THICKNESS)
    # Extending outward from the X = +/-68 mm walls so M5 bolts are 100% accessible
    tab_x_outer = PC_BRACKET_M5_X + 12.0   # 102 mm -> 204 mm total length
    tab_y_width = 24.0                     # 24 mm wide tab around Y = +/-30 mm
    tab_overlap = 10.0                     # overlap into main frame wall

    tabs = []
    gussets = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            x_in = sx * (outer_x / 2 - tab_overlap)
            x_out = sx * tab_x_outer
            cx = (x_in + x_out) / 2
            lx = abs(x_out - x_in)
            cy = sy * PC_BRACKET_M5_Y

            with bd.BuildSketch(bd.Plane.XY) as tab_sk:
                with bd.Locations((cx, cy)):
                    bd.RectangleRounded(lx, tab_y_width, 4.0)
            tabs.append(bd.extrude(tab_sk.sketch, PC_BRACKET_TAB_THICKNESS))

            # 45-deg stiffening gussets seated fully inside the flat top of each tab (zero overhang)
            gx0 = sx * (outer_x / 2 - 1.0)
            gx1 = sx * (outer_x / 2 + (STANDOFF_H - PC_BRACKET_TAB_THICKNESS))
            for gsy in (-1, 1):
                gy = cy + gsy * (tab_y_width / 2 - 4.0)
                pts = [
                    (gx0, PC_BRACKET_TAB_THICKNESS),
                    (gx1, PC_BRACKET_TAB_THICKNESS),
                    (gx0, STANDOFF_H),
                ]
                if sx < 0:
                    pts = list(reversed(pts))
                with bd.BuildSketch(bd.Plane.XZ.offset(-gy)) as g_sk:
                    bd.Polygon(*pts, align=None)
                gussets.append(bd.extrude(g_sk.sketch, 2.0, both=True))

    # Fuse frame, tabs, and gussets
    body = frame
    for part in tabs + gussets:
        body = body + part

    # 3. Cut 4x M5 through-holes at X = +/-90 mm, Y = +/-30 mm
    m5_holes = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            m5_holes.append(
                bd.Pos(sx * PC_BRACKET_M5_X, sy * PC_BRACKET_M5_Y, 0)
                * bd.Cylinder(
                    M5_BORE / 2,
                    PC_BRACKET_TAB_THICKNESS + 2.0,
                    align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
                )
            )

    # 4. Cut 2x M4 heat-set insert holes from top face at X = 0, Y = +/-47.975 mm
    m4_holes = []
    m4_y = STL_M4_HOLE_SPACING / 2
    for sy in (-1, 1):
        m4_holes.append(
            bd.Pos(0, sy * m4_y, STANDOFF_H - M4_INSERT_HOLE_DEPTH)
            * bd.Cylinder(
                M4_BORE / 2,
                M4_INSERT_HOLE_DEPTH + 1.0,
                align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
            )
        )

    # 5. Add small under-frame airflow / deck-screw clearance channels on +/-X walls
    # Using 45-degree triangular/pentagonal arches so FDM prints with zero supports
    arch_cuts = []
    arch_w = 24.0
    arch_h_wall = 2.0
    arch_h_peak = 6.0  # 45 deg roof over 8 mm? Wait: peak rise = arch_w/2 for 45 deg!
    # For a 45-deg self-supporting arch with height <= 7 mm, max width = 2 * 5 = 10 mm
    # Use 3 neat 45-deg diamond/pentagon vents along each +/-X wall (width 10 mm, height 7 mm)
    vent_w = 10.0
    vent_base_h = 2.0
    vent_peak_h = vent_base_h + vent_w / 2  # 7.0 mm (exact 45 deg roof!)
    for sx in (-1, 1):
        for vy in (-24.0, 0.0, 24.0):
            pts = [
                (vy - vent_w / 2, 0.0),
                (vy + vent_w / 2, 0.0),
                (vy + vent_w / 2, vent_base_h),
                (vy, vent_peak_h),
                (vy - vent_w / 2, vent_base_h),
            ]
            with bd.BuildSketch(bd.Plane.YZ.offset(sx * (outer_x / 2 + 1.0))) as v_sk:
                bd.Polygon(*pts, align=None)
            arch_cuts.append(
                bd.extrude(v_sk.sketch, -sx * ((outer_x - STL_INNER_X) / 2 + 2.0))
            )

    body = body - (m5_holes + m4_holes + arch_cuts)

    # 6. Light top-edge chamfer (0.8 mm) for clean feel and insertion
    assert len(body.solids()) == 1, f"Expected 1 solid, got {len(body.solids())}"
    bb = body.bounding_box()
    assert abs(bb.size.Z - STANDOFF_H) < 0.05, f"Unexpected height {bb.size.Z}"
    assert bb.size.X <= 256.0 and bb.size.Y <= 256.0, f"Exceeds X2D bed: {bb.size}"

    body.label = "pc_bracket"
    body.material = plastics.abs_(process=fdm(layer_height_mm=LAYER_HEIGHT_MM))
    body.color = "#3b4252"
    return body


@model
def pc_bracket():
    return build_pc_bracket()


if __name__ == "__main__":
    pc_bracket()
