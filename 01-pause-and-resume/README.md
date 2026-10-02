# 1. Pause and resume

Your agent's long jobs are hogging the machine and urgent work just landed. Pause the jobs, give the urgent work the whole machine, then resume them. Nothing has to restart.

`msb pause` freezes a whole microsandbox in milliseconds, with every process, its memory and its progress intact. A paused sandbox uses almost no CPU, and `msb resume` carries on from the exact step it stopped at.

## Run it

```bash
npm i -g microsandbox

./demo.sh                                       # the 60-second CLI version
python3 measure.py                              # reproduce the numbers from the video
cd typescript && npm install && npm start       # a small priority queue in TypeScript
cd python && uv run priority_queue.py           # the same in Python
```

## What you'll see

Three jobs each keep one core busy (about 100% each). Paused, each drops to about 2.5%. After resume they're back at about 100%, and their progress counters carry on from where they stopped instead of starting over. Pause and resume each take about 10 ms from the CLI, and a few ms from the SDKs.

## Good to know

- Pause and resume work on local sandboxes; they're not supported on microsandbox cloud.
- Paused sandboxes keep their memory. Pausing frees CPU, not RAM.
- New commands are rejected while a sandbox is paused, and network connections may time out.
- On a machine with many cores, the urgent task won't run much faster, because the jobs weren't competing for its cores. The CPU drop is what you'll notice.

Tested with microsandbox 0.7.6 on macOS (Apple Silicon). Docs: [pause and resume](https://docs.microsandbox.dev/sandboxes/lifecycle#pause-and-resume).
