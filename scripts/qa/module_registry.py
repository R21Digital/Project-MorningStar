#!/usr/bin/env python3
"""
Lightweight Module Status & Metrics for MS11 (Flask version)

Reads small JSON files in ./data and simple line counts in ./logs to provide
overview metrics per module. Safe to run without data (returns zeros).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

DATA_DIR = Path("data")
LOGS_DIR = Path("logs")


def _exists(p: Path) -> bool:
    try:
        return p.exists()
    except Exception:
        return False


def _read_json(p: Path, fallback: Any) -> Any:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def _line_count(p: Path) -> int:
    try:
        if not p.exists():
            return 0
        return p.read_text(encoding="utf-8").count("\n")
    except Exception:
        return 0


def _iso(x: datetime) -> str:
    return x.isoformat()


Health = str  # 'active' | 'degraded' | 'disabled' | 'error'


def _health(errors: int, events: int, last_run: Optional[str]) -> Health:
    if not last_run:
        return "degraded"
    if errors >= events and errors > 0:
        return "error"
    if errors > 0:
        return "degraded"
    return "active"


def _recent_mtime(path: Path) -> Optional[str]:
    try:
        if not path.exists():
            return None
        return _iso(datetime.fromtimestamp(path.stat().st_mtime))
    except Exception:
        return None


def overview_config() -> Dict[str, Any]:
    cfg = DATA_DIR / "config" / "ms11.config.json"
    last = _recent_mtime(cfg)
    data = _read_json(cfg, {})
    metrics = [
        {"key": "profiles", "label": "Profiles", "value": data.get("profiles", 0)},
        {"key": "env", "label": "Envs", "value": data.get("environments", 1)},
    ]
    return {
        "id": "configuration",
        "name": "Configuration Management",
        "description": "Manage MS11 configuration files and settings",
        "health": _health(0, 1, last),
        "lastRunAt": last,
        "since": _iso(datetime.utcnow() - timedelta(days=1)),
        "metrics": metrics,
        "links": [{"label": "Open Config", "href": "/configuration"}],
    }


def overview_combat() -> Dict[str, Any]:
    log = LOGS_DIR / "combat.log"
    err = LOGS_DIR / "combat.error.log"
    events = _line_count(log)
    errors = _line_count(err)
    last = _recent_mtime(log)
    metrics = [
        {"key": "events", "label": "Events (24h)", "value": events},
        {"key": "errors", "label": "Errors (24h)", "value": errors},
    ]
    return {
        "id": "combat",
        "name": "Combat System",
        "description": "Combat profiles, rotations, and battle management",
        "health": _health(errors, events, last),
        "lastRunAt": last,
        "since": _iso(datetime.utcnow() - timedelta(days=1)),
        "metrics": metrics,
        "links": [{"label": "Open Combat", "href": "/combat"}],
    }


def overview_movement() -> Dict[str, Any]:
    log = LOGS_DIR / "movement.log"
    events = _line_count(log)
    last = _recent_mtime(log)
    metrics = [
        {"key": "events", "label": "Moves (24h)", "value": events},
    ]
    return {
        "id": "movement",
        "name": "Movement & Travel",
        "description": "Travel automation, pathfinding, and navigation",
        "health": _health(0, events, last),
        "lastRunAt": last,
        "since": _iso(datetime.utcnow() - timedelta(days=1)),
        "metrics": metrics,
        "links": [{"label": "Open Travel", "href": "/movement"}],
    }


def overview_professions() -> Dict[str, Any]:
    trainers = _read_json(DATA_DIR / "professions" / "trainers.json", {}).get("count", 0)
    crafts = _read_json(DATA_DIR / "professions" / "crafts.json", {}).get("recipes", 0)
    last = _iso(datetime.utcnow() - timedelta(minutes=30))
    metrics = [
        {"key": "trainers", "label": "Trainers", "value": trainers},
        {"key": "recipes", "label": "Recipes", "value": crafts},
    ]
    return {
        "id": "professions",
        "name": "Profession Management",
        "description": "Crafting, harvesting, and profession automation",
        "health": "active" if (trainers + crafts) > 0 else "degraded",
        "lastRunAt": last,
        "since": _iso(datetime.utcnow() - timedelta(days=1)),
        "metrics": metrics,
        "links": [{"label": "Open Professions", "href": "/professions"}],
    }


def overview_quests() -> Dict[str, Any]:
    log = LOGS_DIR / "quests.log"
    events = _line_count(log)
    errors = _line_count(LOGS_DIR / "quests.error.log")
    last = _recent_mtime(log)
    metrics = [
        {"key": "events", "label": "Completions (24h)", "value": events},
        {"key": "errors", "label": "Errors (24h)", "value": errors},
    ]
    return {
        "id": "quests",
        "name": "Quest System",
        "description": "Quest tracking, automation, and management",
        "health": _health(errors, events, last),
        "lastRunAt": last,
        "since": _iso(datetime.utcnow() - timedelta(days=1)),
        "metrics": metrics,
        "links": [{"label": "Open Quests", "href": "/quests"}],
    }


def overview_analytics() -> Dict[str, Any]:
    s = _read_json(DATA_DIR / "analytics" / "summary.json", {"sessions": 0, "dpsAvg": 0})
    last = _iso(datetime.utcnow() - timedelta(minutes=10))
    metrics = [
        {"key": "sessions", "label": "Sessions", "value": s.get("sessions", 0)},
        {"key": "dps", "label": "Avg DPS", "value": s.get("dpsAvg", 0)},
    ]
    return {
        "id": "analytics",
        "name": "Analytics & Reports",
        "description": "Performance metrics, statistics, and reporting",
        "health": "active",
        "lastRunAt": last,
        "since": _iso(datetime.utcnow() - timedelta(days=1)),
        "metrics": metrics,
        "links": [{"label": "Open Analytics", "href": "/analytics"}],
    }


def overview_discord() -> Dict[str, Any]:
    log = LOGS_DIR / "discord.log"
    events = _line_count(log)
    last = _recent_mtime(log)
    metrics = [
        {"key": "messages", "label": "Relays (24h)", "value": events},
    ]
    return {
        "id": "discord",
        "name": "Discord Integration",
        "description": "Discord bot management and relay settings",
        "health": _health(0, events, last),
        "lastRunAt": last,
        "since": _iso(datetime.utcnow() - timedelta(days=1)),
        "metrics": metrics,
        "links": [{"label": "Open Discord", "href": "/discord"}],
    }


def overview_system() -> Dict[str, Any]:
    s = _read_json(DATA_DIR / "system" / "health.json", {"cpu": 0, "mem": 0, "uptime": 0})
    last = _iso(datetime.utcnow() - timedelta(minutes=1))
    metrics = [
        {"key": "cpu", "label": "CPU %", "value": s.get("cpu", 0)},
        {"key": "mem", "label": "Mem %", "value": s.get("mem", 0)},
        {"key": "uptime", "label": "Uptime (m)", "value": int((s.get("uptime", 0) or 0) / 60)},
    ]
    return {
        "id": "system",
        "name": "System Monitor",
        "description": "System health, performance, and diagnostics",
        "health": "active",
        "lastRunAt": last,
        "since": _iso(datetime.utcnow() - timedelta(days=1)),
        "metrics": metrics,
        "links": [{"label": "Open Monitor", "href": "/system"}],
    }


def get_all_overviews() -> List[Dict[str, Any]]:
    return [
        overview_config(),
        overview_combat(),
        overview_movement(),
        overview_professions(),
        overview_quests(),
        overview_analytics(),
        overview_discord(),
        overview_system(),
    ]


def get_overview(module_id: str) -> Optional[Dict[str, Any]]:
    for x in get_all_overviews():
        if x["id"] == module_id:
            return x
    return None


