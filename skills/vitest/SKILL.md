---
name: vitest
description: Use when configuring, writing, debugging, migrating, or running Vitest tests in JavaScript or TypeScript projects, including Vite, Vue, Nuxt, React, Node libraries, workspaces, coverage, mocks, fake timers, snapshots, flaky tests, and Jest migration.
metadata:
  author: ihororlovskyi
  version: "1.0"
license: Apache-2.0
compatibility: Requires Python and a JavaScript package manager; Vitest must be installed in the target project before tests can run.
---

# Vitest

Use this skill to add, fix, or run Vitest tests without turning the task into a Vitest API reference lookup.

**Helper Scripts Available**:
- `scripts/inspect_vitest.py` - Detects package manager, Vitest config, scripts, test files, framework hints, and likely run commands
- `scripts/run_vitest.py` - Runs Vitest through the detected package manager with useful defaults

**Always run scripts with `--help` first** to see usage. DO NOT read the source until you try running the script first and find that a customized solution is absolutely necessary. These scripts are meant to be called directly as black-box helpers.

## Decision Tree

```
User task → Is this an existing project?
    ├─ Yes → Run: python <skill>/scripts/inspect_vitest.py --root <project>
    │        Use detected framework, config, aliases, and package manager.
    │
    └─ No / new setup → Inspect package.json manually if present, then create the
                       smallest Vitest setup that matches the runtime.

Next → What is under test?
    ├─ Node/library logic → environment: node
    ├─ React/Vue/Svelte component → environment: jsdom or happy-dom
    ├─ Nuxt/Vue app code → prefer existing Nuxt/Vite test utilities and config
    ├─ Edge/Workers code → match the project's existing worker test setup
    └─ Browser-specific behavior → consider Vitest browser mode only if already used

Then → Write or fix one focused test, run it directly, then broaden only as needed.
```

## Core Workflow

1. Inspect first: discover existing scripts, config files, setup files, aliases, and test conventions.
2. Match the project: use its package manager, test naming, setup file, mock style, and import aliases.
3. Keep tests behavioral: assert public outcomes instead of private implementation details.
4. Isolate state: reset mocks, timers, DOM, environment variables, and module state when the test mutates them.
5. Verify narrowly first: run one file or name pattern before running the whole suite.

## Running Tests

Run the helper help first:

```bash
python scripts/run_vitest.py --help
```

Common pattern:

```bash
python scripts/run_vitest.py --root . -- tests/example.test.ts
python scripts/run_vitest.py --root . --coverage -- tests/example.test.ts
python scripts/run_vitest.py --root . --test-name "formats currency"
```

If the helper cannot infer the package manager or script, use the project's own command exactly as defined in `package.json`.

## Writing Patterns

- Use `describe`, `it`/`test`, `expect`, and `vi` from `vitest`.
- Use `vi.fn()` for function seams and `vi.mock()` for module boundaries.
- Prefer deterministic inputs over snapshots. Use snapshots only for stable, intentional structures.
- For dates and timers, use fake timers and restore real timers in teardown.
- For async code, await observable outcomes instead of sleeping.
- For components, render through the framework's testing library and assert accessible output.
- For coverage, add thresholds only when the project already enforces them or the user asks.

## Migration Notes

When migrating from Jest, change imports and globals deliberately:

- `jest.fn()` → `vi.fn()`
- `jest.mock()` → `vi.mock()`
- `jest.spyOn()` → `vi.spyOn()`
- `jest.useFakeTimers()` → `vi.useFakeTimers()`
- `jest.resetModules()` → `vi.resetModules()`

Do not enable Vitest globals just to avoid imports unless the existing project already uses global test APIs.

## Common Failure Modes

- **Aliases fail**: make Vitest config reuse the same aliases as Vite/TS config.
- **DOM APIs missing**: choose `jsdom` or `happy-dom` for component tests.
- **Mocks leak between tests**: add `afterEach(() => vi.restoreAllMocks())` or project-equivalent cleanup.
- **Timer tests hang**: restore real timers and advance timers explicitly.
- **ESM/CJS mismatch**: follow the project module type and avoid mixing require/import patterns.
- **Flaky async tests**: wait for specific state, DOM text, emitted events, or resolved promises.

## Reference Examples

- `examples/node_function.test.ts` - Pure TypeScript/Node logic
- `examples/react_component.test.tsx` - React Testing Library style
- `examples/vue_component.test.ts` - Vue Test Utils style

