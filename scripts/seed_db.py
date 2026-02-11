"""Seed PostgreSQL with demo data for development."""

import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy import text


async def seed():
    from app.db.postgres import async_session
    from app.db.models import User, Project, Asset
    from app.auth.service import hash_password

    async with async_session() as db:
        # Create demo user
        user = User(
            id=uuid.uuid4(),
            email="demo@rcengine.io",
            name="Demo Engineer",
            password_hash=hash_password("demo1234"),
            role="admin",
        )
        db.add(user)
        await db.flush()

        # Create demo project
        project = Project(
            id=uuid.uuid4(),
            owner_id=user.id,
            name="Gangwon Expressway Anti-Icing System",
            description="Phase 1 MVP: Salt spray validation for mountain road curbs",
            safety_factor_target=1.5,
            location_code="GW-001",
            location_name="Gangwon-do Yeongdong Expressway KP 42.5",
            latitude=37.45,
            longitude=128.73,
            status="active",
        )
        db.add(project)
        await db.flush()

        # Create road segment
        road = Asset(
            project_id=project.id,
            type="road_segment",
            name="Mountain Pass Section A",
            geometry_json={"type": "LineString", "coordinates": [[128.73, 37.45], [128.74, 37.45]]},
            properties={
                "length": 200.0,
                "width": 7.0,
                "lanes": 2,
                "slope": 6.0,
                "surface_material": "asphalt",
                "elevation": 850.0,
            },
        )
        db.add(road)

        # Create spray devices
        for i in range(4):
            device = Asset(
                project_id=project.id,
                type="spray_device",
                name=f"Spray Nozzle {i+1}",
                geometry_json={"type": "Point", "coordinates": [128.73 + i * 0.002, 37.45]},
                properties={
                    "nozzle_diameter": 0.003,
                    "spray_angle": 60.0,
                    "flow_rate": 0.5,
                    "pump_pressure": 300000.0,
                    "brine_concentration": 23.0,
                    "mounting_height": 0.3,
                    "orientation": 90.0,
                },
            )
            db.add(device)

        await db.commit()
        print(f"Seeded: user={user.email}, project={project.name}")


if __name__ == "__main__":
    asyncio.run(seed())
