# CTO Strategy Document
## Brine Spray Simulation Engine — Product Blueprint

**Version:** 1.0
**Date:** 2026-02-07
**Author:** CTO Office
**Status:** Draft for CEO Review

---

## 1. EXECUTIVE SUMMARY

### What We're Building
**Pre-installation design validation platform for road anti-icing systems.**

Engineers can simulate brine spray device placement on real Korean roads,
see coverage in 3D/satellite view, and get PASS/FAIL judgment —
all before a single hole is drilled.

### One-Line Pitch
> "현실이 알려주기 전에, 시뮬레이션이 먼저 실패를 보여주는 엔지니어링 판정 플랫폼"

### Why Now
- Korean government: Digital Twin National Land Platform 2025-2026 rollout
- Seoul: Autonomous Driving Vision 2030 — road infrastructure digitization
- Zero direct competitors in Korea for brine spray design simulation
- We already have a working prototype with core engine

---

## 2. MARKET ANALYSIS

### 2.1 Competitive Landscape

| Player | What They Do | What They DON'T Do |
|--------|-------------|-------------------|
| RITCO (리트코) | AI brine spray hardware + IoT monitoring | No design-phase simulation |
| Bentley OpenRoads | Road design BIM ($6K-$15K/yr) | No anti-icing module |
| Autodesk Civil 3D | Road design ($3K/yr) | No winter maintenance |
| COMSOL/ANSYS | General FEA/CFD ($5K-$40K/yr) | Not productized for brine spray |
| E8 Co. | Digital twin platform | Not domain-specific |

**Result: Zero direct competitors in our space.**

### 2.2 Target Customers (Priority Order)

| Tier | Customer | Pain Point | Deal Size |
|------|----------|-----------|-----------|
| 1 | Hardware companies (RITCO etc.) | Need design validation for clients | $10K-$50K/yr B2B |
| 2 | Korea Expressway Corp (한국도로공사) | 전국 고속도로 결빙 방지 최적화 | $50K-$200K/yr |
| 3 | Local governments (지자체) | Budget waste on ineffective installations | $5K-$20K/yr |
| 4 | Engineering consulting firms | Competitive edge in proposals | $3K-$10K/yr/seat |
| 5 | Research institutions (대학, 연구소) | R&D simulation tool | $1K-$5K/yr |

### 2.3 Revenue Model

**SaaS Subscription (Tiered)**

| Plan | Price | Target | Features |
|------|-------|--------|----------|
| **Starter** | Free | Researchers, students | 3 projects, L0 simulation, basic report |
| **Professional** | $99/mo ($1,188/yr) | Individual engineers | Unlimited projects, L0+L1, export |
| **Team** | $299/mo/team ($3,588/yr) | Engineering firms | 5 seats, shared projects, API access |
| **Enterprise** | Custom ($10K-$50K/yr) | 도로공사, 대기업 | SSO, custom rules, on-premise option |

**Year 1 Target:** 20 paying customers = $50K-$100K ARR
**Year 3 Target:** 200 customers = $500K-$1M ARR

---

## 3. PRODUCT ARCHITECTURE

### 3.1 System Overview

