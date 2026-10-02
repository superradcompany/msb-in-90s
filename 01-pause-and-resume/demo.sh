#!/usr/bin/env bash
# msb in 90s, episode 1: pause and resume.
# Starts three busy microsandboxes, pauses them, then resumes them. Their progress counters carry on from where they stopped.
set -euo pipefail

JOBS=(tests build eval)
IMAGE=alpine

cleanup() {
  for n in "${JOBS[@]}"; do
    msb stop -f "$n" >/dev/null 2>&1 || true
    msb rm "$n" >/dev/null 2>&1 || true
  done
}
trap cleanup EXIT

progress() {
  for n in "${JOBS[@]}"; do printf "  %-6s step %s\n" "$n" "$(msb exec "$n" -- cat /tmp/progress)"; done
}

echo "starting three jobs: each burns its one CPU and counts its progress 10 times a second"
cleanup
for n in "${JOBS[@]}"; do
  msb create "$IMAGE" --name "$n" --cpus 1 --memory 1G >/dev/null
  msb exec "$n" -- sh -c "nohup sh -c 'n=0; while true; do n=\$((n+1)); echo \$n > /tmp/progress; sleep 0.1; done' >/dev/null 2>&1 &
    nohup sh -c 'while :; do :; done' >/dev/null 2>&1 &
    echo started" >/dev/null
done
sleep 5
progress

echo
echo "urgent work arrived: pausing the jobs"
for n in "${JOBS[@]}"; do msb pause "$n"; done
msb list

echo
echo "paused for 5 s: the jobs are frozen in memory and use almost no CPU"
sleep 5

echo
echo "resuming"
for n in "${JOBS[@]}"; do msb resume "$n"; done
progress
echo "the counters carried on from where they stopped, not from 0"
