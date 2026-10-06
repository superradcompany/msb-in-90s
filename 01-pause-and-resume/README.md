<div align="center">
  <h1>Pause and Resume</h1>
</div>

<br />

https://github.com/user-attachments/assets/564e7af6-53c5-4f0b-8c58-f464b6032760

<br />

**`msb pause`** freezes a running [microsandbox](https://github.com/superradcompany/microsandbox) in milliseconds. **`msb resume`** picks it up exactly where it stopped, with every process and all its progress intact.

##

- <img height="14" src="https://octicons-col.vercel.app/flame/A770EF"> **Urgent Work**: Urgent work needs the machine, but your long builds, test runs or agent jobs are halfway done.
- <img height="14" src="https://octicons-col.vercel.app/device-desktop/A770EF"> **Your Laptop Back**: You need the machine for a call, a demo or a recording.
- <img height="14" src="https://octicons-col.vercel.app/briefcase/A770EF"> **Park a Dev Environment**: Put it away, servers and all, and come back to it later.
- <img height="14" src="https://octicons-col.vercel.app/sync/A770EF"> **Take Turns**: Run more sandboxes than you have cores and let them share.
- <img height="14" src="https://octicons-col.vercel.app/bug/A770EF"> **Freeze a Bad Run**: Stop it right there before it changes more state.

A paused sandbox uses almost no CPU. In our test each one dropped from about 100% of a core to about 2.5%.

<br />

## <a href="./#gh-dark-mode-only" target="_blank"><img height="18" src="https://octicons-col.vercel.app/terminal/ffffff" alt="cli-dark"></a><a href="./#gh-light-mode-only" target="_blank"><img height="18" src="https://octicons-col.vercel.app/terminal/000000" alt="cli"></a>&nbsp;&nbsp;Walk Through It

#### <img height="14" src="https://octicons-col.vercel.app/download/A770EF">&nbsp;&nbsp;Install the CLI
> Requires the [development build](https://github.com/superradcompany/microsandbox/pull/1774), not yet released. [Setup guide →](https://github.com/superradcompany/microsandbox/blob/main/DEVELOPMENT.md)

<br />

#### <img height="14" src="https://octicons-col.vercel.app/play/A770EF">&nbsp;&nbsp;1. Start a Sandbox With a Job in It
> Create a sandbox called `pause-demo` and start a tiny counter in it. It prints a number once a second, so it stands in for any long-running work.
>
> ```sh
> msb create alpine --name pause-demo
> ```
>
> ```sh
> counter=$(msb exec -d --no-tty pause-demo -- sh -c '
>   n=0
>   while true; do
>     n=$((n + 1))
>     echo "$n"
>     sleep 1
>   done
> ')
> ```

<br />

#### <img height="14" src="https://octicons-col.vercel.app/eye/A770EF">&nbsp;&nbsp;2. Check That It's Counting
> Run this a few times and the number keeps going up. The output below is from one run; your numbers will differ.
>
> ```sh
> sleep 1
> ```
>
> ```sh
> msb logs pause-demo --job "$counter" --tail 1
> ```
>
> → `86`

<br />

#### <img height="14" src="https://octicons-col.vercel.app/stopwatch/A770EF">&nbsp;&nbsp;3. Pause It
> Every process in the sandbox freezes on the spot, including the counter, and the sandbox drops to almost no CPU. The sandbox just waits in memory, which is why this takes milliseconds.
>
> ```sh
> msb pause pause-demo
> ```
>
> → `✓ Paused pause-demo`

<br />

#### <img height="14" src="https://octicons-col.vercel.app/circle-slash/A770EF">&nbsp;&nbsp;4. Try to Talk to It
> A paused sandbox turns away new commands until you resume it, which is a quick way to see that it really is frozen.
>
> ```sh
> msb exec pause-demo -- echo hello
> ```
>
> → `error: sandbox 'pause-demo' is in state Paused and cannot be started`
>
> The last counter value is still readable:
>
> ```sh
> msb logs pause-demo --job "$counter" --tail 1
> ```
>
> → `86`

<br />

#### <img height="14" src="https://octicons-col.vercel.app/play/A770EF">&nbsp;&nbsp;5. Resume It
> Wait five seconds and check the counter. It hasn't moved.
>
> ```sh
> sleep 5
> ```
>
> ```sh
> msb logs pause-demo --job "$counter" --tail 1
> ```
>
> → `86`
>
> Now resume it.
>
> ```sh
> msb resume pause-demo
> ```
>
> → `✓ Resumed pause-demo`

<br />

#### <img height="14" src="https://octicons-col.vercel.app/check-circle/A770EF">&nbsp;&nbsp;6. Check the Counter Again
> ```sh
> sleep 2
> ```
>
> ```sh
> msb logs pause-demo --job "$counter" --tail 1
> ```
>
> → `89`
>
> It's at 89. It stayed at 86 during those five seconds, then carried on counting after resume. If it had restarted, it would be back near 1. It picked up from exactly where it stopped.

<br />

#### <img height="14" src="https://octicons-col.vercel.app/trash/A770EF">&nbsp;&nbsp;7. Clean Up
> ```sh
> msb kill pause-demo --job "$counter"
> ```
>
> ```sh
> msb stop pause-demo
> ```
>
> ```sh
> msb rm pause-demo
> ```

> [!TIP]
>
> Run `./demo.sh` to see the same thing with three busy jobs at once, and `python3 measure.py` to measure the CPU yourself.

<br />

## <a href="./#gh-dark-mode-only" target="_blank"><img height="18" src="https://octicons-col.vercel.app/package-dependencies/ffffff" alt="sdk-dark"></a><a href="./#gh-light-mode-only" target="_blank"><img height="18" src="https://octicons-col.vercel.app/package-dependencies/000000" alt="sdk"></a>&nbsp;&nbsp;From Code

The SDKs have the same two calls.

> ```typescript
> await sb.pause();
> ```
>
> ```typescript
> await sb.resume();
> ```
>
> <details>
> <summary><b>&nbsp;Python Example →</b></summary>
>
> ```python
> await sb.pause()
> ```
>
> ```python
> await sb.resume()
> ```
>
> </details>

The full examples are in [`typescript/`](typescript) and [`python/`](python), using the development SDKs.

<br />

## <a href="./#gh-dark-mode-only" target="_blank"><img height="18" src="https://octicons-col.vercel.app/info/ffffff" alt="info-dark"></a><a href="./#gh-light-mode-only" target="_blank"><img height="18" src="https://octicons-col.vercel.app/info/000000" alt="info"></a>&nbsp;&nbsp;Good to Know

- It works on local sandboxes.
- A paused sandbox keeps its memory. Only the CPU is freed.
- New guest commands are refused until you resume. Saved job logs stay readable.
- Network connections may time out during a long pause.
- Full snapshots and forks are currently refused while detached jobs are active.
- Tested with the detached-jobs development build on macOS, OVH Linux/KVM, and Windows ARM64/WHP with Git Bash. The companion scripts were also tested on macOS.

<br />

<a href="https://docs.microsandbox.dev/sandboxes/lifecycle#pause-and-resume"><img src="https://img.shields.io/badge/Pause_%26_Resume_Docs-%E2%86%92-A770EF?style=flat-square&labelColor=2b2b2b" alt="Pause and resume docs"></a>

<br />

<p align="center"><img src="assets/freeze.svg" width="100%" alt="A beige microsandbox computer counts up on its screen, freezes under frost with a pause badge while the number holds, then thaws and keeps counting from the same number."></p>