```
                    ┌─────────────────────────────────┐
                    │         CLIENT (Browser)         │
                    │                                  │
                    │  ┌──────────┐  ┌──────────────┐ │
                    │  │ Next.js  │  │ Three.js/R3F │ │
                    │  │ Dashboard│  │ 3D Simulation│ │
                    │  └────┬─────┘  └──────┬───────┘ │
                    │       │               │         │
                    │  ┌────┴───────────────┴───────┐ │
                    │  │     MapLibre GL JS          │ │
                    │  │   (Korean Road Maps)        │ │
                    │  └────────────┬────────────────┘ │
                    └──────────────┼──────────────────┘
                                   │
                          HTTPS / WebSocket
                                   │
                    ┌──────────────┼──────────────────┐
                    │         API GATEWAY              │
                    │        (Nginx/Traefik)           │
                    └──────┬──────────────┬───────────┘
                           │              │
              ┌────────────┴──┐    ┌──────┴────────────┐
              │   Next.js SSR │    │    FastAPI         │
              │   (Frontend)  │    │   (Backend API)    │
              │   Port 3000   │    │   Port 8000        │
              └───────────────┘    └──────┬────────────┘
                                          │
                          ┌───────────────┼───────────────┐
                          │               │               │
                   ┌──────┴──────┐ ┌──────┴─────┐ ┌──────┴──────┐
                   │   Celery    │ │   Redis    │ │ PostgreSQL  │
                   │  Workers    │ │  Cache/MQ  │ │ + PostGIS   │
                   │ (Simulation)│ │            │ │             │
                   └──────┬──────┘ └────────────┘ └─────────────┘
                          │
              ┌───────────┴────────────────┐
              │    SIMULATION ENGINE        │
              │                            │
              │  ┌─────────────────────┐   │
              │  │  neutral_model.py   │   │
              │  │  (Data Models)      │   │
              │  └─────────┬───────────┘   │
              │            │               │
              │  ┌─────────┴───────────┐   │
              │  │  gis_reality.py     │   │
              │  │  (Environment)      │   │
              │  └─────────┬───────────┘   │
              │            │               │
              │  ┌─────────┴───────────┐   │
              │  │  spray_simulation   │   │
              │  │  (Coverage Calc)    │   │
              │  └─────────┬───────────┘   │
              │            │               │
              │  ┌─────────┴───────────┐   │
              │  │  rule_engine.py     │   │
              │  │  (L0/L1 Judgment)   │   │
              │  └─────────┬───────────┘   │
              │            │               │
              │  ┌─────────┴───────────┐   │
              │  │  report_generator   │   │
              │  │  (PASS/FAIL Report) │   │
              │  └─────────────────────┘   │
              └────────────────────────────┘
```

### 3.2 Tech Stack Decision

| Layer | Choice | Reason |
|-------|--------|--------|
| Frontend | **Next.js 14+ (React + TypeScript)** | SSR, API routes, component architecture |
| 3D | **Three.js via React Three Fiber** | Lightweight, open-source, web-native |
| Maps | **MapLibre GL JS + VWorld tiles** | Free Korean government map tiles |
| Road View | **Kakao Maps API (Roadview)** | Korean road 360 panorama |
| Backend | **FastAPI + Uvicorn** | Async, fast, auto-docs, Python native |
| Task Queue | **Celery + Redis** | Long-running simulation jobs |
| Database | **PostgreSQL 16 + PostGIS 3.4** | Spatial queries, JSONB, enterprise |
| Auth | **NextAuth.js + Kakao Login** | Korean market + enterprise SSO |
| i18n | **react-i18next (ko/en)** | Korean/English runtime switching |
| Deploy | **Docker + AWS Seoul (ap-northeast-2)** | Korean data residency, low latency |
| CI/CD | **GitHub Actions** | Auto test/build/deploy |

### 3.3 API Design (Core Endpoints)

```
# Authentication
POST   /api/auth/login
POST   /api/auth/register
POST   /api/auth/kakao

# Projects
GET    /api/projects
POST   /api/projects
GET    /api/projects/{id}
PUT    /api/projects/{id}
DELETE /api/projects/{id}

# Road Segments
POST   /api/projects/{id}/roads
PUT    /api/projects/{id}/roads/{road_id}

# Spray Devices
POST   /api/projects/{id}/devices
PUT    /api/projects/{id}/devices/{device_id}
DELETE /api/projects/{id}/devices/{device_id}

# Simulation
POST   /api/projects/{id}/simulate
GET    /api/projects/{id}/simulation/status
GET    /api/projects/{id}/simulation/result
WS     /ws/projects/{id}/simulate   (real-time streaming)

# Environment
GET    /api/climate/presets
GET    /api/climate/realtime?lat={lat}&lng={lng}

# Reports
GET    /api/projects/{id}/report
GET    /api/projects/{id}/report/pdf

# GIS Data
GET    /api/gis/roads?bbox={bbox}
GET    /api/gis/utilities?bbox={bbox}
```

---

## 4. DATABASE SCHEMA

