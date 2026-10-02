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

## Walk through it

Install the CLI first with `npm i -g microsandbox`.

**1. Start a sandbox with a job in it.** This creates a sandbox called `job` and starts a tiny counter inside it. The counter adds one ten times a second and writes the number to `/tmp/n`, so it stands in for any long-running work.

```bash
msb create alpine --name job
msb exec job -- sh -c "nohup sh -c 'n=0; while true; do n=\$((n+1)); echo \$n > /tmp/n; sleep 0.1; done' >/dev/null 2>&1 &"
```

**2. Check that it's counting.** Run this a few times and the number keeps going up.

```bash
msb exec job -- cat /tmp/n
```

```
40
```

**3. Pause it.** Every process in the sandbox freezes on the spot, including the counter, and the sandbox drops to almost no CPU. Nothing is saved to disk. The sandbox just waits in memory, which is why this takes milliseconds.

```bash
msb pause job
```

```
✓ Paused       job
```

**4. Try to talk to it.** A paused sandbox turns away new commands until you resume it, which is a quick way to see that it really is frozen.

```bash
msb exec job -- cat /tmp/n
```

```
error: sandbox 'job' is in state Paused and cannot be started
```

**5. Wait a bit, then resume it.**

```bash
sleep 5
msb resume job
```

```
✓ Resumed      job
```

**6. Check the counter again.**

```bash
msb exec job -- cat /tmp/n
```

```
41
```

It's at 41. If the job had kept running during those 5 seconds it would be around 91, and if it had restarted it would be back near 0. It picked up from exactly where it stopped.

**7. Clean up** with `msb stop -f job` and then `msb rm job`.

To see the same thing with three busy jobs at once, run [`./demo.sh`](demo.sh).

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
