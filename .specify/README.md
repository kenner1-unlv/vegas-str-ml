# Spec Kit provenance and usage

Scaffolded 2026-10-09 with official [github/spec-kit](https://github.com/github/spec-kit), specify-cli 1.1.3 (MIT), Codex skills mode and PowerShell scripts. Vendored skills/templates/scripts are toolkit infrastructure, not project completion evidence.

Initialization command used from repository root:

```powershell
uv --cache-dir data/raw/.uv-cache tool run --from specify-cli==1.1.3 specify init --here --force --non-interactive --integration codex --integration-options="--skills" --script ps --ignore-agent-tools
```

Do not rerun --force as a routine workflow: review scaffold changes and preserve project constitution and existing work. No global installation is required. The cache override was a local Windows workaround.

Constitution -> $speckit-specify -> $speckit-plan -> $speckit-tasks -> scoped $speckit-implement -> verification. Skills are instructions, not shell commands. Active milestone: [comparable listings](../specs/001-comparable-price-baseline/spec.md). No extensions/hooks were configured during initial setup. Future skill refreshes should pin/version-review the toolkit.

The machine-local feature.json pointer is ignored by the toolkit. For a fresh checkout, set `$env:SPECIFY_FEATURE_DIRECTORY = "specs/001-comparable-price-baseline"` before prerequisite/planning scripts; task and feature paths are not inferred solely from branch names. Keep auth/session files out of version control; only generated .agents/skills/speckit-* instructions are tracked.
