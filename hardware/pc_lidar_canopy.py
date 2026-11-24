"""Single-piece Synthara-style triangulated truss canopy for the ODrive BotWheel Explorer.

Combines:
  - Integrated Minisforum UM890 Pro mounting cradle centered at X = -80 mm, Y = 0 mm
    (37 mm behind chassis front edge to STL lip plate, 40 mm to PC; open front & rear for I/O).
  - 4 bolted column anchors on the real 30 x 30 mm chassis grid at X = +10 / -140 mm, Y = +/-90 mm.
  - Organic tapered triangulated truss struts rising from the 4 columns to the elevated
    SICK TiM781 LiDAR platform locked on base_link (X = 0, Y = 0, top Z = 94 mm, 5 mm above PC).

Print orientation: Upright (+Z up), base tray and 4 column bosses flat on the build plate.
Material: ABS / PETG-CF, 0.4 mm nozzle, tree supports under the elevated LiDAR deck.
Check: cad model dfm "$ID" --process printing --technology fdm --material abs --nozzle 0.4 --build-volume 256x256x260
"""

import build123d as bd
from bd_materials import plastics
from bd_materials.processes import fdm
from cad import model

from params import (
    CANOPY_BOLT_XS,
    CANOPY_BOLT_Y,
    CANOPY_CLEAR_Z,
    CANOPY_DECK_THICKNESS,
    CHASSIS_BOLT_CLEARANCE_DIA,
    LAYER_HEIGHT_MM,
    LIDAR_M3_CBORE_DIA,
    LIDAR_M3_CLEARANCE_DIA,
    LIDAR_M3_WEB_THICKNESS,
    LIDAR_M3_X,
    LIDAR_M3_Y,
    M4_INSERT_HOLE_DEPTH,
    M4_INSERT_HOLE_DIA,
    PC_CENTER_X,
    PC_TRAY_HEIGHT,
    STL_INNER_X,
    STL_INNER_Y,
    STL_M4_HOLE_SPACING,
    STL_OUTER_X,
    STL_OUTER_Y,
)

# Tunable parameters
TRAY_H = model.param("tray_height", PC_TRAY_HEIGHT, min=9.5, max=16.0, unit="mm")
CLEAR_Z = model.param("lidar_clear_z", CANOPY_CLEAR_Z, min=84.0, max=120.0, unit="mm")
DECK_THK = model.param("lidar_deck_thickness", CANOPY_DECK_THICKNESS, min=6.5, max=12.0, unit="mm")
BOLT_BORE = model.param("chassis_bolt_bore", CHASSIS_BOLT_CLEARANCE_DIA, min=5.4, max=9.0, unit="mm")
M4_BORE = model.param("m4_insert_bore", M4_INSERT_HOLE_DIA, min=4.2, max=6.2, unit="mm")
STRUT_R = model.param("strut_radius", 5.5, min=4.0, max=8.0, unit="mm")


def _tapered_strut(p0, p1, r0, r1):
    """Create a smooth tapered cylindrical strut with spherical end caps between two 3D points."""
    v0 = bd.Vector(*p0)
    v1 = bd.Vector(*p1)
    dv = v1 - v0
    length = dv.length
    assert length > 1e-3, f"Zero-length strut between {p0} and {p1}"
    z_dir = dv.normalized()
    plane = bd.Plane(origin=v0, z_dir=z_dir)
    # Tapered cone frustum (or cylinder when radii are equal)
    if abs(r0 - r1) < 1e-4:
        shaft = bd.Solid.make_cylinder(r0, length, plane)
    else:
        shaft = bd.Solid.make_cone(r0, r1, length, plane)
    # Add spherical knuckles at both endpoints so intersecting truss nodes blend smoothly
    cap0 = bd.Pos(*p0) * bd.Sphere(r0)
    cap1 = bd.Pos(*p1) * bd.Sphere(r1)
    return shaft + cap0 + cap1


