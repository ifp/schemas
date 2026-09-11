# Internal Sale Advert Schema Changelog

### Fixes (2026-09-11)

Type-correctness fixes only. No field added or removed, and every existing fixture still
validates — see the notes against each item for why each is non-breaking.

- `advert.pre_attributed` now `$ref`s `property/attributes-schema_v1.0.0.json` instead of
  the three strict enum files (`types-schema-enum`, `features-schema-enum`,
  `tags-schema-enum`). Since #137 loosened `property.attributes` to accept any string,
  a value could be legal in `property.attributes.types` and rejected in
  `advert.pre_attributed.types`. The two blocks are structurally identical, so sharing one
  definition means they cannot diverge again — including when the enums are restored.
  Loosening only: nothing that validated before fails now.
- `original_property`, `pre_checker_original_property`, `importer_property`,
  `translations` and `unmapped_fields` gain `"type": "object"`. They were bare
  `{"additionalProperties": true}`, which also accepted a string or an integer.
- `mapped_enums` typed as `["array", "null"]` with object items. It is built as an array of
  `{feed_field, feed_value, ifp_field, ifp_value}` by the importer
  (`downloader/converter.rb`) and may be null when no mapping ran — it was never an object.
- Descriptions added to the top-level `updated_at` / `created_at` and to
  `advert.created_at` / `advert.updated_at`, so the two same-named pairs one level apart
  are no longer ambiguous: the top-level pair is the pipeline's own ISO 8601 timestamps,
  the `advert` pair is the feed's own values copied through verbatim.

### v1.1.0 (2016-10-12)

- Change of {property.floor_plans} from array of strings, to an array of objects

### v1.0.0 (2016-09-01)

Initial Release
