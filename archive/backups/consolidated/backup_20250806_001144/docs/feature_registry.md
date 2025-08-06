# Feature Registry

This document lists modules with top-level comments or TODO markers and notes their key dependencies.

| Module | Purpose | Dependencies | TODO |
|-------|---------|--------------|------|
| `core/profession_leveler.py` | High level helper for sequential profession training. | `TravelManager`, optional `progress_tracker` | |
| `core/travel_manager.py` | Utilities for traveling to trainers and managing profession training. | `TrainerScanner`, `utils.travel` | |
| `core/trainer_scanner.py` | Utilities for OCR'ing skill lists from a trainer window. | `pyautogui`, `pytesseract`, `cv2` | |
| `core/trainer_ocr.py` | OCR helpers for scanning trainer dialogue. | `utils.screen_capture`, `pytesseract` | |
| `core/profession_manager.py` | Manage profession skill training. | `utils.*`, `config.profession_config` | |
| `core/session_manager.py` | Track session XP and credits. | `XPEstimator`, `utils.session_utils` | |
| `core/xp_estimator.py` | Simple XP estimator with rolling averages. | built-in modules | |
| `modules/training/trainer_seeker.py` | Seek out trainers and train skills when enough XP is available. | `progress_tracker`, `trainer_navigator`, `trainer_visit`, `read_xp_via_ocr` | |
| `modules/travel/shuttle_manager.py` | Shuttle-based travel helpers. | `src.vision`, `movement_profiles`, `scripts.travel.shuttle` | |
| `modules/travel/trainer_travel.py` | Travel to profession trainers via shuttle. | `scripts.travel.shuttle`, `movement_profiles.walk_to_coords` | |
| `modules/professions/progress_tracker.py` | Load profession data, check prerequisites and recommend skills. | `profession_logic.modules.xp_estimator` | |
| `modules/skills/training_check.py` | Determine which profession skills are trainable. | standard library only | |
| `profession_logic/config.py` | Starter configuration toggles for profession logic. | None | |
| `profession_logic/modules/profession_manager.py` | High-level interface for profession progression. | `config` | |
| `profession_logic/modules/trainer_finder.py` | Locate profession trainers in game data. | None | |
| `profession_logic/modules/xp_estimator.py` | XP estimation utilities with logging. | `src.xp_tracker`, `src.xp_paths` | |
| `profession_logic/modules/leveling_path.py` | Plan out recommended leveling paths. | None | |
| `profession_logic/utils/data_importer.py` | Load profession data files. | standard library | |
| `profession_logic/utils/logger.py` | Logging utilities for profession modules. | `logging` | |
| `archive/ms11-core/xp_tracker.py` | XP tracking with OCR and heuristics. | `asyncio`, `ThreadPoolExecutor` | Add screenshot and OCR parsing logic |
| `src/movement/movement_profiles.py` | Strategy functions for common movement behaviors. | `MovementAgent`, `waypoints` | Implement screen recognition & WASD walking |
| `src/execution/dialogue.py` | Handle dialogue steps and training with NPCs. | `training.train_with_npc` | Replace with UI interaction/OCR/macro |