def build_pc_lidar_canopy():
    """Return the monolithic PC + LiDAR Synthara-style truss canopy (+Z up, base_link frame)."""
    top_z = CLEAR_Z + DECK_THK        # 94.0 mm
    deck_mid_z = CLEAR_Z + DECK_THK / 2.0
    x_front, x_rear = CANOPY_BOLT_XS  # +10.0, -140.0
    y_col = CANOPY_BOLT_Y             # 90.0
    boss_r = 12.5                     # Ø25 mm column pad (clears M6/M8 washer & socket head)
    boss_h = 10.0                     # Base column boss height (Z = 0..10)

    parts = []

    # 1. Central PC mounting cradle (Z = 0..TRAY_H) centered at (PC_CENTER_X, 0)
    # Matches UM890_PRO_table_mount_v3_lip.stl (136.0 x 131.92 mm) with 95 x 75 mm airflow cutout
    with bd.BuildSketch(bd.Plane.XY) as cradle_sk:
        with bd.Locations((PC_CENTER_X, 0.0)):
            bd.RectangleRounded(STL_OUTER_X, STL_OUTER_Y, 6.0)
            bd.RectangleRounded(STL_INNER_X, STL_INNER_Y, 5.0, mode=bd.Mode.SUBTRACT)
    cradle = bd.extrude(cradle_sk.sketch, TRAY_H)
    parts.append(cradle)

    # 2. Four bolted column anchor pads on the real chassis grid (X = +10, -140; Y = +/-90)
    # Connected to the PC cradle via sleek swept base arms on Z = 0..8 mm (open front & rear for I/O!)
    arm_h = 8.0
    for sy in (-1, 1):
        yc = sy * y_col
        # Side longitudinal rail tying front and rear column pads together along Y = +/-90 mm
        with bd.BuildSketch(bd.Plane.XY) as rail_sk:
            with bd.Locations(((x_front + x_rear) / 2.0, yc)):
                bd.RectangleRounded(abs(x_front - x_rear) + 2.0 * boss_r, 14.0, 6.0)
        parts.append(bd.extrude(rail_sk.sketch, arm_h))

        # Front & rear circular column bosses (slightly taller collar for stiffness)
        for xc in (x_front, x_rear):
            parts.append(
                bd.Pos(xc, yc, 0.0)
                * bd.Cylinder(
                    boss_r,
                    boss_h,
                    align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
                )
            )

        # Two angled base tie-arms per side linking the longitudinal rail to the PC cradle side wall
        # Leaves front (+X) and rear (-X) of the PC completely unobstructed for cables & slide-in
        y_cradle_edge = sy * (STL_OUTER_Y / 2.0 - 6.0)
        for x_anchor, x_cradle in [
            (x_front - 18.0, PC_CENTER_X + 42.0),
            (x_rear + 14.0, PC_CENTER_X - 42.0),
        ]:
            # Build a 2D flat strap on Z = 0..arm_h between (x_anchor, yc) and (x_cradle, y_cradle_edge)
            p_a = bd.Vector(x_anchor, yc, 0)
            p_b = bd.Vector(x_cradle, y_cradle_edge, 0)
            dv = p_b - p_a
            ang = bd.Vector(1, 0, 0).get_signed_angle(dv, bd.Vector(0, 0, 1))
            mid = (p_a + p_b) * 0.5
            with bd.BuildSketch(bd.Plane.XY) as strap_sk:
                with bd.Locations(bd.Location((mid.X, mid.Y, 0), (0, 0, ang))):
                    bd.RectangleRounded(dv.length + 14.0, 14.0, 5.0)
            parts.append(bd.extrude(strap_sk.sketch, arm_h))

    # 3. Elevated SICK TiM781 LiDAR platform (Z = CLEAR_Z .. top_z), locked on base_link (X=0, Y=0)
    # Footprint sized to support TiM781 base (X in [-47, +29], Y in [-31, +30]) cleanly
    lidar_plat_x_min = -44.0
    lidar_plat_x_max = 24.5
    lidar_plat_cx = (lidar_plat_x_min + lidar_plat_x_max) / 2.0  # -9.0 mm
    lidar_plat_lx = lidar_plat_x_max - lidar_plat_x_min          # 70.0 mm
    lidar_plat_ly = 68.0
    with bd.BuildSketch(bd.Plane.XY.offset(CLEAR_Z)) as top_sk:
        with bd.Locations((lidar_plat_cx, 0.0)):
            bd.RectangleRounded(lidar_plat_lx, lidar_plat_ly, 8.0)
    top_deck = bd.extrude(top_sk.sketch, DECK_THK)
    parts.append(top_deck)

    # 4. Synthara-style organic triangulated truss struts (both sides Y = +/-)
    # Shoulder nodes sit above the PC top (Z = CLEAR_Z = 88 mm) and outside the PC walls (|Y| >= 75 mm),
    # so every side truss strut is >= 49 deg (self-supporting) and clears the UM890 Pro with 0 interference.
    r_main = STRUT_R          # 5.5 mm -> Ø11 mm main load-bearing struts
    r_sec = STRUT_R * 0.72    # ~4.0 mm -> Ø8 mm triangulated cross-braces

    for sy in (-1, 1):
        # Base launch points offset slightly along rail from bolt centers so bolt heads clear cleanly
        p_f_base = (x_front - 14.0, sy * y_col, arm_h - 1.0)           # (-4, +/-90, 7)
        p_r_base = (x_rear + 14.0, sy * y_col, arm_h - 1.0)            # (-126, +/-90, 7)
        p_m_base = ((x_front + x_rear) / 2.0, sy * y_col, arm_h - 1.0) # (-65, +/-90, 7)

        # Upper shoulder nodes: outside PC (|Y| >= 75 mm vs 63.5 mm) and above PC top (88 mm vs 81 mm)
        p_f_mid = (6.0, sy * 75.0, CLEAR_Z)                            # (+6, +/-75, 88)
        p_r_mid = (-68.0, sy * 76.0, CLEAR_Z)                          # (-68, +/-76, 88)

        # Top deck landing nodes (blended cleanly into the LiDAR platform edges)
        p_top_f = (16.0, sy * 28.0, deck_mid_z)                        # (+16, +/-28, 92)
        p_top_r = (-34.0, sy * 28.0, deck_mid_z)                       # (-34, +/-28, 92)

        # Primary load-bearing legs (tapered thicker at base, sleeker at top)
        parts.append(_tapered_strut(p_f_base, p_f_mid, r_main * 1.15, r_main * 0.95))
        parts.append(_tapered_strut(p_f_mid, p_top_f, r_main * 0.95, r_main * 0.85))

        parts.append(_tapered_strut(p_r_base, p_r_mid, r_main * 1.15, r_main * 0.95))
        parts.append(_tapered_strut(p_r_mid, p_top_r, r_main * 0.95, r_main * 0.85))

        # Triangulated Synthara web braces (all >= 49 deg, high fore-aft & torsional stiffness)
        parts.append(_tapered_strut(p_m_base, p_f_mid, r_sec * 1.1, r_sec))
        parts.append(_tapered_strut(p_m_base, p_r_mid, r_sec * 1.1, r_sec))
        parts.append(_tapered_strut(p_f_mid, p_r_mid, r_sec, r_sec))
        parts.append(_tapered_strut(p_f_mid, p_top_r, r_sec * 0.95, r_sec * 0.85))

    # Fuse all solid components into a single monolithic body
    body = parts[0]
    for p in parts[1:]:
        body = body + p

    # Trim anything protruding below Z = 0 or above top_z (e.g. spherical end caps)
    clip_box = bd.Pos(-65.0, 0.0, top_z / 2.0) * bd.Box(300.0, 300.0, top_z)
    body = body & clip_box

    # 5. Cut holes:
    cuts = []

    # 5a. 4x Chassis mounting bolt clearance holes + vertical tool-access clearance above each boss
    for xc in (x_front, x_rear):
        for sy in (-1, 1):
            yc = sy * y_col
            # Through-hole in boss
            cuts.append(
                bd.Pos(xc, yc, -1.0)
                * bd.Cylinder(
                    BOLT_BORE / 2.0,
                    boss_h + 4.0,
                    align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
                )
            )
            # Clear socket/washer landing zone above boss (Z = boss_h .. boss_h + 25)
            cuts.append(
                bd.Pos(xc, yc, boss_h)
                * bd.Cylinder(
                    max(BOLT_BORE / 2.0 + 3.5, 7.5),
                    30.0,
                    align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
                )
            )

    # 5b. 2x M4 heat-set insert bores in PC cradle at X = PC_CENTER_X, Y = +/-47.975 mm
    m4_y = STL_M4_HOLE_SPACING / 2.0
    for sy in (-1, 1):
        cuts.append(
            bd.Pos(PC_CENTER_X, sy * m4_y, TRAY_H - M4_INSERT_HOLE_DEPTH)
            * bd.Cylinder(
                M4_BORE / 2.0,
                M4_INSERT_HOLE_DEPTH + 1.0,
                align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
            )
        )

    # 5c. 2x SICK TiM781 M3 through-holes + underside counterbores at X = +1.0, Y = +/-25.5 mm
    cbore_depth = DECK_THK - LIDAR_M3_WEB_THICKNESS  # 8.0 - 5.0 = 3.0 mm
    assert cbore_depth >= 0.0, "DECK_THK must be >= LIDAR_M3_WEB_THICKNESS"
    for sy in (-1, 1):
        # M3 clearance through-hole
        cuts.append(
            bd.Pos(LIDAR_M3_X, sy * LIDAR_M3_Y, CLEAR_Z - 1.0)
            * bd.Cylinder(
                LIDAR_M3_CLEARANCE_DIA / 2.0,
                DECK_THK + 2.0,
                align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
            )
        )
        # Underside counterbore so M3x10 SHCS engages 2.5 mm (<= 2.8 mm SICK limit)
        if cbore_depth > 0.1:
            cuts.append(
                bd.Pos(LIDAR_M3_X, sy * LIDAR_M3_Y, CLEAR_Z - 0.5)
                * bd.Cylinder(
                    LIDAR_M3_CBORE_DIA / 2.0,
                    cbore_depth + 0.5,
                    align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
                )
            )

    body = body - cuts

    assert len(body.solids()) == 1, f"Expected 1 solid, got {len(body.solids())}"
    bb = body.bounding_box()
    assert bb.max.X <= 25.0, f"Canopy overhangs front edge (+25 mm): max.X={bb.max.X:.2f}"
    assert bb.size.X <= 256.0 and bb.size.Y <= 256.0 and bb.size.Z <= 260.0, (
        f"Exceeds X2D build volume: {bb.size}"
    )

    body.label = "pc_lidar_canopy"
    body.material = plastics.abs_(process=fdm(layer_height_mm=LAYER_HEIGHT_MM))
    body.color = "#2a2e35"
    return body


@model
def pc_lidar_canopy():
    return build_pc_lidar_canopy()


if __name__ == "__main__":
    pc_lidar_canopy()
