"""
MS11 Plugin Manager (scaffold)

Purpose
 - Discover plugins in the top-level `plugins/` directory
 - Read optional `plugin.json` manifests
 - Track enabled/disabled state in `data/plugins/enabled.json`
 - Provide simple metadata to the UI

Notes
 - This is a read/manage scaffold; it does not yet import or execute plugins.
 - Execution hooks can be added later (init/start/stop).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Optional


REPO_ROOT = Path(__file__).parents[2]
PLUGINS_DIR = REPO_ROOT / "plugins"
STATE_DIR = REPO_ROOT / "data" / "plugins"
STATE_DIR.mkdir(parents=True, exist_ok=True)
ENABLED_FILE = STATE_DIR / "enabled.json"


@dataclass
class PluginInfo:
    plugin_id: str
    name: str
    version: str = "0.1.0"
    description: str = ""
    author: str = ""
    enabled: bool = True
    path: str = ""


def _load_enabled_state() -> Dict[str, bool]:
    if ENABLED_FILE.exists():
        try:
            return json.loads(ENABLED_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_enabled_state(state: Dict[str, bool]) -> None:
    try:
        ENABLED_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception:
        pass


def _read_manifest(dir_path: Path) -> Optional[dict]:
    manifest_path = dir_path / "plugin.json"
    if manifest_path.exists():
        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def discover_plugins() -> List[PluginInfo]:
    enabled_state = _load_enabled_state()
    plugins: List[PluginInfo] = []
    if not PLUGINS_DIR.exists():
        return plugins

    for child in sorted(PLUGINS_DIR.iterdir()):
        if child.is_dir():
            manifest = _read_manifest(child) or {}
            plugin_id = manifest.get("id") or child.name
            plugins.append(
                PluginInfo(
                    plugin_id=plugin_id,
                    name=manifest.get("name") or child.name,
                    version=str(manifest.get("version") or "0.1.0"),
                    description=manifest.get("description") or "",
                    author=manifest.get("author") or "",
                    enabled=bool(enabled_state.get(plugin_id, True)),
                    path=str(child.relative_to(REPO_ROOT)),
                )
            )
        elif child.suffix in {".py"}:
            # single-file plugin (no manifest)
            plugin_id = child.stem
            plugins.append(
                PluginInfo(
                    plugin_id=plugin_id,
                    name=child.stem,
                    enabled=bool(enabled_state.get(plugin_id, True)),
                    path=str(child.relative_to(REPO_ROOT)),
                )
            )
    return plugins


def list_plugins() -> List[dict]:
    return [asdict(p) for p in discover_plugins()]


def set_enabled(plugin_id: str, enabled: bool) -> bool:
    state = _load_enabled_state()
    state[plugin_id] = enabled
    _save_enabled_state(state)
    return True


