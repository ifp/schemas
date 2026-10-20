# docs/

Internal working documentation. The **public** entry point is the repo
[README](../README.md) — that's what third parties read.

| Path | What it is |
|---|---|
| [`../SITREP.md`](../SITREP.md) | Situation report — where the repo is right now, open questions, next actions |
| [`TODO.md`](TODO.md) | Forward-looking backlog. Mostly contract decisions rather than tasks |
| [`history/`](history/) | One retrospective per piece of work, `YYYY-MM-DD-<slug>.md` |
| [`../CLAUDE.md`](../CLAUDE.md) | Auto-loaded context: release model, conventions, gotchas |

Elsewhere in the repo, and easy to miss:

- [`../systems/`](../systems/) — how each consuming system uses the schema. `loader.md` and
  `importer.md` have content; `checker.md` and `quota.md` are 0 bytes.
- [`../partner_exports.md`](../partner_exports.md) — field-by-field prose for the simplified
  partner export.
- Per-schema changelogs live next to the schemas, in `json/public/` and `json/internal/`.

## History

| Date | Doc | Status |
|---|---|---|
| 2026-10-20 | [Public sale-advert schema v1.2.0 adds the property's coordinates](history/2026-10-20-public-schema-lat-lon.md) | in-progress |
| 2026-09-11 | [The fixtures must carry both image generations, not just the new one](history/2026-09-11-fixtures-both-image-generations.md) | stable |
| 2026-09-11 | [floor_plans v1.2.0 required a field half of all adverts never have](history/2026-09-11-floor-plans-original-url-fix.md) | stable |
| 2026-09-11 | [Floor plans schema v1.2.0 — one lifecycle, three CDN generations](history/2026-09-11-floor-plans-schema-v1.2.0.md) | stable |
| 2026-09-11 | [Partner export contract, queue envelope, and the proximity WIP](history/2026-09-11-schema-contract-cleanup.md) | stable |
| 2026-09-11 | [Schema validator and CI](history/2026-09-11-schema-validator.md) | stable |
