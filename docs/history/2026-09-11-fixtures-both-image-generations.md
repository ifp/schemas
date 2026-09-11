---
title: The fixtures must carry both image generations, not just the new one
tags: [fixtures, images, cdn, correction]
status: in-progress
completed:
commits: []
pr: 145
---

# The fixtures must carry both image generations, not just the new one

> **Awaiting verification.** Unmerged at the time of writing.

This corrects [the fixture rebuild](2026-09-11-floor-plans-original-url-fix.md), which converted
every image in every fixture to the Bunny shape on the strength of two live adverts. Two adverts
were not enough.

## What the two adverts did not show

`IFP\Basebox\Advert::getImageFromCdn` reads:

```php
$cdn = $image_data[ 'cdn' ] ?? 2;

switch ( $cdn ) {
    case 2:
        $public_id            = $image_data[ 'public_id' ];
        $format               = $image_data[ 'format' ];
        $agency_id            = $this->getAgencyIdFromImagePublicId( $public_id );
        $image_data[ 'cdn' ]  = 3;
        $image_data[ 'path' ] = "/cloudinary-2020-11/agency_" . $agency_id . "/" . $public_id . '.' . $format;
```

An image with **no `cdn` key defaults to 2** and is rewritten on the fly into a Bunny path under
`/cloudinary-2020-11/`, then served as `cdn: 3`. That is live migration handling for every record
predating the 2020 Cloudinary→Bunny move.

So there are **three** shapes in production, not two:

| Source | `cdn` | Carries |
|---|---|---|
| Legacy, pre-2020 | absent | `cloudinary_account`, `public_id`, `version`, `format`, `bytes` |
| Feed-imported | 3 | `path`, `original_url`, `original_bytes`, `archived_at` |
| Private vendor | 4 | `path` — no `original_url` |

The old fixture was entirely legacy, which is why it exercised the shim without anyone realising.
Converting it wholesale to `cdn: 3` **silently removed the only coverage of that code path**, and
`french-property.com`'s suite was the thing that noticed.

Three claims made yesterday were wrong, all from the same cause — generalising from two adverts
that happened to be modern:

- "No Cloudinary fields appear in live data at all." They appear on every pre-2020 record.
- "`format` and `bytes` are declared but unused." `format` is **load-bearing**: the shim
  interpolates it into the path. Removing it would produce URLs ending in `.`.
- "`french-property.com`'s suite cannot run on PHP 8.5." It is a **dual-trunk repo** — `master`
  is PHP 8.3 / Laravel 11 and must be run with `php83`, which its own `CLAUDE.md` says plainly.
  Run correctly it is green: `OK (76 tests, 355 assertions)`. The 74 failures were my own error.

## What shipped

All three fixtures now carry **five legacy images** (positions 0–4, no `cdn`, with
`cloudinary_account` / `public_id` / `version` / `format` / `bytes`) and **five Bunny-native
images** (positions 5–9, `cdn: 3` with `path`). Production has both, so the fixtures should.

Verified against `french-property.com` with `php83`:

| Fixture | `RentalSearchControllerTest` |
|---|---|
| Original (all legacy) | OK — 76 tests, 355 assertions |
| All-Bunny (yesterday's) | 2 failures — all ten image URLs changed |
| Mixed (this change) | 2 failures — only the five Bunny URLs changed; the first eight assertions pass |

The remaining two failures are expected and correct: those five images genuinely render from a
different path now, so the test's expectations need updating. That is a one-for-one substitution
of five lines, already generated and verified, and it lands in `french-property.com` once this is
released.

## The lesson worth keeping

Both this and the `original_url` bug it corrects came from the same move: **inferring a rule from
the records that happened to be to hand.** The first time it was two adverts saying `original_url`
is always present. The second time it was the same two adverts saying Cloudinary is dead.

`CLAUDE.md` now says not to add to a `required` list *or remove a field as unused* without
checking live adverts, and notes that the two known sample IDs are both modern — so they cannot
answer questions about legacy records.
