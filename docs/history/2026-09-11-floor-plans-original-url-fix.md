---
title: floor_plans v1.2.0 required a field that half of all adverts never have
tags: [schema, images, cdn, regression]
status: in-progress
completed:
commits: [afd36a3]
pr: 144
---

# floor_plans v1.2.0 required a field that half of all adverts never have

> **Awaiting verification.** Unmerged at the time of writing.

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

## Follow-up this makes urgent

**The other three fixtures are still Cloudinary-shaped**, and now there is no excuse for it —
the real shape is known. `upsert_sale_advert.json`, `elasticsearch_single_sale_advert_result.json`
and `search_engine_single_sale_advert_result.json` all carry `cloudinary_account: "test-account"`
and no `cdn` or `path`.

This is not a self-contained change. `upsert_sale_advert` is loaded by `ifp/system`'s tests
(`AdvertHelper`, `AdvertCounterTrait`) and by `french-property.com`'s. Those suites need running
before and after. The one piece of good news: `ifp/system`'s Cloudinary tests
(`AdvertImageTest`, `AdvertTest`) build their own `cdn: 2` arrays inline rather than loading our
fixture, so they are unaffected.
