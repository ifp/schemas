---
title: Schema validator and CI
tags: [tooling, ci, validation]
status: stable
completed: 2026-09-11
verified: ci
commits: [f76f58f]
pr: 141
---

# Schema validator and CI

Verified 11 Sep 2026 (auto tier): CI `validate` green on merge commit `3e7af4c`; `python3 bin/validate.py` on `master` reports PASSED with 9 fixture/schema pairings green across 41 live schema files, and 1 non-fatal warning.

## What shipped

`bin/validate.py` — a single-file validator, plus `.github/workflows/validate.yml` running it on
every branch and pull request. First time anything in this repo has been checked automatically.

Five checks:

1. Builds the **live set** — the schemas in `PAIRS` and `EXTRA_ROOTS` plus everything they `$ref`,
   transitively. 42 files today.
2. Every live schema is a valid draft-07 schema.
3. Six fixture/schema pairings validate.
4. Warns on hollow schemas — `type: object` with properties, no `required`, and open
   `additionalProperties`.
5. Warns on files under `json/` that nothing live references.

## Two decisions worth keeping

**`$ref`s are rewritten to the working tree.** Every cross-file reference in this repo is an
absolute `raw.githubusercontent.com/.../master/` URL. A validator that resolves them as written
tests `master`, not your branch — so it would pass a branch that breaks a sub-schema, which is the
exact class of bug the validator exists to catch. `LocalResolver.resolve_remote` maps the prefix
onto the repo root.

**Strict checks cover the reachable set only; orphans warn.** The tree contains abandoned
work-in-progress from a proximity feature that was never finished, and three of those files are
broken outright:

| File | Problem |
|---|---|
| `geo/locality-wip.json` | Not valid JSON — syntax error at line 147 |
| `geo/locality-data-nearest-schema.json` | Not a valid draft-07 schema (`"type": ["string"]` where a schema object belongs) |
| `geo/locality-data-schema-wip.json` | `$ref`s `locality-data-distances_from-schema.json`, which does not exist |

Nothing live references any of them, and all three predate this work. Failing CI on files no
consumer can reach would have meant either fixing someone's abandoned WIP without knowing the
intent, or deleting it — neither is a validator's call. They warn instead, so they stay visible.
The six 0-byte `geo/distances_from/*.json` placeholders are remnants of the same unfinished
feature.

## Findings

**The `simplified_export` schema still enforces the strict enums.**
[#137](https://github.com/ifp/schemas/pull/137) loosened `property/attributes-schema` to accept any
type/feature/tag string, and [#139](https://github.com/ifp/schemas/pull/139) brought
`advert.pre_attributed` back in line. `json/public/simplified_export_sale-advert-schema_v1.0.0.json`
is the third occurrence and is still divergent — verified 11 Sep: `bastide_provencale_neuve`,
`heat_pump` and `off_grid` are accepted by `property.attributes` and **rejected** by the partner
export schema. So an advert carrying a new type can fail the schema we publish for our own export.
Not fixed here: it is a partner-facing contract and the direction is a decision, not a cleanup.

**`simplified_export` also guarantees nothing.** No `required`, `additionalProperties: true` — it
validates any object, `{}` included. It is what `partner_exports.md` documents as our export
contract. Check 4 exists because of it.

**A public schema `$ref`s internal enum files**, so the partner-facing export surface exposes the
internal `_unclassified` / `_unmapped` sentinel values.

**The README's link to the internal changelog was dead** — `json/internal_sale-advert-schema_changelog.md`
instead of `json/internal/…`. Fixed here, along with the two published schemas the README never
listed (`simplified_export`, `geo-public`).

## Test plan

```bash
python3 bin/validate.py          # expect: PASSED, 9 warnings, exit 0
```

Negative test performed before commit: setting `translations` to a string in
`json/fixtures/upsert_sale_advert.json` produced `FAILED: 1 problem` and exit 1; restoring it
returned exit 0. A validator that cannot fail is worth nothing, so re-run that check if the script
changes.

## Follow-ups

Everything in the SITREP's "known open questions" table. The `simplified_export` enum divergence is
the one where our own output can fail our own published schema today.
