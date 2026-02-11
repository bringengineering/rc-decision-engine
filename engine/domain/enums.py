"""Core enumerations for the decision engine."""

from enum import Enum


class AssetType(str, Enum):
    ROAD_SEGMENT = "road_segment"
    SPRAY_DEVICE = "spray_device"
    SUPPLY_SYSTEM = "supply_system"
    BRIDGE_PIER = "bridge_pier"
    JET_FAN = "jet_fan"
    CURB = "curb"


class Verdict(str, Enum):
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


class SimulationType(str, Enum):
    SALT_SPRAY = "salt_spray"
    THERMAL = "thermal"
    STRUCTURAL = "structural"
    FLUID = "fluid"


class SensorType(str, Enum):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    WIND_SPEED = "wind_speed"
    WIND_DIRECTION = "wind_direction"
    STRAIN = "strain"
    DISPLACEMENT = "displacement"
    PRESSURE = "pressure"
    FLOW_RATE = "flow_rate"


class CalibrationStatus(str, Enum):
    UNCALIBRATED = "uncalibrated"
    CALIBRATED = "calibrated"
    DRIFTING = "drifting"
    RECALIBRATING = "recalibrating"
