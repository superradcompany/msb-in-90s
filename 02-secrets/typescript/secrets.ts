// msb in 90s, episode 2: secrets.
// The sandbox only ever sees a placeholder for GITHUB_TOKEN. microsandbox swaps in the real token on the way out, and
// only for requests to postman-echo.com. The same placeholder sent anywhere else is blocked.
import { Sandbox } from "microsandbox";

// A fake token is all the demo needs.
const token = process.env.GITHUB_TOKEN ?? "ghp_fake1234567890";

const AUTH = '-H "Authorization: Bearer $GITHUB_TOKEN"';

const sb = await Sandbox.builder("secrets-demo")
  .image("python:3.12-bookworm")
  .secret((s) => s.env("GITHUB_TOKEN").value(token).allow("postman-echo.com"))
  .replace()
  .create();
try {
  const seen = await sb.shell("echo $GITHUB_TOKEN");
  console.log(`inside the sandbox GITHUB_TOKEN is ${seen.stdout().trim()}`);

  const allowed = await sb.shell(`curl -s https://postman-echo.com/headers ${AUTH} | tr , '\\n' | grep authorization`);
  console.log(`postman-echo.com received  ${allowed.stdout().trim()}`);

  const leak = await sb.shell(`curl -sS https://example.com ${AUTH}`);
  console.log(`example.com (not allowed): ${leak.success ? "got through" : `blocked, ${leak.stderr().trim()}`}`);
} finally {
  await sb.destroy();
}
