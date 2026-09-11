# Reconcile Everything — ifp/schemas project data

**This is a data file** referenced by the global `reconcile-everything` skill at `~/.claude/skills/reconcile-everything/SKILL.md`. The global skill carries the procedure logic; this file supplies project-specific values that the procedure substitutes in.

Update this file when project conventions change. Don't put procedure logic here.

## Paths

| Key | Value |
|---|---|
| `memory_dir` | `~/.claude/projects/<encoded-cwd>/memory/` |
| `situation_report` | `SITREP.md` _(does not exist yet — the first reconcile creates it)_ |
| `todo` | `docs/TODO.md` _(does not exist yet — same)_ |
| `history_docs` | `docs/history/` _(filenames: `YYYY-MM-DD-<slug>.md`; does not exist yet)_ |
| `docs_index` | `docs/README.md` _(does not exist yet)_ |
| `repo_level_claude_md` | `CLAUDE.md` |

`architecture_docs` and `phase_docs` are deliberately omitted — this repo's schemas *are* the
architecture document, and it has no phased-delivery structure.

## Stack / framework

| Key | Value |
|---|---|
| `language` | PHP (autoload only — `src/Fixtures/Loader.php` is the entire codebase); content is JSON Schema draft-07 |
| `framework` | None. Distributed as the Composer package `ifp/schemas`. |
| `route_list_cmd` | N/A — no routes |
| `source_ext` | `*.json` (the schemas and fixtures are the source; `*.php` is one file) |
| `test_runner` | None in-repo. Validate by hand — recipe in `CLAUDE.md` → "Validating a change". |
| `frontend_build_cmd` | N/A |
| `db_engine` | N/A |
| `deploy_platform` | Git tag → Composer. No deploy; consumers resolve tags via a VCS repository entry. |

### Release check — run this every reconcile

This repo ships by **tag**, not by merge, so a reconcile must check for merged-but-unreleased
work:

```bash
git describe --tags --abbrev=0 && git log --oneline $(git describe --tags --abbrev=0)..master
```

Any commits listed are merged but not released to consumers. Surface them and the tag that
should be cut. Tags are bare SemVer with no `v` prefix.

## Verification tiers

Nothing in this repo is user-visible — it is JSON Schemas, fixtures and a validator, consumed by
other services rather than read by anyone. So the human-tier list is deliberately empty and every
history doc here is **auto tier**: the reconcile verifies it itself and promotes it.

```yaml
human_verify_paths: []
```

`verify_default: review` is **not** set. This is not a docs repo — `bin/validate.py` runs in CI on
every branch and can make a real claim about the schemas, so "the reviewer read the diff" is not
the strongest check available. An auto-tier promotion here means CI green on the merge commit
**plus** a named spot-check of the behaviour that changed — a validator run, or a document that
should now be accepted or rejected. Record the check in the doc body; "CI was green" alone is
inference from the merge, not a check.

## Code directories — for stable-doc deep-audit (10a)

- `json/public/` — the third-party feed contract, examples and changelog
- `json/internal/` — the pipeline envelope, `advert-schema`, `metadata-schema`
- `json/internal/property/` — per-sub-object schemas, plus `geo/` and `enums/`
- `json/fixtures/` — canonical documents consuming systems test against
- `src/Fixtures/Loader.php` — the package's only PHP
- `systems/` — per-system usage notes (`loader.md`, `importer.md` have content; `checker.md`, `quota.md` are 0 bytes)

## Stable docs in this project

| Path | What it covers |
|---|---|
| `README.md` | Public entry point — links to each published schema version and its examples. Goes stale when a schema version is added; check it lists every file in `json/public/`. |
| `partner_exports.md` | Field-by-field prose for the simplified partner export. Must track `json/public/simplified_export_sale-advert-schema_v1.0.0.json`. |
| `systems/loader.md` | How the loader interprets `action`, `advert.status` and `advert.approval`. |
| `systems/importer.md` | Importer template → JSON schema field mapping. |
| `json/public/public_sale-advert-schema_changelog.md` | Must have an entry for every public schema change. |
| `json/internal/internal_sale-advert-schema_changelog.md` | Same, for internal. |

## Reconcile mode — folded (default)

Run the reconcile on the active feature branch *before* it merges, so the reconcile docs ride
in the same PR as the code.

Fall back to a standalone post-merge reconcile only when catching up several already-merged PRs
at once.

Apply the folded-mode deltas from the global SKILL.md: diff window =
`git merge-base origin/master HEAD`..HEAD, history doc named with the feature/PR slug,
`reconciled` tag still finalised post-merge.

## Dance procedure reference

Global skill `~/.claude/skills/git-dance/`. No project data file — this repo has no worktrees,
no env files and no database, so most of the dance is a no-op. The meaningful steps are: pull
`master`, delete the local branch, **and cut the release tag** (see CLAUDE.md → "After the PR
merges") — the tag is the step that actually ships the change.

## Notable historical incidents

**2026-08-26 — the public schema was impossible to satisfy, and nobody noticed**

`agency_microsite` sat in `advert.required` but was never defined in `advert.properties`. With
`additionalProperties: false` that made both v1.0.0 and v1.1.0 unsatisfiable — our own published
example failed to validate. It had been that way for years, because nothing in the repo
validated the examples against the schemas. Fixed in place in
[#138](https://github.com/ifp/schemas/pull/138) rather than bumped, on the grounds that no valid
feed could have depended on broken behaviour. *Why the procedure now validates fixtures against
schemas on every reconcile: a schema nobody runs is a schema nobody can trust.*

**2026-09-11 — a sub-schema drifted from the schema that references it**

[#137](https://github.com/ifp/schemas/pull/137) loosened `property/attributes-schema` to accept
any type/feature/tag string, but `advert.pre_attributed` still `$ref`d the strict enum files —
so the same value could be legal in `property.attributes.types` and rejected in
`advert.pre_attributed.types`. Found only by cross-referencing against an external schema, three
months later. Fixed in [#139](https://github.com/ifp/schemas/pull/139) by pointing
`pre_attributed` at `attributes-schema` directly, so the two share one definition. *Why the
procedure checks for duplicated-rather-than-referenced definitions: this repo has several
structurally identical blocks, and any copy can drift.*

**2026-09-11 — six defects reported, three withdrawn on verification**

The same cross-reference produced nine "defects". On checking each against the fixtures and the
live producers, three did not survive: a loose `lat`/`lon` type that turned out to be the
repo's deliberate as-supplied/normalised idiom; a fixture "violation" that was a misread of an
absent key; and a claim that `mapped_enums` should be an object when the importer builds it as
an array. *Why the procedure verifies a finding against a producer or a fixture before writing
it down: schema defects are unusually easy to assert and unusually easy to get wrong.*

## Optional / project-quirks block

- **`$ref`s are absolute URLs pinned to `master`**, so a tagged release is not self-consistent
  and local validation needs a URL→working-tree rewrite. Detail in `CLAUDE.md`.
- **Two version axes** — the Composer tag and the `_vX.Y.Z` schema file version — move
  independently. Don't conflate them in a history doc.
- **0-byte placeholder files** exist in `systems/` and `json/internal/property/geo/distances_from/`.
  A reconcile should not report them as documentation that covers anything.
