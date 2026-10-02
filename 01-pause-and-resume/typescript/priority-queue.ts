// msb in 90s, episode 1: pause and resume.
// Three background jobs run in microsandboxes. Urgent work arrives: pause the jobs, give the urgent task the machine,
// then resume the jobs. Their progress carries on from where it stopped.
import { Sandbox } from "microsandbox";

const JOBS = ["tests", "build", "eval"];
const BUSY =
  "nohup sh -c 'n=0; while true; do n=$((n+1)); echo $n > /tmp/progress; sleep 0.1; done' >/dev/null 2>&1 & " +
  "nohup sh -c 'while :; do :; done' >/dev/null 2>&1 &";
const URGENT = "i=0; while [ $i -lt 2000000 ]; do i=$((i+1)); done";

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
const progress = async (sb: Sandbox) => (await sb.shell("cat /tmp/progress")).stdout().trim();

async function timed<T>(fn: () => Promise<T>): Promise<string> {
  const t = performance.now();
  await fn();
  return `${(performance.now() - t).toFixed(0)} ms`;
}

const jobs = await Promise.all(
  JOBS.map((name) => Sandbox.builder(name).image("alpine").cpus(1).memory(512).replace().create()),
);
try {
  await Promise.all(jobs.map((sb) => sb.shell(BUSY)));
  await sleep(5000);
  console.log("background jobs running:");
  for (const [i, sb] of jobs.entries()) {
    console.log(`  ${JOBS[i].padEnd(6)} step ${await progress(sb)}, ${(await sb.metrics()).cpuPercent.toFixed(0)}% CPU`);
  }

  console.log("\nurgent work arrived: pausing the jobs");
  const before: string[] = [];
  for (const [i, sb] of jobs.entries()) {
    before.push(await progress(sb));
    console.log(`  paused ${JOBS[i]} in ${await timed(() => sb.pause())}`);
  }

  console.log("\nrunning the urgent task");
  const urgent = await Sandbox.builder("urgent").image("alpine").replace().create();
  console.log(`  done in ${await timed(() => urgent.shell(URGENT))}`);
  await urgent.destroy();

  console.log("\nresuming the jobs");
  for (const [i, sb] of jobs.entries()) {
    console.log(`  resumed ${JOBS[i]} in ${await timed(() => sb.resume())}`);
  }
  await sleep(1000);
  for (const [i, sb] of jobs.entries()) {
    console.log(`  ${JOBS[i].padEnd(6)} step ${before[i]} before the pause, step ${await progress(sb)} now`);
  }
} finally {
  await Promise.all(jobs.map((sb) => sb.destroy()));
}
