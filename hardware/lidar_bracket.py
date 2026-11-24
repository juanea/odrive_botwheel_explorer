"""Elevated SICK TiM781 LiDAR bridge bracket for the ODrive BotWheel Explorer RevB.

Print orientation: Lying flat on its front face (robot +X = print +Z, robot +Y = print +X,
robot +Z = print +Y) so the entire arch, legs, and internal fillets print flat on the
build plate with ZERO overhangs and continuous filament along the load path.

In robot base_link frame (after rotating +90 deg about X and shifting X by -DEPTH/2):
  - Feet bolt to 30 x 30 mm M5 grid at Y = +/-90 mm, X = -30, 0, +30 mm (6x M5)
  - Inner opening: Y in [-76, +76] (152 mm wide), Z in [0, 98] (clears UM890 Pro)
  - Top mounting deck at Z = 106.0 mm (clears PC and rear E-stop for unobstructed 270 deg FOV)
  - 2x M3 counterbored holes at X = +1.00 mm, Y = +/-25.50 mm (5.0 mm web -> 2.5 mm engagement
    with M3x10 SHCS, respecting SICK TiM781 2.8 mm max screw-in depth).

Material: ABS (final, 100% infill) / PETG (prototyping), 0.4 mm nozzle.
Check: cad model dfm "$ID" --process printing --technology fdm --material abs --nozzle 0.4 --build-volume 256x256x260
"""

import build123d as bd
from bd_materials import plastics
from bd_materials.processes import fdm
from cad import model

from params import (
    LAYER_HEIGHT_MM,
    LIDAR_BRIDGE_CLEAR_Z,
    LIDAR_BRIDGE_DECK_THICKNESS,
    LIDAR_BRIDGE_DEPTH_X,
    LIDAR_BRIDGE_FOOT_THICKNESS,
    LIDAR_BRIDGE_INNER_SPAN_Y,
    LIDAR_BRIDGE_LEG_THICKNESS,
    LIDAR_BRIDGE_M5_XS,
    LIDAR_BRIDGE_M5_Y,
    LIDAR_BRIDGE_OUTER_Y,
    LIDAR_M3_CBORE_DIA,
    LIDAR_M3_CLEARANCE_DIA,
    LIDAR_M3_WEB_THICKNESS,
    LIDAR_M3_X,
    LIDAR_M3_Y,
    M5_CLEARANCE_DIA,
)

# Tunable parameters (plain literals so they can be tuned in the viewer)
CLEAR_HEIGHT = model.param("clear_height", 98.0, min=85.0, max=140.0, unit="mm")
INNER_SPAN = model.param("inner_span", 148.0, min=140.0, max=164.0, unit="mm")
DECK_THK = model.param("deck_thickness", 8.0, min=6.0, max=12.0, unit="mm")
DEPTH = model.param("bridge_depth", 76.0, min=68.0, max=96.0, unit="mm")


