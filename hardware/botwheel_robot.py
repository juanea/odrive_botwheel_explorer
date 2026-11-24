"""Imported official ODrive BotWheel Explorer CAD model (from Onshape publication V39).

Aligned to ROS REP-103 base_link:
  +X : forward (wheel end; front edge of deck at X = +25.0 mm, rear tip at X = -340.0 mm)
  +Y : left (drive wheel axle centered at X = 0.0 mm, Y = +/-239.5 mm, Z = -79.0 mm)
  +Z : up (top surface of 6.35 mm aluminum deck at Z = 0.0 mm, ground at Z = -164.65 mm)

Deck mounting hole grid (110x Ø6.6 mm M6 clearance holes, 30 x 30 mm pitch):
  X = +10, -20, -50, -80, -110, -140, -170, -200, -230, -260 mm
  Y = -180, -150, -120, -90, -60, -30, 0, +30, +60, +90, +120, +150, +180 mm
"""

import build123d as bd
from cad import model, xbf

from params import BOTWHEEL_RAW_AXLE_Y, BOTWHEEL_RAW_DECK_TOP_Z, BOTWHEEL_XBF


@model
def botwheel_robot():
    raw = xbf.read(BOTWHEEL_XBF)
    # Raw Onshape frame: -Y is forward (wheels at Y=25), +X is left, deck top at Z=165.35.
    # Rot(0, 0, 90) maps -Y -> +X (forward) and +X -> +Y (left); Pos shifts axle to X=0 and deck top to Z=0.
    robot = bd.Pos(BOTWHEEL_RAW_AXLE_Y, 0.0, -BOTWHEEL_RAW_DECK_TOP_Z) * bd.Rot(0, 0, 90) * raw
    robot.label = "botwheel_explorer"
    return robot


if __name__ == "__main__":
    botwheel_robot()
