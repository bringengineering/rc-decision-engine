"""Physical constants and KDS (Korean Design Standards) thresholds."""

import math

# ===== Physical Constants =====
GRAVITY = 9.81  # m/s^2
AIR_DENSITY = 1.225  # kg/m^3 at 15°C, sea level
WATER_DENSITY = 1000.0  # kg/m^3
BRINE_DENSITY_23PCT = 1170.0  # kg/m^3 (23% NaCl solution)

# NaCl Brine Properties
NACL_EUTECTIC_TEMP = -21.1  # °C (eutectic point of NaCl-water)
NACL_EUTECTIC_CONC = 23.3  # % weight
BRINE_VISCOSITY = 1.8e-3  # Pa·s (23% NaCl at 0°C)
BRINE_SURFACE_TENSION = 0.076  # N/m

# Thermal Properties
ASPHALT_THERMAL_CONDUCTIVITY = 0.75  # W/(m·K)
ASPHALT_SPECIFIC_HEAT = 920.0  # J/(kg·K)
ASPHALT_DENSITY = 2360.0  # kg/m^3
ICE_LATENT_HEAT = 334000.0  # J/kg
STEFAN_BOLTZMANN = 5.67e-8  # W/(m^2·K^4)

# Drag Coefficients
SPHERE_DRAG_COEFF = 0.47
DROPLET_DRAG_COEFF = 0.44  # For small spherical droplets

# ===== KDS (Korean Design Standards) Thresholds =====
# KDS 24 10 10 — Road Design Standards
KDS_MIN_SAFETY_FACTOR = 1.5  # Default minimum safety factor
KDS_ROAD_FRICTION_MIN = 0.3  # Minimum friction coefficient (wet)
KDS_ROAD_FRICTION_DRY = 0.6  # Standard dry friction
KDS_MAX_SLOPE_ICE = 8.0  # % — max slope for icing conditions
KDS_MIN_BRINE_COVERAGE = 0.85  # 85% minimum coverage ratio

# Temperature Thresholds
FREEZING_POINT_WATER = 0.0  # °C
ICE_WARNING_TEMP = 3.0  # °C — warning when surface temp drops below
ICE_CRITICAL_TEMP = -5.0  # °C — critical icing condition

# ===== Decision Thresholds =====
MONTE_CARLO_N = 1000  # Default number of samples
FAIL_PROBABILITY_THRESHOLD = 0.20  # Pf >= 20% → FAIL
FAIL_SAFETY_FACTOR_THRESHOLD = 1.0  # SF < 1.0 → FAIL
PASS_SAFETY_FACTOR_TARGET = 1.5  # SF >= 1.5 → PASS
UCL_CONFIDENCE = 0.95  # 95% confidence level

# ===== Calibration Thresholds =====
DRIFT_THRESHOLD_PCT = 5.0  # Trigger re-calibration when drift > 5%
DRIFT_SUSTAINED_MINUTES = 10  # Must sustain for > 10 minutes
CALIBRATION_LAMBDA = 0.1  # Weight for sensor loss in PINNs: L_total = L_physics + λ·L_sensor

# ===== Spray System Parameters =====
DEFAULT_NOZZLE_DIAMETER = 0.003  # 3mm
DEFAULT_SPRAY_ANGLE = 60.0  # degrees
DEFAULT_FLOW_RATE = 0.5  # L/min
DEFAULT_PUMP_PRESSURE = 300000.0  # Pa (3 bar)
SPRAY_VELOCITY_COEFF = 0.95  # Nozzle velocity coefficient (Cv)
