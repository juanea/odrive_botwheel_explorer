"""Full robot assembly for the ODrive BotWheel Explorer:
  - Official ODrive BotWheel Explorer chassis (imported from Onshape V39, aligned to base_link)
  - Single-piece Synthara-style PC + LiDAR truss canopy (4x chassis bolts on 30 x 30 mm grid)
  - UM890_PRO_table_mount_v3_lip.stl + Minisforum UM890 Pro centered at X = -80 mm (37-40 mm inside front)
  - SICK TiM781 LiDAR from vendor xbf locked on base_link Z-axis (X = 0, Y = 0, +X forward 270 deg FOV)
"""

import build123d as bd
from bd_materials import metals, plastics
from cad import model, stl, xbf

from botwheel_robot import botwheel_robot
from params import (
    CANOPY_TOP_Z,
    D435_STL,
    LIDAR_BOTTOM_Z_LOCAL,
    PC_CENTER_X,
    PC_DEPTH_Y,
    PC_HEIGHT_Z,
    PC_TRAY_HEIGHT,
    PC_WIDTH_X,
    STL_INNER_X,
    STL_INNER_Y,
    STL_M4_HOLE_SPACING,
    STL_OUTER_X,
    STL_OUTER_Y,
    STL_THICKNESS,
    TIM781_XBF,
    UM890_STL,
)
from pc_lidar_canopy import pc_lidar_canopy


def _reference_um890_stl_plate():
    """B-rep representation of UM890_PRO_table_mount_v3_lip.stl (verified against STL bounds)."""
    scan_bb = stl.read(UM890_STL).bounding_box()
    assert abs(scan_bb.size.X - STL_OUTER_X) < 0.2
    assert abs(scan_bb.size.Y - STL_OUTER_Y) < 0.2
    assert abs(scan_bb.size.Z - STL_THICKNESS) < 0.2

    with bd.BuildSketch(bd.Plane.XY) as sk:
        bd.RectangleRounded(STL_OUTER_X, STL_OUTER_Y, 4.0)
        bd.RectangleRounded(STL_INNER_X, STL_INNER_Y, 3.0, mode=bd.Mode.SUBTRACT)
        for sy in (-1, 1):
            with bd.Locations((0, sy * STL_M4_HOLE_SPACING / 2)):
                bd.Circle(2.04, mode=bd.Mode.SUBTRACT)
    plate = bd.extrude(sk.sketch, STL_THICKNESS)
    plate.label = "um890_table_mount_stl_ref"
    plate.material = plastics.petg()
    plate.color = "#8faadc"
    return plate


def _reference_um890_pc():
    """Simplified envelope of the Minisforum UM890 Pro Mini PC (130 x 127 x 66.6 mm)."""
    with bd.BuildSketch(bd.Plane.XY) as sk:
        bd.RectangleRounded(PC_WIDTH_X, PC_DEPTH_Y, 8.0)
    pc = bd.extrude(sk.sketch, PC_HEIGHT_Z)
    pc.label = "minisforum_um890_pro_ref"
    pc.material = metals.aluminum()
    pc.color = "#1f2328"
    return pc


def _reference_realsense_d435():
    """Exact-envelope B-rep of the Intel RealSense D435 (90 x 25 x 25 mm, verified against d435.stl).

    Local frame: +X forward (front glass at X = 0), +Y left (width 90 mm), +Z up (height 25 mm).
    """
    scan_bb = stl.read(D435_STL).bounding_box()
    assert abs(scan_bb.size.X - 90.0) < 0.2
    assert abs(scan_bb.size.Y - 25.0) < 0.2
    assert abs(scan_bb.size.Z - 25.05) < 0.2

    # Rounded aluminum housing (X in [-25, 0], Y in [-45, +45], Z in [-12.5, +12.5])
    with bd.BuildSketch(bd.Plane.YZ) as body_sk:
        bd.RectangleRounded(90.0, 25.0, 11.5)
    housing = bd.extrude(body_sk.sketch, -25.0)
    housing.label = "d435_housing"
    housing.material = metals.aluminum()
    housing.color = "#b8c0c8"

    # Front black glass face (X = 0..+0.4)
    with bd.BuildSketch(bd.Plane.YZ) as glass_sk:
        bd.RectangleRounded(84.0, 19.0, 8.5)
    glass = bd.extrude(glass_sk.sketch, 0.4)
    glass.label = "d435_front_glass"
    glass.material = plastics.abs_()
    glass.color = "#14171a"

    # 4 optical apertures (left IR, IR projector, right IR, RGB) on front glass
    lenses = []
    for ly, lr in [(-32.5, 4.5), (-11.5, 4.5), (17.5, 4.5), (32.5, 3.8)]:
        lens = (
            bd.Pos(0.4, ly, 0.0)
            * bd.Rot(0, 90, 0)
            * bd.Cylinder(lr, 0.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        )
        lens.label = "d435_lens"
        lens.material = plastics.abs_()
        lens.color = "#2b3038"
        lenses.append(lens)

    return bd.Compound(children=[housing, glass, *lenses], label="realsense_d435")


@model
def assembly():
    # 0. Official ODrive BotWheel Explorer chassis (deck top at Z = 0, wheel axle at X = 0)
    robot = botwheel_robot().shape
    robot.label = "botwheel_explorer"

    # 1. Single-piece Synthara-style PC + LiDAR truss canopy (already in base_link frame)
    canopy = pc_lidar_canopy().shape
    canopy.label = "pc_lidar_canopy"

    # 2. STL mount plate sits on top of canopy PC cradle (X = PC_CENTER_X, Z = PC_TRAY_HEIGHT)
    stl_plate = bd.Pos(PC_CENTER_X, 0.0, PC_TRAY_HEIGHT) * _reference_um890_stl_plate()

    # 3. UM890 Pro Mini PC sits on top of STL plate
    um890 = bd.Pos(PC_CENTER_X, 0.0, PC_TRAY_HEIGHT + STL_THICKNESS) * _reference_um890_pc()

    # 4. SICK TiM781 LiDAR from vendor xbf locked on base_link Z-axis (X = 0, Y = 0, +X forward)
    lidar_raw = xbf.read(TIM781_XBF)
    lidar_z_shift = CANOPY_TOP_Z - LIDAR_BOTTOM_Z_LOCAL + 0.05
    lidar = bd.Pos(0.0, 0.0, lidar_z_shift) * bd.Rot(90, 0, 0) * lidar_raw
    lidar.label = "sick_tim781"

    # 5. Intel RealSense D435 (high & forward under LiDAR deck, tilted 15 deg down, front glass at X = +32 mm, Z = 72 mm)
    # Clears front PC I/O (Z = 14..57 mm open, 22 mm ahead of PC), stays 53 mm behind tire front (+85.6 mm)
    d435 = bd.Pos(32.0, 0.0, 72.0) * bd.Rot(0, 15, 0) * _reference_realsense_d435()
    d435.label = "realsense_d435"

    return bd.Compound(
        children=[robot, canopy, stl_plate, um890, lidar, d435],
        label="botwheel_pc_lidar_assembly",
    )


if __name__ == "__main__":
    assembly()