```sql
-- Users & Auth
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         VARCHAR(255) UNIQUE NOT NULL,
    name          VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255),
    provider      VARCHAR(50),  -- 'local', 'kakao', 'google'
    role          VARCHAR(20) DEFAULT 'engineer',
    org_id        UUID REFERENCES organizations(id),
    created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE organizations (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name       VARCHAR(200) NOT NULL,
    plan       VARCHAR(20) DEFAULT 'starter',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Projects
CREATE TABLE projects (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id      UUID REFERENCES users(id),
    org_id        UUID REFERENCES organizations(id),
    name          VARCHAR(200) NOT NULL,
    description   TEXT,
    location_name VARCHAR(200),
    location      GEOGRAPHY(POINT, 4326),  -- PostGIS
    status        VARCHAR(20) DEFAULT 'draft',
    created_at    TIMESTAMPTZ DEFAULT now(),
    updated_at    TIMESTAMPTZ DEFAULT now()
);

-- Road Segments (PostGIS geometry)
CREATE TABLE road_segments (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id       UUID REFERENCES projects(id) ON DELETE CASCADE,
    segment_id       VARCHAR(50) NOT NULL,
    road_type        VARCHAR(30) NOT NULL,
    surface_material VARCHAR(30) NOT NULL,
    geometry         GEOGRAPHY(LINESTRING, 4326),
    length_m         FLOAT NOT NULL,
    width_m          FLOAT NOT NULL,
    lanes            INT NOT NULL,
    slope_percent    FLOAT DEFAULT 0,
    elevation_m      FLOAT DEFAULT 0,
    properties       JSONB DEFAULT '{}'
);

-- Spray Devices
CREATE TABLE spray_devices (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id        UUID REFERENCES projects(id) ON DELETE CASCADE,
    device_id         VARCHAR(50) NOT NULL,
    position          GEOGRAPHY(POINT, 4326),
    position_along_m  FLOAT NOT NULL,
    position_cross_m  FLOAT DEFAULT 0,
    installation_type VARCHAR(30) NOT NULL,
    burial_depth_mm   FLOAT DEFAULT 0,
    spray_pattern     VARCHAR(20) NOT NULL,
    spray_angle_deg   FLOAT NOT NULL,
    spray_range_m     FLOAT NOT NULL,
    flow_rate_lpm     FLOAT NOT NULL,
    properties        JSONB DEFAULT '{}'
);

-- Supply Systems
CREATE TABLE supply_systems (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id         UUID REFERENCES projects(id) ON DELETE CASCADE,
    tank_capacity_l    FLOAT NOT NULL,
    pump_pressure_bar  FLOAT NOT NULL,
    pipe_diameter_mm   FLOAT NOT NULL,
    pipe_material      VARCHAR(50),
    pipe_burial_mm     FLOAT DEFAULT 0,
    has_heating        BOOLEAN DEFAULT false,
    has_insulation     BOOLEAN DEFAULT false
);

-- Underground Utilities
CREATE TABLE underground_utilities (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id       UUID REFERENCES projects(id) ON DELETE CASCADE,
    utility_type     VARCHAR(30) NOT NULL,
    depth_mm         FLOAT NOT NULL,
    position         GEOGRAPHY(LINESTRING, 4326),
    diameter_mm      FLOAT NOT NULL
);

-- Simulation Runs
CREATE TABLE simulation_runs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID REFERENCES projects(id) ON DELETE CASCADE,
    triggered_by    UUID REFERENCES users(id),
    climate_preset  VARCHAR(50),
    climate_data    JSONB NOT NULL,
    status          VARCHAR(20) DEFAULT 'queued',
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    result          JSONB,       -- SimulationResult
    judgment        JSONB,       -- JudgmentResult
    report_text     TEXT,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- Spatial indexes
CREATE INDEX idx_projects_location ON projects USING GIST(location);
CREATE INDEX idx_roads_geometry ON road_segments USING GIST(geometry);
CREATE INDEX idx_devices_position ON spray_devices USING GIST(position);
```

---

## 5. DEVELOPMENT ROADMAP

### Phase 0: Foundation (Current) -- DONE
- [x] Core simulation engine (Python)
- [x] Neutral Model JSON schema
- [x] L0 Rule-based judgment
- [x] CLI interface
- [x] Prototype visualizations (4 HTML files)
- [x] 9 passing tests
- [x] GitHub repository

### Phase 1: Backend Platform (Weeks 1-4)
**Goal: API-driven simulation with database**

| Week | Deliverable |
|------|------------|
| W1 | FastAPI project setup, Docker config, PostgreSQL+PostGIS |
| W2 | Auth (Kakao + email login), user/org CRUD |
| W3 | Project/device/road CRUD APIs, simulation trigger endpoint |
| W4 | WebSocket real-time simulation streaming, Celery workers |

**Exit Criteria:** `POST /api/projects/{id}/simulate` returns PASS/FAIL with full report

### Phase 2: Web Frontend (Weeks 5-8)
**Goal: Production-ready web application**

