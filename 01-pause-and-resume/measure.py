#!/usr/bin/env python3
"""Reproduce the numbers in episode 1 of msb in 90s.

Starts three microsandboxes with one vCPU each, runs a CPU-bound job and a progress counter in each, and measures host CPU
for the three while running, while paused and after resume. CPU is the exact CPU time each sandbox's VM process used over
a window (from `ps`), not ps's decaying %cpu. Needs only Python 3 and the msb CLI (macOS or Linux).

    python3 measure.py            # prints a summary and writes measure.json
"""
import json
import re
import subprocess
import time
from pathlib import Path

NAMES = ["tests", "build", "eval"]
IMAGE = "alpine"
WINDOW = 15  # seconds per CPU measurement


def sh(cmd, timeout=300):
    return subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, timeout=timeout)


def ex(name, script, timeout=60):
    try:
        return subprocess.run(["msb", "exec", name, "--", "sh", "-c", script], capture_output=True, text=True, timeout=timeout).stdout.strip()
    except subprocess.TimeoutExpired:
        return "TIMEOUT"


def cpu_seconds(text):
    parts = text.split(":")
    return float(parts[-1]) + 60 * float(parts[-2]) + (3600 * float(parts[-3]) if len(parts) > 2 else 0)


def vm_cpu_times():
    """Cumulative CPU seconds of each sandbox's VM process, keyed by sandbox name."""
    out = {}
    for row in sh("ps -axo time=,command=").stdout.splitlines():
        if " machine " not in row:
            continue
        m = re.search(r"--name[ =](\S+)", row)
        if m and m.group(1) in NAMES:
            out[m.group(1)] = cpu_seconds(row.split(None, 1)[0])
    return out


def measure(window=WINDOW):
    a = vm_cpu_times(); time.sleep(window); b = vm_cpu_times()
    per = {n: round(100 * (b[n] - a[n]) / window, 1) for n in NAMES if n in a and n in b}
    return {"per_sandbox_pct": per, "total_pct": round(sum(per.values()), 1)}


def timed(cmd):
    t = time.monotonic(); r = sh(cmd); ms = round((time.monotonic() - t) * 1000, 1)
    return ms, (r.stdout + r.stderr).strip()


def drop(name):
    for cmd in (["msb", "stop", "-f", name], ["msb", "rm", name]):
        sh(cmd)


def main():
    for n in NAMES:
        drop(n)
    try:
        for n in NAMES:
            sh(["msb", "create", IMAGE, "--name", n, "--cpus", "1", "--memory", "1G"])
            ex(n, "nohup sh -c 'n=0; while true; do n=$((n+1)); echo $n > /tmp/progress; sleep 0.1; done' >/dev/null 2>&1 &"
                  " nohup sh -c 'while :; do :; done' >/dev/null 2>&1 & echo started")
        time.sleep(5)
        print(f"measuring {WINDOW} s while running ...", flush=True)
        r = {"running": measure()}
        r["progress_before"] = {n: ex(n, "cat /tmp/progress") for n in NAMES}
        r["pause_ms"] = {}
        for n in NAMES:
            r["pause_ms"][n], line = timed(["msb", "pause", n])
            print(f"  {line}  ({r['pause_ms'][n]} ms)")
        time.sleep(2)
        print(f"measuring {WINDOW} s while paused ...", flush=True)
        r["paused"] = measure()
        r["resume_ms"] = {}
        for n in NAMES:
            r["resume_ms"][n], line = timed(["msb", "resume", n])
            print(f"  {line}  ({r['resume_ms'][n]} ms)")
        r["progress_after"] = {n: ex(n, "cat /tmp/progress") for n in NAMES}
        time.sleep(3)
        print("measuring 10 s after resume ...", flush=True)
        r["resumed"] = measure(10)
    finally:
        for n in NAMES:
            drop(n)

    Path(__file__).with_name("measure.json").write_text(json.dumps(r, indent=2))
    print("\n             running   paused   resumed")
    for n in NAMES:
        print(f"  {n:<8} {r['running']['per_sandbox_pct'].get(n, '?'):>7}%  {r['paused']['per_sandbox_pct'].get(n, '?'):>6}%  {r['resumed']['per_sandbox_pct'].get(n, '?'):>7}%")
    print(f"  {'total':<8} {r['running']['total_pct']:>7}%  {r['paused']['total_pct']:>6}%  {r['resumed']['total_pct']:>7}%")
    print("\nprogress before the pause:", r["progress_before"])
    print("progress right after resume:", r["progress_after"], "(it carries on, it doesn't restart)")
    print("100% = one host core. Memory stays allocated while paused; only CPU is freed.")


if __name__ == "__main__":
    main()
