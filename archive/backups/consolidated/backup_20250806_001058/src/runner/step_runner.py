import json
from src.execution.core import execute_step


def run_step_list(path: str):
    with open(path, "r") as f:
        steps = json.load(f)

    for i, step in enumerate(steps):
        print(f"\n[RUNNER] Executing step #{i + 1}: {step['type']}")
        execute_step(step)
