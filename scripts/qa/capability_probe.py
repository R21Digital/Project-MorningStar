#!/usr/bin/env python3
"""
Capability Probe Service for MS11

Collects runtime facts (mounts, UI env, skills, inventory stubs) automatically
and caches them for other components to consume. Designed to be resilient: all
probes are optional and failures are logged but do not crash callers.
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, List, Optional


# Optional imports – each probe guards its own dependencies
try:
    from movement.mount_manager import (
        get_mount_manager,
        detect_mounts as mm_detect_mounts,
    )
    MOUNTS_AVAILABLE = True
except Exception:
    get_mount_manager = None  # type: ignore
    mm_detect_mounts = None  # type: ignore
    MOUNTS_AVAILABLE = False


RUNTIME_DIR = Path("profiles/runtime")
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class MountsInfo:
    # Mounts detected from OCR/command parsing but not yet verified by mount attempt
    detected_unverified: List[str] = field(default_factory=list)
    # Mounts verified by an actual successful mount attempt (or system-confirmed)
    learned_verified: List[str] = field(default_factory=list)
    best_suggestion: Optional[str] = None
    last_probe_ts: float = 0.0


@dataclass
class UIInfo:
    resolution: Optional[str] = None
    ui_scale: Optional[float] = None
    language: Optional[str] = None
    last_probe_ts: float = 0.0


@dataclass
class SkillsInfo:
    learned_skills: List[str] = field(default_factory=list)
    last_probe_ts: float = 0.0


@dataclass
class InventoryInfo:
    essentials: Dict[str, Any] = field(default_factory=dict)
    last_probe_ts: float = 0.0


@dataclass
class Capabilities:
    mounts: MountsInfo = field(default_factory=MountsInfo)
    ui: UIInfo = field(default_factory=UIInfo)
    skills: SkillsInfo = field(default_factory=SkillsInfo)
    inventory: InventoryInfo = field(default_factory=InventoryInfo)
    version: str = "1.0"


class CapabilityProbe:
    """Aggregate runtime capability information with TTL-based refresh."""

    def __init__(self, ttl_seconds: int = 900) -> None:
        self._lock = threading.RLock()
        self.ttl = max(ttl_seconds, 60)
        self._character: str = self._detect_default_character()
        self.data: Capabilities = self._load_file()
        self._running = False

    # ---------- Persistence ----------
    def _capabilities_path(self) -> Path:
        safe = (self._character or "default").replace("/", "_").replace("\\", "_")
        return RUNTIME_DIR / f"{safe}_capabilities.json"

    def _load_file(self) -> Capabilities:
        path = self._capabilities_path()
        if path.exists():
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                return self._from_dict(raw)
            except Exception:
                pass
        return Capabilities()

    def _save_file(self) -> None:
        try:
            self._capabilities_path().write_text(
                json.dumps(self.to_dict(), indent=2), encoding="utf-8"
            )
        except Exception:
            pass

    def to_dict(self) -> Dict[str, Any]:
        with self._lock:
            return asdict(self.data)

    def _from_dict(self, raw: Dict[str, Any]) -> Capabilities:
        def get(d: Dict[str, Any], k: str, default: Any) -> Any:
            v = d.get(k)
            return v if isinstance(v, type(default)) or v is None else default

        try:
            mounts_raw = raw.get("mounts", {})
            ui_raw = raw.get("ui", {})
            skills_raw = raw.get("skills", {})
            inv_raw = raw.get("inventory", {})
            return Capabilities(
                mounts=MountsInfo(
                    detected_unverified=list(mounts_raw.get("detected_unverified", []) or []),
                    learned_verified=list(mounts_raw.get("learned_verified", []) or []),
                    best_suggestion=mounts_raw.get("best_suggestion"),
                    last_probe_ts=float(mounts_raw.get("last_probe_ts", 0.0)),
                ),
                ui=UIInfo(
                    resolution=ui_raw.get("resolution"),
                    ui_scale=ui_raw.get("ui_scale"),
                    language=ui_raw.get("language"),
                    last_probe_ts=float(ui_raw.get("last_probe_ts", 0.0)),
                ),
                skills=SkillsInfo(
                    learned_skills=list(skills_raw.get("learned_skills", []) or []),
                    last_probe_ts=float(skills_raw.get("last_probe_ts", 0.0)),
                ),
                inventory=InventoryInfo(
                    essentials=dict(inv_raw.get("essentials", {}) or {}),
                    last_probe_ts=float(inv_raw.get("last_probe_ts", 0.0)),
                ),
                version=str(raw.get("version", "1.0")),
            )
        except Exception:
            return Capabilities()

    # ---------- Probes ----------
    def probe_mounts(self, *, verify: bool = False) -> None:
        if not MOUNTS_AVAILABLE:
            return
        try:
            detected: List[str] = []
            # Primary method
            try:
                result = mm_detect_mounts()
                # mount_manager.detect_mounts returns a List[str]
                if isinstance(result, list):
                    detected = list({m.lower() for m in result})
                elif isinstance(result, dict) and "mounts_found" in result:
                    detected = list({m.lower() for m in result.get("mounts_found", [])})
            except Exception:
                detected = []

            best: Optional[str] = None
            try:
                manager = get_mount_manager()
                best = manager.get_best_mount()  # type: ignore[attr-defined]
            except Exception:
                best = None

            with self._lock:
                # Merge unverified detections
                existing_unverified = set(self.data.mounts.detected_unverified)
                existing_verified = set(self.data.mounts.learned_verified)
                new_unverified = set(detected) - existing_verified
                self.data.mounts.detected_unverified = sorted(existing_unverified | new_unverified)
                self.data.mounts.best_suggestion = best
                self.data.mounts.last_probe_ts = time.time()
        finally:
            self._save_file()

        # Optional verification step – confirm which mounts can actually be used
        if verify and MOUNTS_AVAILABLE:
            try:
                manager = get_mount_manager()
                verified: List[str] = []
                for name in list(self.data.mounts.detected_unverified):
                    try:
                        # Attempt to mount, then immediately dismount; if successful mark verified
                        if manager.mount_creature(name):  # type: ignore[attr-defined]
                            verified.append(name)
                            try:
                                manager.dismount_creature()  # type: ignore[attr-defined]
                            except Exception:
                                pass
                    except Exception:
                        continue
                if verified:
                    with self._lock:
                        vset = set(self.data.mounts.learned_verified)
                        vset.update(verified)
                        self.data.mounts.learned_verified = sorted(vset)
                        # remove from unverified
                        u = set(self.data.mounts.detected_unverified) - set(verified)
                        self.data.mounts.detected_unverified = sorted(u)
                    self._save_file()
            except Exception:
                pass

    def probe_ui(self) -> None:
        # Placeholder: wire in real UI size/scale later
        with self._lock:
            self.data.ui.resolution = self.data.ui.resolution or "auto"
            self.data.ui.ui_scale = self.data.ui.ui_scale or 1.0
            self.data.ui.language = self.data.ui.language or "en"
            self.data.ui.last_probe_ts = time.time()
        self._save_file()

    def probe_skills(self) -> None:
        # Placeholder: integrate with OCR skill scan when available
        with self._lock:
            self.data.skills.learned_skills = self.data.skills.learned_skills or []
            self.data.skills.last_probe_ts = time.time()
        self._save_file()

    def probe_inventory(self) -> None:
        # Placeholder: essential consumables presence
        with self._lock:
            essentials = self.data.inventory.essentials or {}
            essentials.setdefault("stims", "unknown")
            essentials.setdefault("repair_kits", "unknown")
            self.data.inventory.essentials = essentials
            self.data.inventory.last_probe_ts = time.time()
        self._save_file()

    # ---------- Public API ----------
    def refresh_all(self, background: bool = True) -> None:
        def run():
            self.probe_mounts()
            self.probe_ui()
            self.probe_skills()
            self.probe_inventory()

        if background:
            threading.Thread(target=run, daemon=True).start()
        else:
            run()

    def ensure_preflight(self, required: Optional[List[str]] = None, *, verify: bool = False) -> Dict[str, Any]:
        """Verify required capabilities; refresh missing ones synchronously."""
        required = required or ["mounts"]
        missing: List[str] = []
        with self._lock:
            now = time.time()
            if "mounts" in required and (
                (not self.data.mounts.learned_verified and not self.data.mounts.detected_unverified)
                or now - self.data.mounts.last_probe_ts > self.ttl
            ):
                missing.append("mounts")

        if missing:
            # Refresh synchronously for determinism before start
            if "mounts" in missing:
                self.probe_mounts(verify=verify)

        return {"ok": True, "missing": []}

    def start_loop(self) -> None:
        if self._running:
            return
        self._running = True

        def loop() -> None:
            while self._running:
                try:
                    self.refresh_all(background=False)
                    # Sleep until next TTL window; short initial sleep if no data
                    time.sleep(self.ttl)
                except Exception:
                    time.sleep(30)

        threading.Thread(target=loop, daemon=True).start()

    def stop_loop(self) -> None:
        self._running = False

    # ---------- Character selection ----------
    def set_current_character(self, name: str) -> None:
        safe = (name or "default").strip()
        if not safe:
            return
        with self._lock:
            if safe == self._character:
                return
            self._character = safe
            # Reload per-character data
            self.data = self._load_file()

    def _detect_default_character(self) -> str:
        # Try to read a runtime profile for current character
        try:
            p = Path("profiles/runtime/your_character.json")
            if p.exists():
                raw = json.loads(p.read_text(encoding="utf-8"))
                return str(raw.get("character_name") or raw.get("name") or "default")
        except Exception:
            pass
        return "default"


# Singleton accessor
_probe: Optional[CapabilityProbe] = None


def get_probe() -> CapabilityProbe:
    global _probe
    if _probe is None:
        _probe = CapabilityProbe()
    return _probe


