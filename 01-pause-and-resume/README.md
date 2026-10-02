# 1. Pause and resume

Your agent's long jobs are hogging the machine and urgent work just landed. Pause the jobs, do the urgent work, then resume them right where they stopped.

<p align="center"><img src="assets/cpu-list.svg" width="100%" alt="A CPU monitor lists tests, build and eval at about 100% each. After msb pause each row drops to about 2.5% and shows a pause badge, and after msb resume all three climb back to about 100%."></p>

<table>
<tr>
<td width="64" valign="top"><img src="../assets/characters/agent-worried.svg" width="64" height="64" alt="The agent"></td>
<td valign="top">

<sub><b>THE AGENT</b></sub><br>
My jobs are 40 minutes in and a P0 just landed. If I stop them, do they start over?

</td>
</tr>
<tr>
<td width="64" valign="top"><img src="../assets/characters/microsandbox-explaining.svg" width="64" height="64" alt="Microsandbox"></td>
<td valign="top">

<sub><b>MICROSANDBOX</b></sub><br>
If you stop them, yes. If you pause them, they wait right where they are.

</td>
</tr>
</table>

## What you need

```bash
npm i -g microsandbox
```

That gives you the `msb` CLI. The code versions further down also need Node.js 22 or newer, or [uv](https://docs.astral.sh/uv/) for Python.

## The recipe

**1. Start three busy jobs.** Each one gets its own microsandbox with one CPU, keeps that CPU at 100% and writes its progress to `/tmp/progress` ten times a second.

```bash
for n in tests build eval; do
  msb create alpine --name "$n" --cpus 1 --memory 1G
  msb exec "$n" -- sh -c "nohup sh -c 'n=0; while true; do n=\$((n+1)); echo \$n > /tmp/progress; sleep 0.1; done' >/dev/null 2>&1 &
    nohup sh -c 'while :; do :; done' >/dev/null 2>&1 &"
done
```

**2. Pause them when the urgent work lands.**

```bash
for n in tests build eval; do msb pause "$n"; done
```

```
   ✓ Paused       tests
   ✓ Paused       build
   ✓ Paused       eval
```

Each pause takes about 10 ms. A paused job drops from about 100% of a core to about 2.5%, and `msb list` shows it as `paused`.

**3. Do the urgent work.** The CPU the jobs were using is free now.

**4. Resume them.**

```bash
for n in tests build eval; do msb resume "$n"; done
for n in tests build eval; do msb exec "$n" -- cat /tmp/progress; done
```

The counters pick up from where they stopped. In our run `tests` was at step 55 before the pause and at 57 right after the resume, not back at 0.

[`demo.sh`](demo.sh) runs all four steps in one go and cleans up after itself.

<p align="center"><img src="assets/freeze.svg" width="100%" alt="A beige microsandbox computer counts up on its screen, freezes under frost with a pause badge while the number holds, then thaws and keeps counting from the same number."></p>

## The same thing from code

The SDKs have the same two calls. Without its logging, the core of [`typescript/priority-queue.ts`](typescript/priority-queue.ts) is this.

```ts
for (const sb of jobs) await sb.pause();

const urgent = await Sandbox.builder("urgent").image("alpine").replace().create();
await urgent.shell(URGENT);
await urgent.destroy();

for (const sb of jobs) await sb.resume();
```

And the same in [`python/priority_queue.py`](python/priority_queue.py).

```python
for sb in jobs:
    await sb.pause()

urgent = await Sandbox.create("urgent", image="alpine", replace=True)
await urgent.shell(URGENT)
await urgent.destroy()

for sb in jobs:
    await sb.resume()
```

Run them with `cd typescript && npm install && npm start` or `cd python && uv run priority_queue.py`. From the SDKs each pause and resume took 1 to 3 ms.

## How it works

Pause freezes every process inside the sandbox and stops its virtual CPUs. Nothing gets copied or saved anywhere. The sandbox's memory just stays where it is, which is why resume is instant and every process carries on from the exact spot it froze.

<table>
<tr>
<td width="64" valign="top"><img src="../assets/characters/agent-curious.svg" width="64" height="64" alt="The agent"></td>
<td valign="top">

<sub><b>THE AGENT</b></sub><br>
Does it really give the CPU back?

</td>
</tr>
<tr>
<td width="64" valign="top"><img src="../assets/characters/microsandbox-happy.svg" width="64" height="64" alt="Microsandbox"></td>
<td valign="top">

<sub><b>MICROSANDBOX</b></sub><br>
Run <code>python3 measure.py</code> and see for yourself.

</td>
</tr>
</table>

[`measure.py`](measure.py) measures the three jobs' CPU while they run, while they're paused and after they resume. Here's our run, where 100% is one full core.

```
             running   paused   resumed
  tests      101.6%     2.6%    101.8%
  build      101.5%     2.5%    102.0%
  eval       101.6%     2.8%    101.9%
```

## Good to know

- Pause and resume work on local sandboxes. They aren't supported on microsandbox cloud.
- A paused sandbox frees its CPU and keeps its memory.
- New commands are refused while a sandbox is paused. `msb exec` says `sandbox 'tests' is in state Paused and cannot be started`.
- Network connections may time out during a long pause.
- Tested with microsandbox 0.7.6 on an Apple Silicon Mac. The SDKs need a matching `msb`, so check `msb --version` if a sandbox won't start.

More in the docs: [pause and resume](https://docs.microsandbox.dev/sandboxes/lifecycle#pause-and-resume).
