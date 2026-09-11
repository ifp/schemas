# TODO

Forward-looking only. What shipped lives in [`docs/history/`](history/) and the
[SITREP](../SITREP.md) roadmap table.

Most of what follows is a **contract decision**, not a task — the schemas here are consumed by
third parties and by our own pipeline, so "just fix it" usually means "pick a direction and cut a
version". Two items that sat on this list turned out not to be defects at all; they are now
recorded in [CLAUDE.md](../CLAUDE.md) as deliberate, and one of them would have caused a
production bug if "fixed". Check there before adding anything back.

## Decisions needed

- [ ] **Rebuild the three remaining fixtures.** `upsert_sale_advert.json`,
  `elasticsearch_single_sale_advert_result.json` and `search_engine_single_sale_advert_result.json`
  still describe images in Cloudinary terms. **No longer blocked** — the live shape is known and
  recorded in `CLAUDE.md`, and `json/fixtures/floor_plans.json` already uses it.

  Not self-contained: `upsert_sale_advert` is loaded by `ifp/system` (`AdvertHelper`,
  `AdvertCounterTrait`) and `french-property.com` tests, so run both suites either side.
  `ifp/system`'s Cloudinary tests build their own `cdn: 2` arrays inline and are unaffected.
  **Biggest open item in this repo.**

- [ ] **`images-schema` describes `format` and `bytes`, which neither live record carries.**
  Both optional, so nothing breaks — but the schema claims fields the pipeline no longer
  populates. Confirm, then remove or document.

- [ ] **`advert-collector` emits floor plans as bare URL strings** (`PublicAdvertMapper::flatUrls`)
  where the schema wants objects. `floor_plans-schema_v1.2.0` now makes the obvious fix possible —
  build them the way `images()` already does — but nothing in this repo forces it. Belongs to
  whoever owns the collector.
- [ ] **`advert.first_visible_at`** is `{"type": "array"}` with no `items`. Every producer emits a
  hardcoded `[]` and nothing populates it. Establish whether it is vestigial, then either type it
  or remove it.
- [ ] **`unmapped_fields` may be vestigial.** No producer emits it; `unexpected_fields` and
  `missing_fields` look like what it was meant to be. Confirm nothing reads it, then remove.
- [ ] **`locality-data-schema` validates `{}`** — properties, but no `required` and open
  `additionalProperties`. The last remaining `bin/validate.py` warning. Its content comes from the
  locality service, so confirm which fields are always present before tightening.
- [ ] **When [#137](https://github.com/ifp/schemas/pull/137)'s "temporary" loosening is reverted,
  three files need it**, not one: `property/attributes-schema`, and `simplified_export`, which
  deliberately carries its own copy of the vocabulary rather than reaching into internal enum
  files. `advert.pre_attributed` follows `attributes-schema` automatically.

## Cleanup

- [ ] **`systems/checker.md` and `systems/quota.md` are 0 bytes.** Write them or remove them;
  `systems/loader.md` and `systems/importer.md` show what they should contain.

## Tooling

- [ ] **`bin/validate.py` pins `jsonschema~=4.25` because it uses `RefResolver`,** deprecated since
  4.18 and slated for removal. Port to the `referencing` library before a major bump forces it.
- [ ] **Add a fixture that exercises `floor_plans` and `virtual_tours`.** Both are `[]` in
  `upsert_sale_advert.json`, which is why the stage mismatch above went unnoticed. Blocked on
  settling that question first.
- [ ] **Consider validating the downstream response fixtures.**
  `elasticsearch_single_sale_advert_result.json` and `search_engine_single_sale_advert_result.json`
  wrap an advert in `hits.hits[]._source` and `data` and are maintained by hand, so they can drift
  from the schema without anything noticing.
