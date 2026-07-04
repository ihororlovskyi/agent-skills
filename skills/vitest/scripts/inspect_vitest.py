#!/usr/bin/env python3
"""
Inspect a JavaScript/TypeScript project for Vitest conventions.

Usage:
    python scripts/inspect_vitest.py --root .
    python scripts/inspect_vitest.py --root ../my-app --json
"""

import argparse
import json
import os
from pathlib import Path


LOCKFILES = [
    ("pnpm-lock.yaml", "pnpm"),
    ("yarn.lock", "yarn"),
    ("bun.lockb", "bun"),
    ("bun.lock", "bun"),
    ("package-lock.json", "npm"),
    ("npm-shrinkwrap.json", "npm"),
]

CONFIG_FILES = [
    "vitest.config.ts",
    "vitest.config.mts",
    "vitest.config.js",
    "vitest.config.mjs",
    "vite.config.ts",
    "vite.config.mts",
    "vite.config.js",
    "vite.config.mjs",
]

TEST_GLOBS = [
    "**/*.test.ts",
    "**/*.test.tsx",
    "**/*.test.js",
    "**/*.test.jsx",
    "**/*.spec.ts",
    "**/*.spec.tsx",
    "**/*.spec.js",
    "**/*.spec.jsx",
]

IGNORE_PARTS = {"node_modules", "dist", "build", "coverage", ".git", ".next", ".nuxt", ".output"}


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def detect_package_manager(root):
    for filename, manager in LOCKFILES:
        if (root / filename).exists():
            return manager
    return "npm"


def package_command(manager, script_name=None):
    if script_name:
        if manager == "npm":
            return f"npm run {script_name} --"
        if manager == "yarn":
            return f"yarn {script_name}"
        if manager == "pnpm":
            return f"pnpm {script_name}"
        if manager == "bun":
            return f"bun run {script_name}"
    if manager == "npm":
        return "npx vitest run"
    if manager == "yarn":
        return "yarn vitest run"
    if manager == "pnpm":
        return "pnpm vitest run"
    if manager == "bun":
        return "bunx vitest run"
    return "npx vitest run"


def has_dep(package_json, name):
    if not package_json:
        return False
    for section in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        if name in package_json.get(section, {}):
            return True
    return False


def detect_frameworks(package_json):
    checks = {
        "vitest": "vitest",
        "vite": "vite",
        "nuxt": "nuxt",
        "vue": "vue",
        "react": "react",
        "svelte": "svelte",
        "jsdom": "jsdom",
        "happy-dom": "happy-dom",
        "@testing-library/react": "@testing-library/react",
        "@vue/test-utils": "@vue/test-utils",
    }
    return sorted(label for label, dep in checks.items() if has_dep(package_json, dep))


def find_test_files(root, limit):
    files = []
    for pattern in TEST_GLOBS:
        for path in root.glob(pattern):
            if any(part in IGNORE_PARTS for part in path.parts):
                continue
            files.append(path)
    unique = sorted(set(files))
    return [str(path.relative_to(root)) for path in unique[:limit]], len(unique)


def detect_likely_test_script(scripts):
    if not scripts:
        return None
    for name in ("test:unit", "test:vitest", "vitest", "test"):
        value = scripts.get(name)
        if value and "vitest" in value:
            return name
    for name, value in scripts.items():
        if "vitest" in value:
            return name
    return None


def build_report(root, limit):
    package_json_path = root / "package.json"
    package_json = read_json(package_json_path)
    scripts = package_json.get("scripts", {}) if package_json else {}
    manager = detect_package_manager(root)
    test_script = detect_likely_test_script(scripts)
    test_files, total_tests = find_test_files(root, limit)
    config_files = [name for name in CONFIG_FILES if (root / name).exists()]
    frameworks = detect_frameworks(package_json)

    warnings = []
    if not package_json:
        warnings.append("No package.json found.")
    if package_json and not has_dep(package_json, "vitest"):
        warnings.append("Vitest is not listed in package dependencies.")
    if "react" in frameworks and not any(env in frameworks for env in ("jsdom", "happy-dom")):
        warnings.append("React component tests usually need jsdom or happy-dom.")
    if "vue" in frameworks and not any(env in frameworks for env in ("jsdom", "happy-dom")):
        warnings.append("Vue component tests usually need jsdom or happy-dom.")
    if not config_files:
        warnings.append("No Vitest/Vite config file found.")

    return {
        "root": str(root),
        "package_manager": manager,
        "frameworks": frameworks,
        "vitest_scripts": {name: value for name, value in scripts.items() if "vitest" in value},
        "likely_test_script": test_script,
        "suggested_run_command": package_command(manager, test_script),
        "config_files": config_files,
        "test_files_sample": test_files,
        "test_files_total": total_tests,
        "warnings": warnings,
    }


def print_human(report):
    print(f"Root: {report['root']}")
    print(f"Package manager: {report['package_manager']}")
    print(f"Framework hints: {', '.join(report['frameworks']) or 'none'}")
    print(f"Suggested run command: {report['suggested_run_command']}")

    print("\nVitest scripts:")
    if report["vitest_scripts"]:
        for name, value in report["vitest_scripts"].items():
            marker = " (likely)" if name == report["likely_test_script"] else ""
            print(f"  - {name}{marker}: {value}")
    else:
        print("  - none")

    print("\nConfig files:")
    for name in report["config_files"] or ["none"]:
        print(f"  - {name}")

    print(f"\nTest files: {report['test_files_total']}")
    for path in report["test_files_sample"]:
        print(f"  - {path}")

    if report["warnings"]:
        print("\nWarnings:")
        for warning in report["warnings"]:
            print(f"  - {warning}")


def main():
    parser = argparse.ArgumentParser(description="Inspect a project for Vitest setup and conventions")
    parser.add_argument("--root", default=".", help="Project root to inspect (default: current directory)")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument("--limit", type=int, default=20, help="Maximum test files to list (default: 20)")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        raise SystemExit(f"Root does not exist: {root}")
    if not root.is_dir():
        raise SystemExit(f"Root is not a directory: {root}")

    report = build_report(root, args.limit)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_human(report)


if __name__ == "__main__":
    main()

