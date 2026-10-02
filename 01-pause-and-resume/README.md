<div align="center">
  <h1>Pause and Resume</h1>
</div>

<br />

<p align="center"><img src="assets/cpu-list.svg" width="560" alt="A CPU monitor lists tests, build and eval at about 100% each. After msb pause each row drops to about 2.5% and shows a pause badge, and after msb resume all three climb back to about 100%."></p>

<br />

**`msb pause`** freezes a running [microsandbox](https://github.com/superradcompany/microsandbox) in milliseconds. **`msb resume`** picks it up exactly where it stopped, with every process and all its progress intact.

##

- <img height="14" src="https://octicons-col.vercel.app/flame/A770EF"> **Urgent Work**: Urgent work needs the machine, but your long builds, test runs or agent jobs are halfway done.
- <img height="14" src="https://octicons-col.vercel.app/device-desktop/A770EF"> **Your Laptop Back**: You need the machine for a call, a demo or a recording.
- <img height="14" src="https://octicons-col.vercel.app/briefcase/A770EF"> **Park a Dev Environment**: Put it away, servers and all, and come back to it later.
- <img height="14" src="https://octicons-col.vercel.app/sync/A770EF"> **Take Turns**: Run more sandboxes than you have cores and let them share.
- <img height="14" src="https://octicons-col.vercel.app/bug/A770EF"> **Freeze a Bad Run**: Stop it right there and inspect a running copy with `msb fork`.

A paused sandbox uses almost no CPU. In our test each one dropped from about 100% of a core to about 2.5%.

<br />

## <a href="./#gh-dark-mode-only" target="_blank"><img height="18" src="https://octicons-col.vercel.app/terminal/ffffff" alt="cli-dark"></a><a href="./#gh-light-mode-only" target="_blank"><img height="18" src="https://octicons-col.vercel.app/terminal/000000" alt="cli"></a>&nbsp;&nbsp;Walk Through It

#### <img height="14" src="https://octicons-col.vercel.app/download/A770EF">&nbsp;&nbsp;Install the CLI
> ```sh
> npm i -g microsandbox
> ```

#### <img height="14" src="https://octicons-col.vercel.app/play/A770EF">&nbsp;&nbsp;1. Start a Sandbox With a Job in It
> Create a sandbox called `job`, copy a tiny counter script into it and start the script in the background. The counter adds one ten times a second and writes the number to `/tmp/n`, so it stands in for any long-running work.
>
> ```sh
> msb create alpine --name job
>
> msb exec job -- sh -c 'cat > /counter.sh' <<'EOF'
> n=0
> while true; do
>   n=$((n + 1))
>   echo $n > /tmp/n
>   sleep 0.1
> done
> EOF
>
> msb exec job -- sh -c 'nohup sh /counter.sh >/dev/null 2>&1 &'
> ```

#### <img height="14" src="https://octicons-col.vercel.app/eye/A770EF">&nbsp;&nbsp;2. Check That It's Counting
> Run this a few times and the number keeps going up.
>
> ```sh
> msb exec job -- cat /tmp/n
> ```
>
> → `40`

#### <img height="14" src="https://octicons-col.vercel.app/stopwatch/A770EF">&nbsp;&nbsp;3. Pause It
> Every process in the sandbox freezes on the spot, including the counter, and the sandbox drops to almost no CPU. Nothing is saved to disk. The sandbox just waits in memory, which is why this takes milliseconds.
>
> ```sh
> msb pause job
> ```
>
> → `✓ Paused job`

#### <img height="14" src="https://octicons-col.vercel.app/circle-slash/A770EF">&nbsp;&nbsp;4. Try to Talk to It
> A paused sandbox turns away new commands until you resume it, which is a quick way to see that it really is frozen.
>
> ```sh
> msb exec job -- cat /tmp/n
> ```
>
> → `error: sandbox 'job' is in state Paused and cannot be started`

#### <img height="14" src="https://octicons-col.vercel.app/play/A770EF">&nbsp;&nbsp;5. Resume It
> Wait a few seconds, then resume it.
>
> ```sh
> sleep 5
> msb resume job
> ```
>
> → `✓ Resumed job`

#### <img height="14" src="https://octicons-col.vercel.app/check-circle/A770EF">&nbsp;&nbsp;6. Check the Counter Again
> ```sh
> msb exec job -- cat /tmp/n
> ```
>
> → `41`
>
> It's at 41. If the job had kept running during those 5 seconds it would be around 91, and if it had restarted it would be back near 0. It picked up from exactly where it stopped.

#### <img height="14" src="https://octicons-col.vercel.app/trash/A770EF">&nbsp;&nbsp;7. Clean Up
> ```sh
> msb stop -f job
> msb rm job
> ```

<p align="center"><img src="assets/freeze.svg" width="480" alt="A beige microsandbox computer counts up on its screen, freezes under frost with a pause badge while the number holds, then thaws and keeps counting from the same number."></p>

> [!TIP]
>
> Run `./demo.sh` to see the same thing with three busy jobs at once, and `python3 measure.py` to measure the CPU yourself.

<br />

## <a href="./#gh-dark-mode-only" target="_blank"><img height="18" src="https://octicons-col.vercel.app/package-dependencies/ffffff" alt="sdk-dark"></a><a href="./#gh-light-mode-only" target="_blank"><img height="18" src="https://octicons-col.vercel.app/package-dependencies/000000" alt="sdk"></a>&nbsp;&nbsp;From Code

The SDKs have the same two calls.

> ```typescript
> await sb.pause();
> await sb.resume();
> ```
>
> <details>
> <summary><b>&nbsp;Python Example →</b></summary>
>
> ```python
> await sb.pause()
> await sb.resume()
> ```
>
> </details>

The full examples are in [`typescript/`](typescript) and [`python/`](python).

<br />

## <a href="./#gh-dark-mode-only" target="_blank"><img height="18" src="https://octicons-col.vercel.app/info/ffffff" alt="info-dark"></a><a href="./#gh-light-mode-only" target="_blank"><img height="18" src="https://octicons-col.vercel.app/info/000000" alt="info"></a>&nbsp;&nbsp;Good to Know

- It works on local sandboxes.
- A paused sandbox keeps its memory. Only the CPU is freed.
- New commands are refused until you resume.
- Network connections may time out during a long pause.
- Tested with microsandbox 0.7.6 on an Apple Silicon Mac.

<br />

<a href="https://docs.microsandbox.dev/sandboxes/lifecycle#pause-and-resume"><img src="https://img.shields.io/badge/Pause_%26_Resume_Docs-%E2%86%92-A770EF?style=flat-square&labelColor=2b2b2b" alt="Pause and resume docs"></a>
