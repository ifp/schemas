# TODO

Forward-looking only. What shipped lives in [`docs/history/`](history/) and the
[SITREP](../SITREP.md) roadmap table.

Most of what follows is a **contract decision**, not a task — the schemas here are consumed by
third parties and by our own pipeline, so "just fix it" usually means "pick a direction and cut a
version". The SITREP's open-questions table is the same list with the reasoning.

## Decisions needed

- [ ] **`simplified_export` enforces enums that `property.attributes` no longer does.** A novel
  type accepted internally is rejected by our own partner-export schema (verified 11 Sep 2026).
  Third occurrence of the divergence [#137](https://github.com/ifp/schemas/pull/137) introduced;
  [#139](https://github.com/ifp/schemas/pull/139) fixed the second. Partner-facing, so the fix is a
  contract change. **The only open item where our own output can fail our own published schema.**
- [ ] **`simplified_export` guarantees nothing** — no `required`, `additionalProperties: true`, so
  it validates `{}`. Decide whether the partner export contract should actually constrain anything.
- [ ] **`virtual_tours` shape** — `[{title, original_url}]` in public, `string[]` in internal. Pick a
  direction; precedent (`floor_plans` in v1.1.0) says this is a version bump, not an in-place fix.
- [ ] **Let/rent vocabulary** — public `let`/`to_let` vs internal `rented`/`to_rent`. Reconcile, or
  publish the mapping.
- [ ] **`unexpected_fields` / `missing_fields`** — the importer emits them
  (`importer/processor/enqueuer.rb:19-21`), the internal schema defines `unmapped_fields` and sets
  top-level `additionalProperties: false`. Establish which side is stale before changing either.
- [ ] **A public schema `$ref`s internal enum files**, exposing the `_unclassified` / `_unmapped`
  sentinels on the partner surface. Decide whether the public surface should have its own copy.

## Cleanup

- [ ] **Abandoned proximity WIP under `json/internal/property/geo/`.** Six 0-byte
  `distances_from/*.json` placeholders, plus `locality-wip.json` (invalid JSON),
  `locality-data-nearest-schema.json` (invalid draft-07) and `locality-data-schema-wip.json`
  (`$ref`s a missing file). All orphaned; `bin/validate.py` warns on each. Either finish the feature
  or delete the files — they have sat since the "proximity wip" commit.
- [ ] **`systems/checker.md` and `systems/quota.md` are 0 bytes.** Write them or remove them;
  `systems/loader.md` and `systems/importer.md` show what they should contain.

## Tooling

- [ ] **`bin/validate.py` pins `jsonschema~=4.25` because it uses `RefResolver`,** deprecated since
  4.18 and slated for removal. Port to the `referencing` library before a major bump forces it.
- [ ] **Consider validating the downstream response fixtures.**
  `elasticsearch_single_sale_advert_result.json` and `search_engine_single_sale_advert_result.json`
  wrap an advert in `hits.hits[]._source` and `data` and are maintained by hand, so they can drift
  from the schema without anything noticing.
