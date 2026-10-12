#!/usr/bin/env bash
# msb in 90s, episode 2: secrets.
# Binds a fake GITHUB_TOKEN to postman-echo.com. The sandbox only sees a placeholder; msb swaps in the real value for
# postman-echo.com and blocks the same placeholder on its way anywhere else. Then it rotates the token live.
set -euo pipefail

NAME=secrets-demo
IMAGE=python:3.12-bookworm
AUTH='-H "Authorization: Bearer $GITHUB_TOKEN"'

cleanup() {
  msb stop -f "$NAME" >/dev/null 2>&1 || true
  msb rm "$NAME" >/dev/null 2>&1 || true
}
trap cleanup EXIT

in_sandbox() { msb exec "$NAME" -- sh -c "$1"; }

cleanup
export GITHUB_TOKEN=ghp_fake1234567890
echo "host: GITHUB_TOKEN=$GITHUB_TOKEN (fake), bound to postman-echo.com"
msb create "$IMAGE" --name "$NAME" --secret 'GITHUB_TOKEN@postman-echo.com' >/dev/null

echo
echo "inside the sandbox, GITHUB_TOKEN is:"
in_sandbox 'echo "  $GITHUB_TOKEN"'

echo
echo "sent to postman-echo.com (allowed), which echoes back what it received:"
in_sandbox "curl -s https://postman-echo.com/headers $AUTH | tr , '\n' | grep authorization | sed 's/^/  /'"

echo
echo "sent to example.com (not allowed):"
in_sandbox "curl -sS https://example.com $AUTH" || echo "  blocked"

echo
echo "example.com without the placeholder still works:"
in_sandbox 'curl -sS -o /dev/null -w "  %{http_code}\n" https://example.com'

echo
export GITHUB_TOKEN=ghp_rotated0987654321
echo "rotating to $GITHUB_TOKEN without restarting the sandbox"
msb modify "$NAME" --secret 'GITHUB_TOKEN@postman-echo.com' >/dev/null
in_sandbox 'echo "  the sandbox still sees $GITHUB_TOKEN"'
in_sandbox "curl -s https://postman-echo.com/headers $AUTH | tr , '\n' | grep authorization | sed 's/^/  /'"
