# Project: lightroom-cli-agentic

## Context

This repo is a fork of `znznzna/lightroom-cli`: a Python CLI, Python SDK, MCP server, and bundled Lightroom Classic Lua plugin for controlling Adobe Lightroom Classic through a local dual-socket bridge.

The strategic direction for this fork is CLI-first, agent-friendly Lightroom automation. Prefer the `lr` CLI and schema discovery surfaces over MCP-only workflows. MCP remains supported because it is generated from the same schema, but agents should be able to complete workflows from shell commands alone.

Current local focus: exposure-bracket workflows. The repo now has a prototype `lr catalog find-brackets` command that groups likely exposure-bracketed photos by capture time and exposure-bias metadata. Lightroom Classic HDR Photo Merge is not currently implemented because no documented Lightroom Classic Lua SDK call has been confirmed for invoking HDR merge directly.

## Commands

Use a virtual environment. Python 3.10+ is required by `pyproject.toml`; CI uses Python 3.10 and 3.12.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/lr --version
```

Core checks:

```bash
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m pytest tests/ -v --ignore=tests/e2e --cov=lightroom_sdk --cov=cli --cov=mcp_server
```

Fast targeted checks for bracket/schema work:

```bash
.venv/bin/python -m pytest tests/integration/test_cli_catalog_extended.py tests/test_schema.py tests/test_paths.py -q
.venv/bin/python -m ruff check .
.venv/bin/lr catalog find-brackets --help
.venv/bin/lr schema catalog.find-brackets
```

Live Lightroom smoke, when Lightroom Classic is available:

```bash
.venv/bin/lr plugin install
.venv/bin/lr system check-connection
.venv/bin/lr -o json catalog get-selected
.venv/bin/lr -o json catalog find-brackets
```

## Architecture

- `cli/` contains the Click CLI. Add user-facing commands under `cli/commands/`.
- `lightroom_sdk/schema.py` is the single source of truth for command metadata, validation, schema discovery, and generated MCP tools.
- `lightroom_sdk/plugin/*.lua` is the Lightroom Classic plugin code. Commands are registered in `PluginInit.lua` and implemented in modules such as `CatalogModule.lua`.
- `lightroom_sdk/socket_bridge.py` and `resilient_bridge.py` handle the local bridge connection and retry behavior.
- `mcp_server/tool_registry.py` generates MCP tools from `COMMAND_SCHEMAS`; keep CLI and MCP behavior schema-aligned.
- `plugin/skills/lightroom-cli/SKILL.md` is the Claude Code skill surface. Update it when adding agent-facing workflows.
- `tests/integration/` mostly mocks the bridge and verifies CLI-to-command wiring.
- `tests/e2e/` requires Lightroom Classic and is skipped in normal local runs.
- `.github/workflows/test.yml` runs ruff, version sync, and non-e2e pytest across macOS and Windows.

## Working Agreements

- Inspect `lr schema <command>` and `lightroom_sdk/schema.py` before adding or changing command behavior.
- For a new command, update all four surfaces together: Click CLI, schema, Lua plugin route/handler, and tests.
- Before coding against Lightroom SDK, Adobe APIs, CLI flags, MCP/FastMCP behavior, or external HDR tools, verify current docs in-session. Record short freshness receipts in the final report or plan update.
- Keep commands machine-readable by default for agents: support `-o json`, `--fields`, `--json`, and `--json-stdin` patterns already used in the repo.
- Prefer explicit photo IDs over implicit selection for repeatable agent workflows, but preserve selected-photo defaults where that is the established UX.
- Return structured failures with actionable `code`, `message`, and recovery hints where practical. Do not leak raw stack traces through CLI output.
- Treat mutating/destructive operations carefully: schema must mark `mutating`, `supports_dry_run`, and `requires_confirm` accurately.
- Do not invent Lightroom SDK capabilities. If a capability is not verified in Adobe docs or live Lightroom behavior, label it as unconfirmed and design a probe first.
- Use adversarial review at phase checkpoints and before final push: ask Claude Code and Codex to review for false SDK assumptions, unsafe defaults, schema/CLI/MCP drift, and missing tests. Fix or explicitly defer findings.

## Constraints

- Do not edit generated/package metadata just to satisfy a local run unless the repo’s version sync requires it. If version sync changes files, include or revert them deliberately.
- Do not make full-catalog scans the default for new agent workflows. Default to selected photos or explicit IDs, and require an explicit flag such as `--all` for catalog-wide scans.
- Avoid long-running Lightroom commands without a command-specific timeout in schema and CLI execution.
- Keep plugin code compatible with Lightroom’s Lua sandbox. Avoid assumptions about unavailable standard-library or OS APIs.
- Do not rely on MCP as the only integration path. Every core workflow should be discoverable and usable from `lr`.

## Current Goal

Make this fork a reliable, agent-optimized CLI for exposure-bracket discovery and, if feasible, HDR batch processing around Lightroom Classic.

The next implementation session should start from:

```bash
docs/plans/2026-05-30-agentic-bracket-workflow-plan.md
```

Compact `/goal` form for long runs:

```text
/goal Harden lightroom-cli-agentic bracket discovery and prove HDR merge feasibility. Verify current Adobe/Lightroom/FastMCP docs before SDK work, run targeted plus full non-e2e tests, use Claude Code and Codex adversarial reviews at checkpoints and final, and stop when live Lightroom bracket smoke passes or the blocker is documented.
```

## Done Conditions

For ordinary code changes:

- Relevant targeted tests pass.
- `ruff check .` passes.
- Schema/help smoke passes for any added command.
- Full non-e2e test suite passes before pushing or opening a PR unless a failure is clearly unrelated and documented.
- Live Lightroom smoke is run for bridge/plugin behavior when Lightroom is available; otherwise document that it was not run.
