"""Shared parametric dimensions for the ODrive BotWheel Explorer RevB
Minisforum UM890 Pro + SICK TiM781 mounting brackets.

All units are in millimetres (mm).
Coordinate convention in assembly (ROS REP-103 base_link):
  +X : forward (270-deg LiDAR FOV center)
  +Y : left (along drive wheel axle)
  +Z : up (Z=0 is the top surface of the aluminum chassis deck)
"""

from pathlib import Path

HARDWARE_DIR = Path(__file__).resolve().parent
VENDOR_DIR = HARDWARE_DIR / "vendor"
EXPORTS_DIR = HARDWARE_DIR / "exports"

# External reference files
BOTWHEEL_XBF = VENDOR_DIR / "botwheel_explorer.xbf"
TIM781_XBF = VENDOR_DIR / "TIM781-2174101.xbf"
ZED_MINI_XBF = VENDOR_DIR / "zed_mini.xbf"
D435_STL = VENDOR_DIR / "d435.stl"
UM890_STL = Path("/home/juan/Desktop/UM890_PRO_table_mount_v3_lip.stl")

# --- Printer (Bambu Lab X2D, 0.4 mm nozzle) ---
NOZZLE_MM = 0.4
LAYER_HEIGHT_MM = 0.2
BUILD_VOLUME_MM = (256.0, 256.0, 260.0)

# --- Real ODrive BotWheel Explorer chassis (measured from botwheel_explorer.xbf) ---
# Frame 'Botwheel 2 Wheel Frame 500': 420.0 x 365.0 mm, 6.35 mm (1/4") plate
# Wheel track: 479.0 mm (centers at Y = +/-239.5 mm), wheel OD 171.3 mm (axle Z = -79.0 mm)
# Deck extends X = +25.0 mm (front) to X = -340.0 mm (rear caster tip), top at Z = 0.0 mm
# 110x Ø6.6 mm (M6 clearance) holes on 30 x 30 mm grid:
#   X_base_link: +10, -20, -50, -80, -110, -140, -170, -200, -230, -260 mm
#   Y_base_link: -180, -150, -120, -90, -60, -30, 0, +30, +60, +90, +120, +150, +180 mm
BOTWHEEL_RAW_AXLE_Y = 25.0
BOTWHEEL_RAW_DECK_TOP_Z = 165.35
GRID_PITCH = 30.0           # 30 x 30 mm hole grid (Ø6.6 mm M6 clearance on real chassis)
DECK_HOLE_X_OFFSET = 10.0   # Grid rows are at X = 10 - 30*k mm relative to wheel axle
M6_CLEARANCE_DIA = 6.6      # Real chassis deck hole diameter
M5_CLEARANCE_DIA = 5.4      # M5 screw clearance hole for FDM
M5_HEAD_CLEARANCE_DIA = 10.5

# --- Minisforum UM890 Pro + UM890_PRO_table_mount_v3_lip.stl ---
# Measured from UM890_PRO_table_mount_v3_lip.stl:
#   outer: 136.00 x 131.92 x 4.36 mm
#   inner cutout: 95.0 x 75.0 mm
#   2x M4 CSK holes centered on X, spaced 95.95 mm along Y
STL_OUTER_X = 136.0
STL_OUTER_Y = 131.92
STL_THICKNESS = 4.36
STL_INNER_X = 95.0
STL_INNER_Y = 75.0
STL_M4_HOLE_SPACING = 95.95

# UM890 Pro mini-PC envelope (sits on top of STL plate)
PC_WIDTH_X = 130.0
PC_DEPTH_Y = 127.0
PC_HEIGHT_Z = 66.6

