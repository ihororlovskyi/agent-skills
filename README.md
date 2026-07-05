# Agent Skills

A collection of [agent skills](https://agentskills.io) for Claude Code and other AI coding agents.

## Skills

| Skill | Description |
| --- | --- |
| [web-debug](skills/web-debug/SKILL.md) | Debug local web apps via Playwright.<br>Script-assisted browser debugging skill. |
| [vitest](skills/vitest/SKILL.md) | Configure, write, debug, run, and migrate Vitest tests for JavaScript/TypeScript projects.<br>Script-assisted Vitest skill. |

## Install

```bash
npx skills add sentimony/skills -s web-debug -a codex claude-code -y
npx skills add sentimony/skills -s vitest -a codex claude-code -y
```

Have fun ;)
