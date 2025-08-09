#!/usr/bin/env python3
"""
Tiny MS11 session runner stub.

Emits log lines to stdout periodically so the main UI can stream them via WS.
Usage:
  python session_runner.py <session_id> <profile> <character> <mode>
  python session_runner.py --daemon <name>
"""
import os
import sys
import time
import argparse
from datetime import datetime


def println(msg: str):
    try:
        print(msg, flush=True)
    except Exception:
        sys.stdout.write(msg + "\n")
        sys.stdout.flush()


def run_session(session_id: str, profile: str, character: str, mode: str):
    println(f"[session:{session_id}] starting profile={profile} character={character} mode={mode}")
    t0 = time.time()
    n = 0
    # Optional: demo behavior tree tick
    try:
        from demo_combat_bt import tick as bt_tick
    except Exception:
        bt_tick = None
    try:
        while True:
            n += 1
            elapsed = int(time.time() - t0)
            println(f"[session:{session_id}] tick={n} elapsed={elapsed}s")
            # demo metrics emitted as lines (main server tags them)
            println(f"METRIC cpu={(5 + (n % 20))}")
            println(f"METRIC memory_mb={(200 + (n % 50))}")
            if bt_tick:
                ctx = {"has_target": True, "distance": (5 + n % 40), "max_range": 30}
                bt_tick(ctx)
                if ctx.get('log'):
                    println(f"BT {';'.join(ctx['log'])}")
            time.sleep(2)
    except KeyboardInterrupt:
        println(f"[session:{session_id}] interrupted")


def run_daemon(name: str):
    println(f"[{name}] daemon started at {datetime.now().isoformat()}")
    n = 0
    try:
        while True:
            n += 1
            println(f"[{name}] heartbeat {n}")
            time.sleep(3)
    except KeyboardInterrupt:
        println(f"[{name}] daemon stopping")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('session_id', nargs='?')
    parser.add_argument('profile', nargs='?')
    parser.add_argument('character', nargs='?')
    parser.add_argument('mode', nargs='?')
    parser.add_argument('--daemon', dest='daemon', help='run as named daemon')
    args = parser.parse_args()

    if args.daemon:
        run_daemon(args.daemon)
        return 0

    if not all([args.session_id, args.profile, args.character, args.mode]):
        print("usage: session_runner.py <session_id> <profile> <character> <mode>", file=sys.stderr)
        return 2

    run_session(args.session_id, args.profile, args.character, args.mode)
    return 0


if __name__ == '__main__':
    sys.exit(main())