def build_lidar_bracket():
    """Return the LiDAR bridge oriented for support-free FDM printing.

    Print-frame mapping:
      print X = robot Y   (arch width, +/-102 mm = 204 mm)
      print Y = robot Z   (arch height, 0 to 106 mm)
      print Z = robot X + DEPTH/2  (extrusion depth, 0 to 76 mm)
    """
    half_inner = INNER_SPAN / 2.0                  # 74.0 mm
    leg_outer = half_inner + LIDAR_BRIDGE_LEG_THICKNESS  # 84.0 mm (6 mm clear to M5 bolt center at 90 mm)
    foot_outer = LIDAR_BRIDGE_OUTER_Y              # 102.0 mm
    foot_h = LIDAR_BRIDGE_FOOT_THICKNESS           # 8.0 mm
    top_y = CLEAR_HEIGHT + DECK_THK                # 106.0 mm
    gusset = 16.0                                  # 45-deg internal knee gussets

    # 1. Arch cross-section in print XY plane (extruded along print +Z)
    # Anticlockwise polygon so normal points +Z; flat foot shelf from 84..102 mm clears M5 heads cleanly
    pts = [
        # Right foot bottom -> outer edge -> top of foot
        (half_inner, 0.0),
        (foot_outer, 0.0),
        (foot_outer, foot_h),
        # Flat foot shelf straight to outer leg wall (leaves full clearance for M5 SHCS at Y=90 mm)
        (leg_outer, foot_h),
        # Up outer right leg to top deck
        (leg_outer, top_y),
        # Across top deck to outer left leg
        (-leg_outer, top_y),
        # Down outer left leg to left foot
        (-leg_outer, foot_h),
        (-foot_outer, foot_h),
        (-foot_outer, 0.0),
        (-half_inner, 0.0),
        # Up inner left leg with 45-deg knee gusset
        (-half_inner, CLEAR_HEIGHT - gusset),
        (-half_inner + gusset, CLEAR_HEIGHT),
        # Across underside of top deck to right knee gusset
        (half_inner - gusset, CLEAR_HEIGHT),
        (half_inner, CLEAR_HEIGHT - gusset),
    ]

    with bd.BuildSketch(bd.Plane.XY) as arch_sk:
        bd.Polygon(*pts, align=None)
    arch = bd.extrude(arch_sk.sketch, DEPTH)

    # 2. Cut 6x M5 mounting holes through the left & right feet
    # In print frame: hole axis is along print Y (robot Z)
    # Positions: print X = +/-90 mm (robot Y), print Z = DEPTH/2 + robot_x
    m5_cuts = []
    for sy in (-1, 1):
        px = sy * LIDAR_BRIDGE_M5_Y
        for rx in LIDAR_BRIDGE_M5_XS:
            pz = DEPTH / 2.0 + rx
            m5_cuts.append(
                bd.Pos(px, -1.0, pz)
                * bd.Rot(-90, 0, 0)
                * bd.Cylinder(
                    M5_CLEARANCE_DIA / 2.0,
                    foot_h + 2.0,
                    align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
                )
            )

    # 3. Cut 2x M3 mounting holes + underside counterbores for SICK TiM781
    # Robot coords: X = LIDAR_M3_X (+1.00), Y = +/-LIDAR_M3_Y (+/-25.50)
    # Print coords: print X = +/-25.50, print Z = DEPTH/2 + 1.00, axis along print Y
    m3_cuts = []
    cbore_depth = DECK_THK - LIDAR_M3_WEB_THICKNESS  # 8.0 - 5.0 = 3.0 mm
    assert cbore_depth >= 0.0, "DECK_THK must be >= LIDAR_M3_WEB_THICKNESS"
    for sy in (-1, 1):
        px = sy * LIDAR_M3_Y
        pz = DEPTH / 2.0 + LIDAR_M3_X
        # M3 through-hole through top deck
        m3_cuts.append(
            bd.Pos(px, CLEAR_HEIGHT - 1.0, pz)
            * bd.Rot(-90, 0, 0)
            * bd.Cylinder(
                LIDAR_M3_CLEARANCE_DIA / 2.0,
                DECK_THK + 2.0,
                align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
            )
        )
        # Underside counterbore so M3x10 SHCS engages 2.5 mm (<= 2.8 mm SICK limit)
        if cbore_depth > 0.1:
            m3_cuts.append(
                bd.Pos(px, CLEAR_HEIGHT - 0.5, pz)
                * bd.Rot(-90, 0, 0)
                * bd.Cylinder(
                    LIDAR_M3_CBORE_DIA / 2.0,
                    cbore_depth + 0.5,
                    align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
                )
            )

    # 4. Weight-reduction / cable-routing oval cutouts in both vertical legs (optional, 45-deg friendly)
    # Cut cleanly through print X (wait: leg faces are in YZ plane; cutting along X makes horizontal holes)
    # Keep solid 12 mm legs for maximum stiffness under ABS full infill / FEA!

    body = arch - (m5_cuts + m3_cuts)

    assert len(body.solids()) == 1, f"Expected 1 solid, got {len(body.solids())}"
    bb = body.bounding_box()
    assert bb.size.X <= 256.0 and bb.size.Y <= 256.0 and bb.size.Z <= 260.0, (
        f"Exceeds X2D build volume: {bb.size}"
    )

    body.label = "lidar_bracket"
    body.material = plastics.abs_(process=fdm(layer_height_mm=LAYER_HEIGHT_MM))
    body.color = "#2e7d6b"
    return body


@model
def lidar_bracket():
    return build_lidar_bracket()


if __name__ == "__main__":
    lidar_bracket()
