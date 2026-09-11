---
title: Floor plans schema v1.2.0 — one lifecycle, three CDN generations
tags: [schema, internal-envelope, images, cdn]
status: stable
completed: 2026-09-11
verified: ci
commits: [7e472ed]
pr: 143
---

# Floor plans schema v1.2.0 — one lifecycle, three CDN generations

Verified 11 Sep 2026 (auto tier): CI `validate` green on merge commit `2a3ed5e`; a collector-shaped `{listing_position, title, original_url}` object is rejected by `floor_plans-schema_v1.1.0` and accepted by v1.2.0 — the exact behaviour the bump existed for.

## The problem, stated properly

`floor_plans-schema_v1.1.0` required all eleven of its keys, including `cloudinary_account` and
`public_id`. Cloudinary was dropped years ago, and those values cannot exist until after a file
has been uploaded — so the schema mandated a dead vendor *and* post-processing values at a point
in the pipeline where neither is knowable.

Images were never like this, and comparing the two is what explains it:

| | `images-schema` | `floor_plans-schema_v1.1.0` |
|---|---|---|
| Required | `listing_position`, `title`, `title_fr` | all eleven keys |
| Bunny fields | `cdn`, `path` | **absent** |
| Cloudinary fields | present, optional | present, **required** |

There are three CDN generations, and the `cdn` integer on each record says which applies:

| `cdn` | CDN | Populates |
|---|---|---|
| 2 | Cloudinary — legacy | `cloudinary_account`, `public_id`, `version` |
| 3, 4 | Bunny — current (`precache_cdns` = `[3, 4]`) | `path` |

`images-schema` was updated when Bunny arrived — it gained `cdn` and `path`, and requires neither
generation's fields. `floor_plans-schema` never was. It is still describing 2016.

## Why a new version and not an in-place fix

Demonstrated before committing, against `advert-collector`'s real behaviour:

```
advert-collector's CURRENT output — bare URL strings from PublicAdvertMapper::flatUrls:
  vs v1.1.0 -> rejected, not of type 'object'
  vs v1.2.0 -> rejected, not of type 'object'

advert-collector's output IF it built objects the way it already does for images:
  vs v1.1.0 -> rejected, 'cloudinary_account' is a required property
  vs v1.2.0 -> ACCEPTED
```

The collector is wrong either way — it emits strings where both versions want objects. But the
*obvious* fix, building floor plan records exactly the way it already builds photo records, was
**impossible under v1.1.0**. That is what made this a version bump rather than a loosening: the
old version isn't merely strict, it rules out the correct producer behaviour.

## What shipped

`floor_plans-schema_v1.2.0` mirrors `images-schema`:

- **Required** — `listing_position`, `title`, `original_url`. The three things knowable when the
  advert is collected. `original_url` is nullable, because an archived entry may no longer have
  one, following this repo's convention that *required* means send the key.
- **Optional** — `cdn`, `path`, `cloudinary_account`, `public_id`, `version`, `width`, `height`,
  `format`, `bytes`, `original_bytes`, `archived_at`, `title_fr`.

The Cloudinary fields are kept rather than removed: `IFP\Basebox\AdvertImage\Cdn2AdvertImage`
still reads all three to build `cdn2.french-property.com` URLs.

`title_fr` is new to floor plans and unpopulated — present so they can adopt images' bilingual
treatment without another bump.

`internal_sale-advert-schema_v1.2.0.json` is v1.1.0 with the `floor_plans` `$ref` bumped, which
is exactly how v1.1.0 came about from v1.0.0. Both older versions stay published.

## Findings

**`self.version` has always been wrong.** Every versioned schema in this repo — public and
internal, v1.0.0 and v1.1.0 — carries `"version": "1-0-0"` in its self-describing block
regardless of its filename. `internal_sale-advert-schema_v1.2.0.json` is the first to state its
real version. Published files left alone; the note is in `CLAUDE.md` so new files don't inherit it.

**The fixtures have not resembled production for years.** `upsert_sale_advert.json` and both
response fixtures describe images in Cloudinary terms — `cloudinary_account: "test-account"`,
`public_id`, `version`, and no `cdn` or `path` anywhere. Since the live pipeline has been Bunny
for years, every test in every consuming repo that loads these fixtures is exercising a shape
production no longer produces. `json/fixtures/floor_plans.json` is the first fixture in the repo
to carry a Bunny-shaped entry, and even its `path` value is **inferred** from
`BunnyCdnHelperTrait` rather than copied from a live row.

This is the largest thing found so far and it is not fixed here — correcting it needs a real
record from the loader box, which this session could not reach.

## Test plan

```bash
python3 bin/validate.py          # expect: PASSED, 1 warning, exit 0
```

Nine fixture/schema pairings, up from seven. `json/fixtures/floor_plans.json` covers all three
stages deliberately: one entry collected but not yet processed, one Bunny-processed (`cdn: 3`,
`path`), one legacy Cloudinary (`cdn: 2`, `public_id`).

## Follow-ups

- **`advert-collector` still emits bare URL strings** and needs changing to emit objects. v1.2.0
  now makes that possible; nothing in this repo forces it.
- **Rebuild the fixtures from a live record**, per the finding above.