| Week | Deliverable |
|------|------------|
| W5 | Next.js project, auth flow, dashboard layout |
| W6 | Project editor: road segment + device placement on MapLibre |
| W7 | Three.js 3D simulation viewer (React Three Fiber migration) |
| W8 | Kakao Roadview integration, report PDF export, i18n (ko/en) |

**Exit Criteria:** Engineer can create project, place devices on map, run simulation, view 3D, get PDF report

### Phase 3: Production & First Customer (Weeks 9-12)
**Goal: Live service with real user**

| Week | Deliverable |
|------|------------|
| W9 | AWS deployment (Docker on ECS or EC2), domain, SSL |
| W10 | Korean weather API integration (기상청), real-time climate |
| W11 | L1 simplified physics: thermal model, drainage flow |
| W12 | Beta launch, first customer onboarding |

**Exit Criteria:** 1 paying customer (or signed LOI)

### Phase 4: Growth (Months 4-6)
- Korean Road DB (국가교통DB) integration
- Team collaboration features
- Enterprise SSO (SAML)
- Mobile-responsive UI
- API documentation for B2B integration
- Marketing site

### Phase 5: Scale (Months 7-12)
- L2 external simulation integration (OpenFOAM)
- AI-assisted device placement recommendation (Gemini API)
- Digital Twin platform integration (MOLIT alignment)
- International expansion (Japan, Northern Europe)
- SOC 2 compliance for enterprise

---

## 6. FOLDER STRUCTURE (Target)

```
brine-spray-sim/
├── README.md
├── LICENSE
├── docker-compose.yml
├── .github/
│   └── workflows/
│       ├── ci.yml                # Test on every PR
│       └── deploy.yml            # Deploy on merge to main
│
├── backend/                      # FastAPI
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic/                  # DB migrations
│   │   └── versions/
│   ├── app/
│   │   ├── main.py               # FastAPI app
│   │   ├── config.py             # Settings (env vars)
│   │   ├── database.py           # SQLAlchemy + PostGIS
│   │   ├── auth/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   └── schemas.py
│   │   ├── projects/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── schemas.py
│   │   │   └── models.py
│   │   ├── simulation/
│   │   │   ├── router.py         # POST /simulate, WS /ws/simulate
│   │   │   ├── service.py
│   │   │   └── tasks.py          # Celery tasks
│   │   ├── gis/
│   │   │   ├── router.py
│   │   │   └── service.py
│   │   └── reports/
│   │       ├── router.py
│   │       └── pdf_generator.py
│   │
│   └── engine/                   # Core simulation (migrated from src/)
│       ├── neutral_model.py
│       ├── gis_reality.py
│       ├── spray_simulation.py
│       ├── rule_engine.py
│       └── report_generator.py
│
├── frontend/                     # Next.js
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── public/
│   │   └── locales/
│   │       ├── ko/translation.json
│   │       └── en/translation.json
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx          # Landing
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx
│   │   │   ├── projects/
│   │   │   │   ├── page.tsx      # Project list
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx  # Project editor
│   │   │   │       ├── simulate/
│   │   │   │       │   └── page.tsx
│   │   │   │       └── report/
│   │   │   │           └── page.tsx
│   │   │   └── auth/
│   │   │       ├── login/page.tsx
│   │   │       └── register/page.tsx
│   │   ├── components/
│   │   │   ├── map/
│   │   │   │   ├── MapView.tsx        # MapLibre
│   │   │   │   ├── DevicePlacer.tsx   # Drag-drop devices
│   │   │   │   └── CoverageOverlay.tsx
│   │   │   ├── simulation/
│   │   │   │   ├── Scene3D.tsx        # React Three Fiber
│   │   │   │   ├── RoadModel.tsx
│   │   │   │   ├── SprayDevice3D.tsx
│   │   │   │   └── SnowParticles.tsx
│   │   │   ├── roadview/
│   │   │   │   └── KakaoRoadview.tsx
│   │   │   ├── report/
│   │   │   │   ├── JudgmentBadge.tsx
│   │   │   │   └── ReportView.tsx
│   │   │   └── ui/                    # shadcn/ui components
│   │   ├── hooks/
│   │   │   ├── useSimulation.ts
│   │   │   ├── useProject.ts
│   │   │   └── useWebSocket.ts
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   └── auth.ts
│   │   └── stores/
│   │       └── simulationStore.ts     # Zustand
│   └── tests/
│
├── tests/                        # Integration tests
│   ├── test_api.py
│   ├── test_simulation_e2e.py
│   └── conftest.py
│
└── docs/
    ├── CTO_STRATEGY.md           # This document
    ├── API.md                    # API documentation
    ├── DEPLOYMENT.md             # Deployment guide
    └── CONTRIBUTING.md
```

