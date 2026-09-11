# Internal Sale Advert Schema Changelog

### Fix to v1.2.0, in place (2026-09-11)

- **`floor_plans-schema_v1.2.0` no longer requires `original_url`.** Required is now
  `listing_position` and `title` only.

  As first cut, v1.2.0 required `original_url` — and then a live advert showed that
  **private-vendor media has no `original_url` at all**. Those files are uploaded to us
  directly, so there is no source URL to record; only feed-imported media carries one. So the
  first cut of v1.2.0 would have rejected every private vendor's floor plans.

  That is precisely the fault v1.2.0 was written to correct — v1.1.0 required
  `cloudinary_account`, a value no producer could know at that point, and the first v1.2.0
  required `original_url`, a value that for half of all adverts never exists. The lesson is the
  one this repo keeps teaching: a `required` list derived from a document rather than from
  production data will be wrong.

  Fixed in place rather than bumped again: v1.2.0 was hours old, had reached no consumer, and
  was wrong. Same reasoning as the `agency_microsite` fix.

  Both live shapes are now covered by `json/fixtures/floor_plans.json`, so the regression is
  locked in:

  | Source | `cdn` | Carries |
  |---|---|---|
  | Feed-imported | 3 | `original_url`, `original_bytes`, `archived_at`, `path` |
  | Private vendor | 4 | `path` only — no source URL, no bytes, no `archived_at` |

### v1.2.0 (2026-09-11)

- Change of `{property.floor_plans}` to `floor_plans-schema_v1.2.0`, which mirrors
  `images-schema`: only the three keys knowable at collection time are required, and everything a
  CDN adds later is optional.

  **Why.** v1.1.0 required all eleven keys, including `cloudinary_account` and `public_id` — a
  vendor we stopped using years ago, and values no producer can know before the file is uploaded.
  Images were never like this: `images-schema` requires only `listing_position`, `title` and
  `title_fr`, carries `cdn` and `path` for Bunny (CDN generations 3 and 4) alongside the legacy
  Cloudinary trio (generation 2), and lets the `cdn` field say which applies. Floor plans never
  got that treatment and stayed frozen in the Cloudinary era.

  The practical effect: `advert-collector` emits floor plans as bare URL strings
  (`PublicAdvertMapper::flatUrls`), which no version accepts — but the obvious fix, emitting
  objects the same way it already does for images, **failed v1.1.0** on `cloudinary_account`.
  v1.1.0 made the sensible fix impossible. Under v1.2.0 that same output validates.

  `floor_plans-schema_v1.2.0` also adds `cdn`, `path`, `archived_at` and `title_fr` (all
  optional) so floor plans and images finally describe the same lifecycle. The Cloudinary fields
  are kept, optional, because `IFP\Basebox\AdvertImage\Cdn2AdvertImage` still reads them.

- `self.version` in this file reads `1-2-0`. Every earlier versioned schema in this repo — public
  and internal, v1.0.0 and v1.1.0 alike — says `1-0-0` regardless of its filename. That is a
  long-standing inconsistency, not a convention; new files should not inherit it. The published
  files are left alone.

### Fix (2026-09-11)

### Fix (2026-09-11)

- **Declare `unexpected_fields` and `missing_fields`.** The importer's enqueuer sets both on
  every outgoing queue message (`importer/processor/enqueuer.rb:19-21`), but neither was in the
  schema, and the top level is `additionalProperties: false` — so the envelope this schema
  describes **rejected the message the importer actually emits**. Verified against `master`
  before the change: adding those two keys to `upsert_sale_advert.json` produced *"Additional
  properties are not allowed"*. Both are typed `["object", "null"]` and are optional. Nothing
  downstream reads them today (the loader never references either), so this is a documentation
  correction to the envelope, not a behaviour change.
- **`unmapped_fields` is marked as possibly vestigial.** No producer found emits it; it looks
  like the name the two fields above were meant to have. Left in place — removing it needs
  someone to confirm nothing relies on it.

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
