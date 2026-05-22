#!/usr/bin/env python3
"""Verify adapter assumptions against upstream harness source checkouts.

This is intentionally source-contract validation, not a local smoke. It checks
that the adapter surfaces this repo depends on still exist in the official
harness codebases.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


CHECKS = {
    "codex": [
        (
            "codex-rs/hooks/src/engine/output_parser.rs",
            [
                "pub(crate) fn parse_pre_tool_use",
                "updated_input",
                "permissionDecision:allow",
            ],
        ),
        (
            "codex-rs/core/src/tools/handlers/shell/shell_command.rs",
            [
                'serde_json::json!({ "command": command })',
                "fn with_updated_hook_input",
                'updated_hook_command(&updated_input)?',
            ],
        ),
        (
            "codex-rs/core/src/tools/registry.rs",
            [
                "run_pre_tool_use_hooks",
                "with_updated_hook_input(invocation.clone(), updated_input)",
            ],
        ),
    ],
    "pi": [
        (
            "packages/coding-agent/src/core/extensions/types.ts",
            [
                "export interface ToolDefinition",
                "execute(",
                "export function defineTool",
                'type: "tool_call"',
                "`event.input` is mutable",
            ],
        ),
        (
            "packages/coding-agent/src/core/extensions/loader.ts",
            [
                "registerTool(tool: ToolDefinition)",
                "extension.tools.set(tool.name",
                "runtime.refreshTools()",
            ],
        ),
        (
            "packages/coding-agent/examples/extensions/structured-output.ts",
            [
                'import { defineTool, type ExtensionAPI } from "@earendil-works/pi-coding-agent"',
                "pi.registerTool(structuredOutputTool)",
            ],
        ),
    ],
    "openclaw": [
        (
            "src/plugin-sdk/plugin-entry.ts",
            [
                "definePluginEntry",
                "OpenClawPluginApi",
            ],
        ),
        (
            "src/plugins/registry.ts",
            [
                "registerTool: (tool, opts) => registerTool(record, tool, opts)",
            ],
        ),
        (
            "src/plugins/hook-types.ts",
            [
                '| "before_tool_call"',
                "params?: Record<string, unknown>",
                "PluginHookBeforeToolCallResult",
            ],
        ),
        (
            "src/plugin-sdk/tool-plugin.ts",
            [
                "api.registerTool",
                "definePluginEntry",
            ],
        ),
    ],
    "hermes-agent": [
        (
            "hermes_cli/plugins.py",
            [
                "def register_tool(",
                "override: bool = False",
                "registry.register(",
            ],
        ),
        (
            "tools/registry.py",
            [
                "def get_entry(self, name: str)",
                "override=True",
            ],
        ),
        (
            "tools/file_tools.py",
            [
                "def _resolve_path_for_task",
                'registry.register(name="read_file"',
            ],
        ),
        (
            "tools/mcp_tool.py",
            [
                "Configuration is read from ~/.hermes/config.yaml under the ``mcp_servers`` key",
                "from mcp.client.stdio import stdio_client",
                "discover",
            ],
        ),
        (
            "website/docs/user-guide/features/mcp.md",
            [
                "MCP lets Hermes Agent connect to external tool servers",
                "Stdio servers run as local subprocesses",
                "mcp_<server_name>_<tool_name>",
            ],
        ),
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--upstream-root",
        type=Path,
        required=True,
        help="Directory containing codex, pi, openclaw, and hermes-agent source checkouts.",
    )
    args = parser.parse_args()

    errors: list[str] = []
    for harness, checks in CHECKS.items():
        repo = args.upstream_root.expanduser().resolve() / harness
        if not repo.is_dir():
            errors.append(f"{harness}: missing checkout at {repo}")
            continue
        for relative, needles in checks:
            path = repo / relative
            if not path.is_file():
                errors.append(f"{harness}: missing {relative}")
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for needle in needles:
                if needle not in text:
                    errors.append(f"{harness}: {relative} missing {needle!r}")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("harness source contracts ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
