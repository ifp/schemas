---
title: floor_plans v1.2.0 required a field that half of all adverts never have
tags: [schema, images, cdn, regression]
status: stable
completed: 2026-09-11
verified: ci
commits: [afd36a3, 57fba02]
pr: 144
---

# floor_plans v1.2.0 required a field that half of all adverts never have

Verified 11 Sep 2026 (auto tier): CI `validate` green on merge commit `3c0bb9c`; live private-vendor media (`cdn: 4`, no `original_url`) is rejected by v1.1.0 and accepted by v1.2.0 as fixed.

`floor_plans-schema_v1.2.0` shipped in `1.19.0` requiring `original_url`. A live advert, fetched
hours later, showed that **private-vendor media has no `original_url` at all**. Those files are
uploaded to us directly, so there is no source URL to record; only feed-imported media carries
one.

So the schema would have rejected every private vendor's floor plans.

## The same mistake, one version apart

v1.2.0 existed because v1.1.0 required `cloudinary_account` — a value no producer can know,
because it does not exist until after the file has been uploaded, and because we stopped using
Cloudinary years ago. The v1.2.0 write-up called that out at length.

And then v1.2.0 required `original_url` — a value that for private-vendor adverts never exists at
all.

The common cause is worth naming, because it is not carelessness about the specific field: **both
`required` lists were derived from a document rather than from production data.** v1.1.0's came
from the Cloudinary-era schema it inherited; v1.2.0's came from reading `images-schema` and
reasoning about what "ought" to be knowable at collection time. Neither was checked against a real
advert. `images-schema` — which requires only `listing_position`, `title` and `title_fr` — has
been quietly accepting both live shapes all along, and simply copying it would have been right.

## The two live shapes

From `https://config.french-property.com/adverts/full_json/{advert_id}`:

| Source | Example | `cdn` | Carries |
|---|---|---|---|
| Private vendor | `1-IFPC47364` | 4 | `path`, `title`, `title_fr`, `width`, `height`, `listing_position` |
| Feed-imported | `1634-BVI84819` | 3 | the above plus `original_url`, `original_bytes`, `archived_at` |

Two further observations from those records:

- **No Cloudinary fields appear in live data at all.** `cloudinary_account`, `public_id` and
  `version` are retained in the schemas only because `Cdn2AdvertImage` still reads them.
- **`format` and `bytes` are in `images-schema` but in neither live record.** Both optional, so
  nothing breaks, but the schema describes fields the pipeline no longer populates.
- `listing_position` starts at **1** for private vendors and **0** for feed imports.

## What shipped

`required` is now `listing_position` and `title` only. Fixed in place rather than bumped again:
v1.2.0 was hours old, had reached no consumer, and was wrong — the `agency_microsite` reasoning
from [#138](https://github.com/ifp/schemas/pull/138).

`json/fixtures/floor_plans.json` is rebuilt from the real shapes and covers four cases, including
the private-vendor one that would have caught this. Its paths and byte counts are copied from the
live records rather than invented, which the previous version's were.

Verified it still rejects what it should: bare URL strings (`advert-collector`'s current output)
and entries missing `listing_position`.

## The fixture rebuild, done in the same PR

All three remaining fixtures are now rebuilt to the live `cdn: 3` shape. `cloudinary_account`,
`public_id` and `version` are gone; so are `format` and `bytes`, which `images-schema` declares
but neither live record carries.

The diff is confined to the images arrays. The first attempt round-tripped each file through
`json.dump` and rewrote every escaped slash and `\u` escape in it — 236 changed lines of pure
noise — so it was redone as a targeted replacement preserving each file's own style.

### What the verification did and did not establish

**`ifp/system` is unchanged**, which is the meaningful result — it loads `upsert_sale_advert` via
`AdvertHelper` and `AdvertCounterTrait`:

```
before: Tests: 1424, Assertions: 3482, Errors: 43
after:  Tests: 1424, Assertions: 3482, Errors: 43
```

The 43 errors are pre-existing and unrelated. Identical assertion counts either side is a strong
signal — but partly because `AdvertHelper::setImageTitlesOnAdvertData` replaces the fixture's
images wholesale with its own `$example_image`, which is **itself still Cloudinary-shaped** in
that repo. So `ifp/system` carries a second copy of this staleness that this PR cannot reach.

**`french-property.com` could not be used at all.** Its suite fails identically with the
*original* fixture — 76 tests, 74 failures — because `spatie/ray` calls `curl_close()`, which
PHP 8.5 deprecates, and Laravel's deprecation handling turns that into a 500 on every request.
Environmental and unrelated to this change, but it means one predicted risk is **unverified
rather than cleared**: `RentalSearchControllerTest:52` sets `public_id` on the fixture's first
image to distinguish two adverts, and under a `cdn: 3` record both resolve through
`Cdn3AdvertImage` from the same `path`. That line most likely needs to set `path` instead.
