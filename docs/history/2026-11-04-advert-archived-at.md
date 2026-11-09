---
title: Internal advert schema records when an advert was archived
tags: [internal-schema, advert, archived-at, task-1402, archived-advert-galleries]
status: stable
completed: 2026-11-09
verified: ci
commits: [0c22061]
pr: 148
---

# Internal advert schema records when an advert was archived

Merged 4 Nov 2026 ([#148](https://github.com/ifp/schemas/pull/148)) and released as `1.23.0`. Verified 9 Nov 2026
(folded reconcile of #149): CI `Validate schemas` green on the merge commit `0c22061`; tag `1.23.0` points at it; the raw
`master` `advert-schema_v1.0.0.json` gives `.properties.archived_at.format` = `"date-time"`.

## What changed

`advert-schema_v1.0.0.json` gains an optional `advert.archived_at`: `null` or an ISO 8601 date-time, when
the advert was last archived. It is added in place, as `advert.external_reference` was
([#125](https://github.com/ifp/schemas/pull/125)): the key is optional and `advert` keeps
`additionalProperties: true`, so every advert valid before stays valid. Changelog entry in
`json/internal/internal_sale-advert-schema_changelog.md`.

## Why

Company Memory TASK-1402, part of the plan in `reports/french-property/archived-advert-galleries/plan.md`.
An advert archived for more than 12 months will show only its main photo, and its other photos will stop
being served, so the pipeline needs to know when each advert was archived. Nothing recorded it:
`advert.status` only says `archived`.

- **ifp/system** sets it in `Advert::save()` (the release after `25.12.0`): now on the save that archives an
  advert, the stored date while it stays archived, removed when it leaves archived. A row archived before
  the change gets its own `updated_at`.
- **Loader** carries a one-off backfill, `ifp:backfill-archived-at`, for the ~522k adverts already archived.
- **Search** returns it through `show` once on that release (it is in ifp/system's
  `ifp_required_advert_keys` allow-list).

The schema change is for the record: nothing failed validation without it.

## Not to be confused with

`property.images[].archived_at` and `property.floor_plans[].archived_at` already exist on feed-imported
media. They are a different date, about the image's own copy, and are untouched.

## Test plan

- `python3 bin/validate.py` passes on the branch (one existing warning, about `locality-data-schema`).
