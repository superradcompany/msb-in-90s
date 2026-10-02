# 1. Pause and resume

`msb pause` freezes a running microsandbox in milliseconds. `msb resume` picks it up exactly where it stopped, with every process and all its progress intact.

<p align="center"><img src="assets/cpu-list.svg" width="560" alt="A CPU monitor lists tests, build and eval at about 100% each. After msb pause each row drops to about 2.5% and shows a pause badge, and after msb resume all three climb back to about 100%."></p>

## When it's useful

- Urgent work needs the machine, but your long builds, test runs or agent jobs are halfway done.
- You need your laptop back for a call, a demo or a recording.
- You want to park a dev environment, servers and all, and come back to it later.
- You have more sandboxes than cores, so you let them take turns.
- A run is misbehaving, so you freeze it right there and inspect a running copy with `msb fork`.

A paused sandbox uses almost no CPU. In our test each one dropped from about 100% of a core to about 2.5%.

## Try it

```bash
npm i -g microsandbox
./demo.sh
```

[`demo.sh`](demo.sh) starts three busy sandboxes, pauses them, then resumes them. Their counters carry on from where they stopped instead of starting over.

```
   ✓ Paused       tests
   ...
   ✓ Resumed      tests
  tests  step 57      (it was at 55 before the pause)
```

<p align="center"><img src="assets/freeze.svg" width="480" alt="A beige microsandbox computer counts up on its screen, freezes under frost with a pause badge while the number holds, then thaws and keeps counting from the same number."></p>

## From code

```ts
await sb.pause();
await sb.resume();
```

```python
await sb.pause()
await sb.resume()
```

The full examples are in [`typescript/`](typescript) and [`python/`](python), and [`measure.py`](measure.py) reproduces the CPU numbers.

## Good to know

- It works on local sandboxes, not on microsandbox cloud.
- A paused sandbox keeps its memory. Only the CPU is freed.
- New commands are refused until you resume.
- Network connections may time out during a long pause.

More in the docs: [pause and resume](https://docs.microsandbox.dev/sandboxes/lifecycle#pause-and-resume).
