---
title: ifp/schemas — situation report
updated: 2026-09-11
reconcile: 1
---

# ifp/schemas — situation report

Canonical JSON Schemas for IFP advert data. Read [CLAUDE.md](CLAUDE.md) first — it carries the
release model and the conventions that read as bugs but aren't.

## Right now

- **Released at `1.17.0`** (11 Sep 2026), covering [#138](https://github.com/ifp/schemas/pull/138),
  [#139](https://github.com/ifp/schemas/pull/139) and [#140](https://github.com/ifp/schemas/pull/140).
  Before this the latest tag was `1.16.0` and two merged fixes had reached no consumer at all —
  this repo ships by tag, not by merge.
- **The repo can now validate itself.** `bin/validate.py` plus a GitHub Actions workflow on every
  branch. Until now nothing checked anything, which is why a public schema stayed impossible to
  satisfy for years and a sub-schema drifted from its parent for three months.
- **Onboarded for Claude Code** ([#140](https://github.com/ifp/schemas/pull/140)) — `CLAUDE.md`,
  reconcile `project.md`, permissions split.
- **First reconcile.** `.reconcile-marker` and the `reconciled` tag start here.

## In flight

- `feat/schema-validator` — the validator, its CI workflow and this reconcile. Unmerged.

## Known open questions — decisions needed, not tasks

These are all **contract changes**. None is safe to fix as a drive-by; each needs a call on
direction first. Detail and the external cross-reference that surfaced most of them:
Company Memory `reports/schemas/atlas-cross-reference/report.md`.

| Question | Why it isn't just a fix |
|---|---|
| `virtual_tours` is `[{title, original_url}]` in public and `string[]` in internal | Changing either breaks a published contract; precedent (`floor_plans`, v1.1.0) says version bump |
| `property.status` says `let`/`to_let` in public, `rented`/`to_rent` in internal | Same vocabulary, two spellings; either reconcile them or publish the mapping |
| `simplified_export` still `$ref`s the strict enum files | Confirmed 11 Sep: a novel type accepted by `property.attributes` is **rejected** by our own partner-export schema. Same class of bug as [#139](https://github.com/ifp/schemas/pull/139), third occurrence. Partner-facing, so fixing it is a contract decision |
| `simplified_export` sets no `required` and leaves `additionalProperties` open | It validates any object, `{}` included. It is the partner export contract and currently guarantees nothing |
| Importer emits `unexpected_fields` / `missing_fields`; schema defines `unmapped_fields` with `additionalProperties: false` | Either the schema or the importer is stale — needs someone who knows which came first |
| Six 0-byte `geo/distances_from/*.json`, plus three broken orphaned WIP files | Remnants of an abandoned proximity feature. Fill or delete — see the TODO doc |

## Next action

1. Merge `feat/schema-validator`, then finalise the `reconciled` tag against the squashed trunk commit.
2. Decide the direction on the `simplified_export` enum divergence — it is the only open question
   where our own output can fail our own published schema today.
3. Everything else in the table above, in whatever order suits.

## Roadmap

| Date | What shipped | History doc |
|---|---|---|
| 2026-09-11 | Schema validator + CI | [2026-09-11-schema-validator.md](docs/history/2026-09-11-schema-validator.md) |
