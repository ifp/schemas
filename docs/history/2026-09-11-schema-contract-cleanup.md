---
title: Partner export contract, queue envelope, and the proximity WIP
tags: [schema, public-contract, internal-envelope, cleanup]
status: in-progress
completed:
commits: [76fe281, 984660d]
pr: 142
---

# Partner export contract, queue envelope, and the proximity WIP

> **Awaiting verification.** Unmerged at the time of writing. `status` stays `in-progress` and
> `completed:` stays blank until someone has confirmed these are the right calls — particularly
> the two items deliberately left alone.

Worked through the six open questions the [first reconcile](2026-09-11-schema-validator.md) put
in the SITREP. Four were real and are fixed. **Two were not defects at all**, and one of them
would have become a production bug had it been "fixed" as written.

## Fixed

### `simplified_export` rejected our own output

Its `attributes` block `$ref`'d the three internal enum files.
[#137](https://github.com/ifp/schemas/pull/137) loosened `property/attributes-schema` to accept
any type/feature/tag string; this was the third copy of that vocabulary and was still strict, so
an advert carrying a newly-added type failed the schema we publish for our own export. Verified
before the change: `bastide_provencale_neuve`, `heat_pump` and `off_grid` were accepted by
`property.attributes` and rejected here.

It now defines its own any-string arrays rather than `$ref`ing internal files.
[#139](https://github.com/ifp/schemas/pull/139) solved the equivalent problem by making
`advert.pre_attributed` share the internal definition — the opposite choice was right here,
because a *public* schema reaching into internal enum files was also leaking the internal
`_unclassified` / `_unmapped` sentinel values onto the partner-facing surface. The cost is that
restoring the enums later means updating this file too.

### `simplified_export` guaranteed nothing

No `required`, `additionalProperties: true` — it validated any JSON object, `{}` included, while
`partner_exports.md` presented it as our export contract. All seventeen documented fields are now
required, following this repo's public-schema convention that *required* means **send the key**,
not send a value; nullable fields stay nullable. Field list unchanged.

Both changes applied in place rather than version-bumped: one constraint rejected valid output
and the other asserted nothing, so no partner could have been depending on either — the same
reasoning as [#138](https://github.com/ifp/schemas/pull/138).

### The internal envelope rejected the importer's own messages

`importer/processor/enqueuer.rb:19-21` sets `unexpected_fields`, `mapped_enums` and
`missing_fields` on every outgoing queue message. Only `mapped_enums` was in the schema, and the
top level is `additionalProperties: false`, so the envelope rejected the message the importer
actually emits. Verified against `master`: *"Additional properties are not allowed
('missing_fields', 'unexpected_fields' were unexpected)"*.

Both are now declared, optional, typed `["object", "null"]`. The loader reads neither, so nothing
changes behaviourally — the schema simply now describes the payload. `unmapped_fields` is kept
but marked possibly vestigial: no producer emits it, and it looks like the name these two were
meant to have.

### The abandoned proximity WIP is gone

Nine orphaned files, all remnants of the never-finished `249ccef "proximity wip"`: six 0-byte
placeholders under `geo/distances_from/`, plus `locality-wip.json` (not valid JSON),
`locality-data-nearest-schema.json` (not a valid draft-07 schema) and `locality-data-schema-wip.json`
(`$ref`s a missing file). Recoverable from history if the feature is ever revived.

`bin/validate.py` goes from nine warnings to one.

## Not fixed, because they were not broken

**`virtual_tours` differs by design.** Public is `[{title, original_url}]`, internal is `string[]`.
Floor plans and images pass through Cloudinary and gain `public_id`, dimensions and bytes; virtual
tours are external video links that never touch our CDN, so only the URL survives.
`PublicAdvertMapper::flatUrls` in `advert-collector` performs the conversion and documents it in
its docblock. Changing either side would break the importer, which sifts `virtual_tours` alongside
`highlights` as a flat list.

**`let`/`to_let` vs `rented`/`to_rent` differs by design — and the planned fix was a bug.** The
intended change was to loosen the public enum to accept both spellings, as a pure non-breaking
widening. It would have broken rental filtering: `PublicAdvertMapper::isForSale` drops rentals by
testing for exactly `['let', 'to_let']`, so a record arriving as `to_rent` would have passed that
filter and been ingested as a sale. The loader canonicalises to the internal spelling
(`DefaultValueTransformer:55`). Both cases are now written up in `CLAUDE.md` under a heading that
says not to touch them.

## Findings recorded, not actioned

**`advert-collector` and `floor_plans` disagree about what stage they are at.** The collector
describes its output as `internal_sale-advert-schema` but emits the *pre-importer* shape — flat
URLs for `floor_plans`, no Cloudinary fields. Internal `floor_plans-schema_v1.1.0` requires all
eleven keys including `public_id`, which no producer can know before upload, while `images-schema`
requires only the three pre-CDN keys for the same lifecycle. One of the two is wrong. Nothing
catches it because `floor_plans` and `virtual_tours` are both `[]` in `upsert_sale_advert.json`.

**`locality-data-schema` is hollow** — properties, but no `required` and open
`additionalProperties`, so it validates `{}`. It is the last remaining validator warning. Its
content comes from the locality service, so fields may legitimately be absent; tightening it needs
that service's behaviour confirmed first.

## Test plan

```bash
python3 bin/validate.py          # expect: PASSED, 1 warning, exit 0
```

Seven fixture/schema pairings now, up from six — `json/fixtures/simplified_export_sale_advert.json`
is new, and its absence is precisely why neither `simplified_export` problem had been noticed.

Behaviour checks run against the new schema before commit: `{}` is now rejected, a missing
`price_eur` is rejected, an unexpected key is rejected, novel enum values are accepted (matching
`property.attributes`), and explicit `null`s in nullable fields are accepted.
