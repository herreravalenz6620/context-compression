# Harness Contract Verification

The four MVP adapters are only useful if they match the real harness surfaces.
Local smoke tests prove the selector/verifier path works; they do not prove the
host integration contract still exists. Use this source-contract check whenever
changing adapter glue, install docs, or claims about harness support.

## Sources Checked

- Codex: `openai/codex`, hook parser and Bash tool rewrite path.
- Pi: `earendil-works/pi`, extension `defineTool` and `pi.registerTool` path.
- OpenClaw: `openclaw/openclaw`, plugin entry and `api.registerTool` path.
- Hermes Agent: `NousResearch/hermes-agent`, MCP stdio client and config docs.

## Reproduce

Clone the upstream harnesses outside this repo:

```sh
mkdir -p /tmp/context-compression-upstream
cd /tmp/context-compression-upstream
git clone --depth 1 https://github.com/openai/codex.git
git clone --depth 1 https://github.com/earendil-works/pi.git
git clone --depth 1 https://github.com/openclaw/openclaw.git
git clone --depth 1 https://github.com/NousResearch/hermes-agent.git
```

Run the contract verifier:

```sh
.venv/bin/python scripts/verify_harness_contracts.py \
  --upstream-root /tmp/context-compression-upstream
```

Expected output:

```text
harness source contracts ok
```

## Current Findings

- Codex supports `PreToolUse` `updatedInput` only when
  `hookSpecificOutput.permissionDecision` is `allow`; Bash exposes and rewrites
  the `command` string. This matches `hook.py`.
- Pi extensions still export `defineTool`, accept TypeBox parameter schemas,
  register tools with `pi.registerTool(...)`, and expose mutable `tool_call`
  events. This matches `adapters/pi/context-selector-tool.ts`.
- OpenClaw plugins still use `definePluginEntry(...)`, support
  `before_tool_call` hook handlers that return replacement `params`, and expose
  `api.registerTool`. This matches the transparent hook and optional evidence
  tool in `adapters/openclaw/index.ts`.
- Hermes Agent plugins can register tools with `ctx.register_tool(...)` and
  intentionally override an existing tool with `override=True`; the registry
  exposes `get_entry(...)`, and `file_tools.py` registers `read_file`. This
  matches `adapters/hermes-plugin/`. Hermes also reads MCP servers from
  `~/.hermes/config.yaml`, supports stdio subprocess MCP servers, and prefixes
  MCP tool names as `mcp_<server>_<tool>`, which matches
  `adapters/mcp/context_selector_server.py`.

If this check fails, do not treat harness smokes as sufficient. Update the
adapter and install docs against the upstream contract first, then rerun the
unit suite and harness smokes.
