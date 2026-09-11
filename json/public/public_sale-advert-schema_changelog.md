# Public Sale Advert Schema Changelog

### Simplified export fixes (2026-09-11)

Both applied in place to `simplified_export_sale-advert-schema_v1.0.0.json` rather than bumped.
Neither version was safe to depend on: the first change fixes a constraint that rejected our own
output, and the second replaces a schema that asserted nothing at all.

- **`attributes` no longer `$ref`s the internal enum files.** The three lists are now plain
  arrays of unique strings, defined in this file. Since the internal
  `property/attributes-schema` was loosened to accept any type/feature/tag string, this schema
  had been **rejecting exports we ourselves generate** — an advert carrying a newly-added type
  failed the schema we publish for it. Defining the vocabulary here also stops the internal
  `_unclassified` / `_unmapped` sentinel values appearing on the partner-facing surface.
  Loosening only: every value that validated before still validates.
- **The schema now has a `required` list and `additionalProperties: false`.** It previously had
  neither, so it validated any JSON object — `{}` included — and guaranteed nothing to the
  partners it is published for. All seventeen documented fields are now required, following the
  same convention as the other public schemas in this repo: *required* means **send the key**,
  not send a value; the nullable fields are still nullable. The field list is unchanged, and is
  the one documented in [partner_exports.md](../../partner_exports.md).

A fixture, `json/fixtures/simplified_export_sale_advert.json`, is now checked against this schema
on every CI run — there was no example document for it before.

### Fix (2026-08-26)

- Remove `agency_microsite` from `advert.required` in v1.0.0 and v1.1.0. It was listed as
  required but never defined in `advert.properties`, and with `additionalProperties: false`
  this made the schema unsatisfiable — no feed (including our own published example) could
  validate. Fixed in place: the versions were impossible to satisfy, so no valid consumer
  feed relied on the broken behaviour.

### v1.1.0 (2016-10-12)

- Change of {property.floor_plans} from array of strings, to an array of objects
- Change of {property.floor_virtual_tours} from array of strings, to an array of objects

### v1.0.0 (2016-09-01)

Initial Release
