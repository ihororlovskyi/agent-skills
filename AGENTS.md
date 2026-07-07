# AGENTS.md

## Mission

This repository is a public collection of agent skills, published on
[skills.sh](https://skills.sh/sentimony/skills). One directory per skill:
`skills/<name>/` containing `SKILL.md`, `CHANGELOG.md`, `LICENSE`, and optionally
`examples/`, `scripts/`, `references/`. The current skill list lives in
[README.md](README.md).

## Language

Everything in this repository is written in English: documentation, SKILL.md content,
code comments, commit messages, and PR descriptions.

## Conventions

- `name` in SKILL.md frontmatter matches the directory name (letters, digits, hyphens only).
- `description` is third-person, "Use when…" style, and never summarizes the workflow itself.
- `license` is a valid SPDX identifier (e.g. `Apache-2.0`). Attribution/adaptation notes
  belong in reference files, not in frontmatter.
- Versioning: plain semver without prefix (`metadata.version: "1.1.0"` and CHANGELOG.md
  headings); the `v` prefix (e.g. `v1.0.0`) is used only for repository git tags.
- Each skill has a `CHANGELOG.md` in its directory (Keep a Changelog style). It is
  deliberately NOT referenced from SKILL.md so it never enters an agent's context.

## Workflow

- Develop in feature branches, never directly in `main`.
- Merge pull requests via squash merge only.
- A branch that adds a new skill may also change previously created files and skills;
  every such change must be noted in the repository-level [CHANGELOG.md](CHANGELOG.md).
- When adding, renaming, or substantially updating a skill, update [README.md](README.md)
  and the skill's `CHANGELOG.md` in the same PR.
- Always update the repository-level [CHANGELOG.md](CHANGELOG.md) in the same PR as
  well — every release entry there must exist before the corresponding `vX.Y.Z` tag
  is created.
- When adding, renaming, or removing a skill, also update [skills.sh.json](skills.sh.json)
  so the skill appears in the right group on the skills.sh page.
- Validate before publishing a release: `gh skill publish --dry-run`; publish with
  `gh skill publish --tag vX.Y.Z` (creates the GitHub Release).
- CI validates SKILL.md frontmatter (name == directory, description present, plain
  semver `metadata.version`), compiles Python scripts/examples, and checks for
  hidden/bidi Unicode.
- The repository is already picked up by skills.sh; no onboarding steps are needed —
  merged changes to `main` are enough for installs via `npx skills add sentimony/skills`.

## Release checklist

Before opening the PR for a new skill version, verify every item:

1. `metadata.version` in SKILL.md is bumped (plain semver, no `v` prefix).
2. The skill's `CHANGELOG.md` has an entry for the new version.
3. [README.md](README.md) is updated: version in the skills table, description if it
   changed, install command for a newly added skill.
4. Repository-level [CHANGELOG.md](CHANGELOG.md) has a release entry (it must exist
   before the `vX.Y.Z` tag is created).
5. [skills.sh.json](skills.sh.json) is updated if a skill was added, renamed, or removed.
6. `git diff --check` and `gh skill publish --dry-run` pass.

After squash merge into `main`: publish with `gh skill publish --tag vX.Y.Z`, then
confirm the README on GitHub shows the new version.
