# /// script
# requires-python = ">=3.10"
# dependencies = ["microsandbox==0.7.6"]
# ///
"""msb in 90s, episode 1: pause and resume.

Three background jobs run in microsandboxes. Urgent work arrives: pause the jobs, give the urgent task the machine, then
resume the jobs. Their progress carries on from where it stopped.

    uv run priority_queue.py
"""
import asyncio
import time

from microsandbox import Sandbox

JOBS = ["tests", "build", "eval"]
BUSY = (
    "nohup sh -c 'n=0; while true; do n=$((n+1)); echo $n > /tmp/progress; sleep 0.1; done' >/dev/null 2>&1 & "
    "nohup sh -c 'while :; do :; done' >/dev/null 2>&1 &"
)
URGENT = "i=0; while [ $i -lt 2000000 ]; do i=$((i+1)); done"


async def progress(sb):
    return (await sb.shell("cat /tmp/progress")).stdout_text.strip()


async def timed(coro):
    t = time.monotonic()
    await coro
    return f"{(time.monotonic() - t) * 1000:.0f} ms"


async def main():
    jobs = await asyncio.gather(*(Sandbox.create(n, image="alpine", cpus=1, memory=512, replace=True) for n in JOBS))
    try:
        await asyncio.gather(*(sb.shell(BUSY) for sb in jobs))
        await asyncio.sleep(5)
        print("background jobs running:")
        for name, sb in zip(JOBS, jobs):
            print(f"  {name:<6} step {await progress(sb)}, {(await sb.metrics()).cpu_percent:.0f}% CPU")

        print("\nurgent work arrived: pausing the jobs")
        before = []
        for name, sb in zip(JOBS, jobs):
            before.append(await progress(sb))
            print(f"  paused {name} in {await timed(sb.pause())}")

        print("\nrunning the urgent task")
        urgent = await Sandbox.create("urgent", image="alpine", replace=True)
        print(f"  done in {await timed(urgent.shell(URGENT))}")
        await urgent.destroy()

        print("\nresuming the jobs")
        for name, sb in zip(JOBS, jobs):
            print(f"  resumed {name} in {await timed(sb.resume())}")
        await asyncio.sleep(1)
        for name, sb, b in zip(JOBS, jobs, before):
            print(f"  {name:<6} step {b} before the pause, step {await progress(sb)} now")
    finally:
        await asyncio.gather(*(sb.destroy() for sb in jobs))


if __name__ == "__main__":
    asyncio.run(main())
