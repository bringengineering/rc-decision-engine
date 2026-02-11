"""Test configuration and fixtures."""

import pytest


@pytest.fixture
def sample_road_segment():
    """Sample road segment asset for testing."""
    from engine.domain.models import PhysicsAsset
    from engine.domain.enums import AssetType
    return PhysicsAsset(
        id="road-001",
        type=AssetType.ROAD_SEGMENT,
        name="Test Road Segment",
        properties={
            "length": 100.0,
            "width": 7.0,
            "lanes": 2,
            "slope": 2.0,
            "surface_material": "asphalt",
        },
    )


@pytest.fixture
def sample_spray_device():
    """Sample spray device asset for testing."""
    from engine.domain.models import PhysicsAsset
    from engine.domain.enums import AssetType
    return PhysicsAsset(
        id="spray-001",
        type=AssetType.SPRAY_DEVICE,
        name="Test Spray Device",
        properties={
            "nozzle_diameter": 0.003,
            "spray_angle": 60.0,
            "flow_rate": 0.5,
            "pump_pressure": 300000.0,
            "brine_concentration": 23.0,
            "mounting_height": 0.3,
            "orientation": 0.0,
        },
    )


@pytest.fixture
def sample_environment():
    """Sample winter environment for testing."""
    from engine.domain.models import EnvironmentCondition
    return EnvironmentCondition(
        temperature=-5.0,
        humidity=70.0,
        wind_speed=4.0,
        wind_direction=270.0,
        precipitation=2.0,
        solar_radiation=100.0,
    )


@pytest.fixture
def sample_assets(sample_road_segment, sample_spray_device):
    """Combined list of road + spray assets."""
    return [sample_road_segment, sample_spray_device]