---

## 7. INFRASTRUCTURE COST ESTIMATE

### Year 1 (MVP + Early Customers)

| Service | Spec | Monthly Cost |
|---------|------|-------------|
| AWS EC2 (backend) | t3.medium (2 vCPU, 4GB) | $35 |
| AWS RDS PostgreSQL | db.t3.small + PostGIS | $30 |
| AWS ElastiCache (Redis) | cache.t3.micro | $15 |
| AWS S3 (reports, assets) | 50GB | $2 |
| Vercel (frontend) | Pro plan | $20 |
| Domain + SSL | brinesim.kr / brinesim.io | $3 |
| GitHub Actions | Free tier | $0 |
| Kakao Maps API | Free tier (daily 300K) | $0 |
| **Total** | | **~$105/mo ($1,260/yr)** |

### Year 2 (Growth)

| Service | Spec | Monthly Cost |
|---------|------|-------------|
| AWS ECS Fargate (backend) | 2 tasks | $80 |
| AWS RDS PostgreSQL | db.t3.medium | $65 |
| AWS ElastiCache | cache.t3.small | $30 |
| AWS S3 + CloudFront | CDN | $15 |
| Monitoring (Datadog) | Infrastructure | $25 |
| **Total** | | **~$215/mo ($2,580/yr)** |

**Break-even: 2 Professional customers ($99/mo x 2 = $198/mo)**

---

## 8. KEY RISKS & MITIGATIONS

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Small TAM (addressable market) | Revenue ceiling | Expand to broader anti-icing (heating wire, IoT) |
| Government procurement slow | Delayed revenue | Start with private engineering firms |
| RITCO builds their own | Direct competition | Partner first, differentiate on simulation depth |
| Simulation accuracy questioned | Trust issues | Validate against real installations, publish papers |
| One-person dev team | Slow progress | Focus on MVP, use AI coding assistants |
| API key leaks | Security breach | Environment variables, secrets management |

---

## 9. KEY METRICS (KPIs)

| Metric | Phase 1 Target | Phase 3 Target |
|--------|---------------|---------------|
| Simulations run | 100/month | 5,000/month |
| Registered users | 20 | 200 |
| Paying customers | 0 | 5 |
| API response time | <2s | <500ms |
| Test coverage | 60% | 80% |
| Uptime | 95% | 99.5% |

---

## 10. DECISION LOG

| # | Decision | Rationale | Date |
|---|----------|-----------|------|
| 1 | Python for simulation engine | Existing code, scientific ecosystem | 2026-02-07 |
| 2 | FastAPI over Django | Async, WebSocket native, lighter | 2026-02-07 |
| 3 | Next.js over plain React | SSR, API routes, Vercel deploy | 2026-02-07 |
| 4 | Three.js over Unity WebGL | Lighter (KB vs MB), open-source, web-native | 2026-02-07 |
| 5 | MapLibre over Google Maps | Free, open-source, Korean VWorld tiles | 2026-02-07 |
| 6 | PostgreSQL+PostGIS over MongoDB | Spatial queries, relational integrity | 2026-02-07 |
| 7 | AWS Seoul over NCP | Global scalability, better K8s support | 2026-02-07 |
| 8 | Kakao Login over Naver | Broader Korean user adoption | 2026-02-07 |
| 9 | Private repo first | API keys in code, pre-revenue | 2026-02-07 |
| 10 | MIT License | Open-core model potential | 2026-02-07 |

---

## 11. IMMEDIATE NEXT STEPS (CEO Action Required)

1. **Approve this strategy** — 이 방향이 맞는지 확인
2. **Domain decision** — brinesim.kr? brinesim.io? icesim.kr?
3. **AWS account** — 계정 생성 필요 (프리 티어 12개월)
4. **Kakao API key** — 이미 발급 완료 (e82f...)
5. **First customer target** — 누구에게 먼저 보여줄 것인가?
6. **Phase 1 착수 승인** — Backend API 개발 시작

---

*This document is a living strategy. Updated as decisions are made.*