# --- Single-piece PC + LiDAR Synthara Truss Canopy ---
# PC shifted back inside chassis (front edge X = +25 mm):
#   PC center at X = -80.0 mm -> PC front at X = -15.0 mm (40 mm gap), STL front at -12.0 mm (37 mm gap)
PC_CENTER_X = -80.0
PC_TRAY_HEIGHT = 10.0           # Deck to bottom of STL plate (fits 8.5 mm M4 inserts, lowers CG)
CANOPY_BOLT_XS = (10.0, -140.0) # Real deck grid rows: +10 mm (front), -140 mm (rear)
CANOPY_BOLT_Y = 90.0            # Real deck grid cols: +/-90 mm (24 mm clear of STL plate)
CHASSIS_BOLT_CLEARANCE_DIA = 6.6  # Matches Ø6.6 mm deck holes (tune to 8.4 mm if tapped M8 / 5/16-18)
CANOPY_CLEAR_Z = 88.0           # Underside of LiDAR deck (7.0 mm above PC top at 80.96 mm)
CANOPY_DECK_THICKNESS = 8.0     # Top of LiDAR deck at Z = 96.0 mm
CANOPY_TOP_Z = CANOPY_CLEAR_Z + CANOPY_DECK_THICKNESS

# Legacy / shared PC Bracket parameters
PC_BRACKET_HEIGHT = PC_TRAY_HEIGHT
PC_BRACKET_TAB_THICKNESS = 6.0  # Mounting ear thickness
PC_BRACKET_M5_X = 90.0
PC_BRACKET_M5_Y = 30.0
M4_INSERT_HOLE_DIA = 5.6        # Standard M4 heat-set brass insert bore
M4_INSERT_HOLE_DEPTH = 8.5      # Depth for M4x8.1 or M4x5.7 insert

# --- SICK TiM781 LiDAR ---
# Measured from TIM781-2174101.stp rotated +90 deg about X (upright):
#   bbox: X [-47.29, +29.00], Y [-30.70, +30.20], Z [-23.59, +62.24]
#   bottom flat face: Z = -23.56 mm
#   2x M3 tapped holes (axis -Z) at X = +1.00 mm, Y = +/-25.50 mm
#   recessed pocket floor at Z = -21.06 mm (2.50 mm above bottom face)
#   max screw-in depth: 2.8 mm per SICK datasheet
LIDAR_BOTTOM_Z_LOCAL = -23.56
LIDAR_M3_X = 1.00
LIDAR_M3_Y = 25.50
LIDAR_M3_RECESS = 2.50
LIDAR_M3_CLEARANCE_DIA = 3.4
LIDAR_M3_CBORE_DIA = 6.4        # DIN 912 M3 SHCS head is 5.5 mm
LIDAR_M3_WEB_THICKNESS = 5.0    # With M3x10 SHCS: 10 - 5.0 - 2.5 = 2.5 mm engagement (<= 2.8 mm)

# Elevated LiDAR Bridge parameters (clears UM890 Pro + rear E-stop)
LIDAR_BRIDGE_INNER_SPAN_Y = 148.0   # Clears 131.92 mm STL (8 mm/side) & 127 mm PC (10.5 mm/side)
LIDAR_BRIDGE_CLEAR_Z = 98.0         # Underside of top deck (~15 mm above PC top)
LIDAR_BRIDGE_DECK_THICKNESS = 8.0   # Top surface at Z = 106.0 mm
LIDAR_BRIDGE_TOP_Z = LIDAR_BRIDGE_CLEAR_Z + LIDAR_BRIDGE_DECK_THICKNESS
LIDAR_BRIDGE_LEG_THICKNESS = 10.0   # Outer leg at +/-84 mm -> 6 mm clear to M5 bolt center at +/-90 mm
LIDAR_BRIDGE_FOOT_THICKNESS = 8.0
LIDAR_BRIDGE_DEPTH_X = 76.0         # Covers X = -30, 0, +30 M5 bolts + TiM781 base
LIDAR_BRIDGE_M5_Y = 90.0            # +/-90 mm (6 grid pitches apart)
LIDAR_BRIDGE_M5_XS = (-30.0, 0.0, 30.0)
LIDAR_BRIDGE_OUTER_Y = 102.0        # +/-102 mm (204 mm total width, < 256 mm X2D bed)
