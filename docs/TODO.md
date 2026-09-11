# TODO

Forward-looking only. What shipped lives in [`docs/history/`](history/) and the
[SITREP](../SITREP.md) roadmap table.

Most of what follows is a **contract decision**, not a task — the schemas here are consumed by
third parties and by our own pipeline, so "just fix it" usually means "pick a direction and cut a
version". Two items that sat on this list turned out not to be defects at all; they are now
recorded in [CLAUDE.md](../CLAUDE.md) as deliberate, and one of them would have caused a
production bug if "fixed". Check there before adding anything back.

## Decisions needed

- [ ] **`advert-collector` and `floor_plans` disagree about lifecycle stage.** The collector
  describes its output as `internal_sale-advert-schema` but emits the pre-importer shape (flat
  URLs, no Cloudinary fields). Internal `floor_plans-schema_v1.1.0` requires all eleven keys
  including `public_id`, which no producer can know before upload, while `images-schema` requires
  only the three pre-CDN keys for the same lifecycle. One of the two is wrong. **The only open
  item that touches a live pipeline** — take it to whoever owns the collector.
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
