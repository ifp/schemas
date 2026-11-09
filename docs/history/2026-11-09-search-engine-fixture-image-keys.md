---
title: The Search-output fixture no longer gives Bunny images keys Search never returns
tags: [fixtures, search-engine, images, bunny, search, task-1402]
status: in-progress
completed:
commits: []
pr: 149
---

# The Search-output fixture no longer gives Bunny images keys Search never returns

> **Waiting on its check (auto tier).** After the merge:
> 1. CI (`Validate schemas`) is green on the merge commit, and tag `1.23.1` is cut on it.
> 2. search.french-property.com on `1.23.1` passes `ElasticSaleAdvertSearchSchemaMapperTest` in CI (its TASK-1402 PR).
>
> Then flip this doc to `stable` / `verified: ci`.

## What changed

`json/fixtures/search_engine_single_sale_advert_result.json`: the five Bunny images (`cdn: 3`, listing positions
5–9) lose `archived_at`, `original_url` and `original_bytes`, each `null`. Nothing else changes.

## Why

The fixture is what Search's API returns for the ES fixture `elasticsearch_single_sale_advert_result.json`, and Search
tests exactly that (`ElasticSaleAdvertSearchSchemaMapperTest`). Search's `ElasticSaleAdvertSearchSchemaMapper` keeps
eleven image keys (`listing_position`, `title`, `title_fr`, the Cloudinary trio, `width`, `height`, `format`, `cdn`,
`path`), so its output never carries these three. The fixtures rebuild in `1.21.0`
([#145](https://github.com/ifp/schemas/pull/145)) gave them `null` in the Search result. Search was locked at `1.14.2`
until 9 Nov 2026, so nothing noticed; its bump to `1.23.0` for TASK-1402 failed that one test on this.

These output fixtures aren't schema-validated (`CLAUDE.md`), so `bin/validate.py` couldn't catch it. The ES fixture
keeps the three keys: it stands for what is stored, and it is what proves the mapper strips them.

## Test plan

- `python3 bin/validate.py`: PASSED.
- Search's `ElasticSaleAdvertSearchSchemaMapperTest` with this fixture: 3/3 pass (1 failed on `1.23.0`).
- Other consumers of this fixture (ifp/system `AdvertTest`, `AdvertSearchTest`; network_sites
  `FrenchAdvertAndSearchTest`) read `cdn` / `path`; the dropped keys were `null`, so reads are unchanged.
