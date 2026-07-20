# Changelog

All notable changes to the `vitest` skill. Versions refer to `metadata.version`
in SKILL.md. This file is for maintainers and is never loaded by agents using the skill.

## [1.0.3] - 2026-07-20

Driven by real-world audit feedback from a Nuxt 4 project (agilecharts) with
mixed node/nuxt environment test files.

### Added
- Common Failure Modes: Nuxt auto-import leak into `environment: node` files
  (`window is not defined` / `useRuntimeConfig` crash at collection, shifted
  stack traces) — cause, diagnosis via transitive-import grep
- Common Failure Modes: do not delete `.nuxt`/`node_modules/.cache/nuxt`
  blindly; regenerate with `nuxt prepare`
- Nuxt adapter: config example for mixing node- and nuxt-environment files
  in one `defineVitestConfig`

## [1.0.2] - 2026-07-19

### Changed
- Description rewritten in "You MUST use this when…" style

## [1.0.1] - 2026-07-05

Node/environment diagnostics. PR #3.

### Added
- Guidance for "fails in CI, passes locally": check environment differences
  (Node version, `.nvmrc`, `package.json#engines`) before rewriting tests
- `scripts/inspect_vitest.py` and `scripts/run_vitest.py` helper scripts

### Changed
- Versioning switched from date-based (`2026.07.05`) to semver (`1.0.1`)

## [1.0.0] - 2026-07-05

Initial release (as `2026.07.05`). PR #2.

### Added
- SKILL.md covering configuring, writing, debugging, running, and migrating
  Vitest tests (Vite, Vue, Nuxt, React, Next.js, Node libraries, workspaces,
  coverage, mocks, snapshots, flaky tests, Jest migration)
