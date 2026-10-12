# /// script
# requires-python = ">=3.10"
# dependencies = ["microsandbox==0.7.8"]
# ///
"""msb in 90s, episode 2: secrets.

The sandbox only ever sees a placeholder for GITHUB_TOKEN. microsandbox swaps in the real token on the way out, and only
for requests to postman-echo.com. The same placeholder sent anywhere else is blocked.

    uv run secrets_demo.py
"""
import asyncio
import os

from microsandbox import Sandbox, Secret

# A fake token is all the demo needs.
TOKEN = os.environ.get("GITHUB_TOKEN", "ghp_fake1234567890")
AUTH = '-H "Authorization: Bearer $GITHUB_TOKEN"'


async def main():
    sb = await Sandbox.create(
        "secrets-demo",
        image="python:3.12-bookworm",
        secrets=[Secret.env("GITHUB_TOKEN", value=TOKEN, allow=["postman-echo.com"])],
        replace=True,
    )
    try:
        seen = await sb.shell("echo $GITHUB_TOKEN")
        print(f"inside the sandbox GITHUB_TOKEN is {seen.stdout_text.strip()}")

        allowed = await sb.shell(f"curl -s https://postman-echo.com/headers {AUTH} | tr , '\\n' | grep authorization")
        print(f"postman-echo.com received  {allowed.stdout_text.strip()}")

        leak = await sb.shell(f"curl -sS https://example.com {AUTH}")
        result = "got through" if leak.success else f"blocked, {leak.stderr_text.strip()}"
        print(f"example.com (not allowed): {result}")
    finally:
        await sb.destroy()


if __name__ == "__main__":
    asyncio.run(main())
