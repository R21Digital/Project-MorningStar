import datetime
import os

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_path = os.path.join(log_dir, f"session_{timestamp}.log")


def log_step(step: dict):
    with open(log_path, "a") as f:
        entry = f"[{datetime.datetime.now()}] {step['type'].upper()}: {step}\n"
        f.write(entry)
