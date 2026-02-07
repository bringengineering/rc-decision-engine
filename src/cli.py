"""
Brine Spray Simulation Engine — CLI Interface
Usage:
    python -m src.cli run examples/demo_gangwon_road.py
    python -m src.cli serve
    python -m src.cli version
"""

import argparse
import sys
import os
import webbrowser
import http.server
import threading

from src.models.neutral_model import SimulationProject
from src.layers.gis_reality import (
    EnvironmentContext, Season, TimeOfDay, TrafficLevel,
    KOREA_CLIMATE_PRESETS, estimate_ice_formation_risk,
)
from src.simulation.spray_simulation import run_full_simulation
from src.judgment.rule_engine import evaluate
from src.report.report_generator import generate_report

VERSION = "0.1.0"
BANNER = f"""
╔══════════════════════════════════════════════════════════╗
║   Brine Spray Simulation Engine  v{VERSION}               ║
║   Problem-Driven BIM Simulation                         ║
║   "Engineering ideas must survive reality"              ║
╚══════════════════════════════════════════════════════════╝
"""


def cmd_version(args):
    print(f"brine-spray-sim v{VERSION}")


def cmd_run(args):
    """JSON 프로젝트 파일로 시뮬레이션 실행"""
    print(BANNER)

    json_path = args.project
    if not os.path.exists(json_path):
        print(f"[ERROR] File not found: {json_path}")
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        project = SimulationProject.from_json(f.read())

    # 환경 프리셋 선택
    preset_key = args.climate or "gangwon_winter_night"
    if preset_key not in KOREA_CLIMATE_PRESETS:
        print(f"[ERROR] Unknown climate preset: {preset_key}")
        print(f"Available: {', '.join(KOREA_CLIMATE_PRESETS.keys())}")
        sys.exit(1)

    climate = KOREA_CLIMATE_PRESETS[preset_key]
    env = EnvironmentContext(
        location_name=project.location_name,
        latitude=project.latitude,
        longitude=project.longitude,
        elevation_m=project.road_segments[0].elevation_m if project.road_segments else 0,
        season=Season.WINTER,
        time_of_day=TimeOfDay.NIGHT,
        climate=climate,
        traffic_level=TrafficLevel.LOW,
    )

    print(f"[1/4] Project loaded: {project.project_name}")
    print(f"[2/4] Environment: {preset_key}")

    ice_risk = estimate_ice_formation_risk(env.climate)
    print(f"       Ice formation risk: {ice_risk:.0%}")

    print("[3/4] Running simulation...")
    sim_result = run_full_simulation(project, env, resolution_m=1.0)
    print(f"       Coverage: {sim_result.coverage_ratio:.1%}")

    print("[4/4] Evaluating...")
    judgment = evaluate(project, env, sim_result)

    report = generate_report(project, env, sim_result, judgment)
    print()
    print(report)

    # 리포트 파일 저장
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\nReport saved to: {args.output}")


def cmd_serve(args):
    """웹 시뮬레이션 서버 실행"""
    print(BANNER)
    port = args.port or 8080
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    os.chdir(root)
    handler = http.server.SimpleHTTPRequestHandler
    server = http.server.HTTPServer(("", port), handler)

    print(f"[SERVER] Running at http://localhost:{port}")
    print(f"[SERVER] Available simulations:")
    print(f"         http://localhost:{port}/simulation.html        — 2D Canvas")
    print(f"         http://localhost:{port}/map_simulation.html    — Satellite Map")
    print(f"         http://localhost:{port}/simulation3d.html      — 3D Walk View")
    print(f"         http://localhost:{port}/roadview_sim.html      — Road View + Map + 3D")
    print(f"[SERVER] Press Ctrl+C to stop")

    if not args.no_browser:
        url = f"http://localhost:{port}/roadview_sim.html"
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[SERVER] Stopped.")
        server.server_close()


def cmd_demo(args):
    """내장 데모 시나리오 실행"""
    print(BANNER)
    # demo_gangwon_road를 직접 실행
    demo_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "examples"
    )
    demo_script = os.path.join(demo_dir, "demo_gangwon_road.py")
    if os.path.exists(demo_script):
        os.system(f'python "{demo_script}"')
    else:
        print("[ERROR] Demo script not found.")


def main():
    parser = argparse.ArgumentParser(
        prog="brine-sim",
        description="Brine Spray Simulation Engine — Problem-Driven BIM Simulation",
    )
    sub = parser.add_subparsers(dest="command")

    # version
    p_ver = sub.add_parser("version", help="Show version")
    p_ver.set_defaults(func=cmd_version)

    # run
    p_run = sub.add_parser("run", help="Run simulation from JSON project file")
    p_run.add_argument("project", help="Path to project JSON file")
    p_run.add_argument("--climate", help="Climate preset (e.g. gangwon_winter_night)")
    p_run.add_argument("--output", "-o", help="Save report to file")
    p_run.set_defaults(func=cmd_run)

    # serve
    p_serve = sub.add_parser("serve", help="Start web simulation server")
    p_serve.add_argument("--port", type=int, default=8080, help="Port number (default: 8080)")
    p_serve.add_argument("--no-browser", action="store_true", help="Don't open browser")
    p_serve.set_defaults(func=cmd_serve)

    # demo
    p_demo = sub.add_parser("demo", help="Run built-in demo scenario")
    p_demo.set_defaults(func=cmd_demo)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
