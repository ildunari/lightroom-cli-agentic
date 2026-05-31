# Agentic Lightroom Bracket Workflow Plan

Date: 2026-05-30

## Goal

Turn this fork into a reliable CLI-first Lightroom Classic automation surface for agents, starting with exposure-bracket discovery and then proving whether batch HDR merge can be implemented inside Lightroom or must be handed to an external engine.

The end state should let an agent safely discover commands, inspect selected or explicit photos, group bracketed sets, report actionable failures, and run verified Lightroom workflows from shell commands without depending on MCP.

## Current Baseline

This fork is based on `znznzna/lightroom-cli` at upstream commit `a4fc4f6`.

Verified local prototype already present:

- `lr catalog find-brackets`
- `catalog.findExposureBrackets` schema entry
- Lua route in `PluginInit.lua`
- Lua implementation in `CatalogModule.lua`
- CLI wiring tests
- schema tests
- stale path tests updated for v1.2.2 tempfile behavior

Known limitation:

- Lightroom Classic HDR Photo Merge has not been proven callable from the public Lua SDK. Treat merge as unconfirmed until a live probe proves otherwise.

## Setup

From repo root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -U pip
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/lr --version
```

For live Lightroom testing:

```bash
.venv/bin/lr plugin install
```

Then restart Lightroom Classic, open **File > Plugin Extras > Start CLI Bridge**, and verify:

```bash
.venv/bin/lr system check-connection
.venv/bin/lr system status
```

## Test Matrix

Fast local loop:

```bash
.venv/bin/python -m pytest tests/integration/test_cli_catalog_extended.py tests/test_schema.py tests/test_paths.py -q
.venv/bin/python -m ruff check .
```

Command discovery smoke:

```bash
.venv/bin/lr catalog find-brackets --help
.venv/bin/lr schema catalog.find-brackets
.venv/bin/lr schema catalog | grep find-brackets
```

Full local non-e2e gate:

```bash
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m pytest tests/ -v --ignore=tests/e2e --cov=lightroom_sdk --cov=cli --cov=mcp_server
```

Live Lightroom smoke:

```bash
.venv/bin/lr -o json catalog get-selected
.venv/bin/lr -o json catalog find-brackets
.venv/bin/lr -o json catalog find-brackets --photo-ids 123,456,789
.venv/bin/lr -o json --fields groups.photos.id,groups.exposureBiases,count catalog find-brackets
```

Live Lightroom bracket fixture test:

1. Import or select at least two known bracket sequences, ideally 3-shot and 5-shot RAW sets.
2. Confirm each file has capture time and exposure-bias metadata visible to Lightroom.
3. Select only one bracket set and run `lr -o json catalog find-brackets`.
4. Select multiple adjacent bracket sets and run again.
5. Run explicit IDs from both sets with `--photo-ids`.
6. Run `--all` only on a small test catalog or after adding a restrictive future filter.

Expected:

- `count` matches known bracket set count.
- `groups[].photos` preserves chronological order.
- `groups[].exposureBiases` contains distinct EV values.
- Missing metadata increments `ignored.missingCaptureTime` or `ignored.missingExposureBias`.

## Implementation Plan

### Phase 1: Harden bracket discovery

Objective: make `lr catalog find-brackets` robust enough for agent use.

Tasks:

- Verify real Lightroom metadata keys for EV compensation. Current implementation tries `exposureBias` and `exposureBiasValue`; confirm with live RAW files.
- Add an output warning when no photos have exposure-bias metadata.
- Add optional `--folder-path`, `--capture-date-from`, `--capture-date-to`, and `--file-format` filters if `--all` is needed on real catalogs.
- Consider outputting a stable `groupId` such as first photo ID plus count.
- Add Lua-level unit coverage if the project has an established Lua test harness; otherwise keep bridge-mocked Python tests and live smoke notes.

Acceptance:

- Targeted tests pass.
- Full non-e2e tests pass.
- Live selected-photo bracket smoke passes on known files.

### Phase 2: Agentic discovery and tool-call ergonomics

Objective: make command discovery and safe tool calling obvious to coding agents.

Tasks:

- Update `plugin/skills/lightroom-cli/SKILL.md` with a bracket workflow section.
- Ensure `lr schema catalog.find-brackets` clearly marks the command as read-only and includes response fields.
- Add examples that use `-o json` and `--fields` for compact output.
- Add a machine-readable recovery note for connection failures in the skill and README.
- Audit whether all mutating commands have accurate `mutating`, `supports_dry_run`, and `requires_confirm` schema metadata.
- Add a short "agent quickstart" doc or README section if the skill is too Claude-specific.

Acceptance:

- A fresh agent can discover `find-brackets` through `lr schema` without reading source.
- A fresh agent can run safe read-only commands before any mutation.
- Error output remains structured and exit-code meaningful.

### Phase 3: Graceful failures

Objective: make common live failures actionable instead of mysterious.

Tasks:

- Confirm connection failures return exit code `3` with `CONNECTION_ERROR`.
- Confirm timeout failures return exit code `4` with `TIMEOUT_ERROR`.
- Add bracket-specific validation:
  - `minPhotos >= 2`
  - `maxPhotos >= minPhotos`
  - `maxSecondsBetween >= 0`
  - non-empty `photoIds` after parsing
- Add warning fields for:
  - source had fewer than `minPhotos`
  - no usable exposure-bias metadata
  - no capture-time metadata
  - `--all` scan used without filters
- Keep warnings in the JSON result, not stderr, for successful read commands.

Acceptance:

- Invalid CLI args fail before connecting when possible.
- Lightroom-side metadata gaps return successful JSON with warnings, not command failure.
- Real connection errors still fail with the correct exit code.

### Phase 4: Determine HDR merge feasibility

Objective: prove or rule out Lightroom-native batch HDR merge.

Tasks:

- Search Adobe Lightroom Classic SDK docs and installed SDK references for any HDR/Photo Merge APIs.
- Inspect Lightroom menu command surfaces available to Lua plugins, if any.
- Build a tiny live probe command only if there is a plausible API. Keep it hidden or experimental until verified.
- If no SDK path exists, document the decision and evaluate alternatives:
  - UI automation of Lightroom Photo Merge
  - Photoshop/Camera Raw handoff
  - external HDR CLI such as PhotomatixCL or another macOS-capable tool
  - grouping only, then human/manual merge

Acceptance:

- A written finding exists with source links and live-probe evidence.
- The repo does not expose a fake `merge` command unless the merge actually works.

### Phase 5: Batch HDR or export workflow

Objective: implement the next useful action after bracket discovery.

Choose one path based on Phase 4:

- If Lightroom-native merge is feasible: add `lr catalog merge-brackets` or `lr hdr merge`.
- If external merge is required: add a command that exports bracket groups or writes a group manifest for an external tool.
- If manual merge is the only safe path: make `find-brackets` produce a compact operator checklist and optional collection creation for each group.

Acceptance:

- Workflow can process multiple bracket groups repeatably.
- Long-running commands have explicit timeouts and progress where possible.
- Destructive or irreversible actions require confirmation.

## Agent Optimization Rules

Use schema-first calling:

```bash
lr schema
lr schema catalog
lr schema catalog.find-brackets
```

Use compact JSON:

```bash
lr -o json --fields groups.photos.id,groups.exposureBiases,count catalog find-brackets
```

Prefer explicit IDs:

```bash
lr -o json --fields photos.id,photos.filename catalog get-selected
lr -o json catalog find-brackets --photo-ids 123,456,789
```

Avoid default full-catalog scans:

```bash
# Good
lr catalog find-brackets
lr catalog find-brackets --photo-ids 123,456,789

# Use only intentionally
lr catalog find-brackets --all
```

Before mutation:

```bash
lr schema COMMAND
lr COMMAND --dry-run
```

## Open Questions

- Which exact metadata key is most reliable for exposure compensation across RAW formats in Lightroom Classic?
- Should bracket grouping tolerate repeated EV values if cameras shoot duplicate frames?
- Should grouping allow fixed bracket sizes, for example `--expected-size 3`?
- Should the fork target upstream PR compatibility or move faster as a Kosta-specific agentic fork?
- What external HDR engine, if any, is acceptable if Lightroom-native merge is not exposed?

## Recommended Next Session Prompt

```text
Read AGENTS.md and docs/plans/2026-05-30-agentic-bracket-workflow-plan.md. Continue Phase 1: harden and live-test lr catalog find-brackets against Lightroom Classic. Verify real exposure-bias metadata keys, improve warnings/validation, update tests, and keep the CLI/schema/MCP surfaces aligned.
```
