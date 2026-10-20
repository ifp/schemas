---
title: Public sale-advert schema v1.2.0 adds the property's coordinates
tags: [public-schema, geo, lat-lon, v1.2.0, advert-collector, 119]
status: in-progress
completed:
commits: [f2e7f22]
pr: 147
---

# Public sale-advert schema v1.2.0 adds the property's coordinates

> **Waiting on its check (auto tier).** It cannot pass before the merge, because v1.2.0's `$ref` resolves
> `geo-public-schema_v1.1.0.json` from `master`. Check, after the merge:
> 1. CI (`validate`) is green on the merge commit.
> 2. `https://raw.githubusercontent.com/ifp/schemas/master/json/public/public_sale-advert-schema_v1.2.0.json`
>    and `…/geo-public-schema_v1.1.0.json` both return 200.
> 3. Tag `1.22.0` is cut and pushed.
>
> Then flip this doc to `stable` / `verified: ci`.

## Why

JB French Houses (agency 119) names hamlets ("Clairet", "Bonen", "Kerraden") that are not communes, so
36 of its 148 live adverts were placed by department only on 20 Oct 2026. JB agreed to send
coordinates. advert-collector
[#119](https://github.com/ifp/advert-collector.french-property.com/pull/119) carries them through to
Locality, which tries coordinates first (the nearest commune within 25 km). But public schema v1.1.0 had
nowhere to put them: `geo-public-schema_v1.0.0`'s `user_data` is `additionalProperties: false`. So JB's
feed is off-contract until a version has the keys.

## What shipped

- **`json/public/geo-public-schema_v1.1.0.json`** is v1.0.0 plus `user_data.lat` and `user_data.lon`. Each
  is `null` or a number (latitude −90…90, longitude −180…180), with a description of the format for
  advertisers. Both are **required but nullable**, per the public convention that a producer sends every
  key.
- **`json/public/public_sale-advert-schema_v1.2.0.json`** is v1.1.0 with `property.geo` pointed at
  geo-public v1.1.0. Its `self.version` is `1-2-0`, the file's real version. Earlier public files keep
  their `1-0-0`.
- A v1.2.0 example (the v1.1.0 one plus `"lat": 46.2561, "lon": 0.8047`), v1.2.0 notes covering only the
  two additions, the changelog entry, and README links. The new pair is in `bin/validate.py`'s `PAIRS`.
- v1.0.0, v1.1.0 and geo-public v1.0.0 are unchanged and still published.

## Checked in both directions (20 Oct 2026, on the branch)

`python3 bin/validate.py`: PASSED, with every fixture valid, including the new v1.2.0 pair. Then, against
v1.2.0 with `$ref`s resolved from the working tree:

| Document | Expected | Result |
|---|---|---|
| v1.2.0 example | valid | valid |
| `lat` / `lon` both `null` | valid | valid |
| v1.1.0 example (no `lat` / `lon` keys) | rejected | `'lat' is a required property` |
| `lat: 100` | rejected | `100 is greater than the maximum of 90` |
| `lon: -181` | rejected | `-181 is less than the minimum of -180` |
| `lat: "46.2561"` (string) | rejected | `'46.2561' is not of type 'null', 'number'` |
| v1.2.0 example against **v1.1.0** | rejected (unchanged) | `'lat', 'lon' were unexpected` |

## Findings worth keeping

- **Numbers only, unlike the internal `user_*` copy.** The internal `geo.user_data` is loosely typed on
  purpose, but this is the public contract, and a JSON producer can always send a number. advert-collector
  still accepts a numeric string from any feed, so a loose producer is not penalised in practice.
- **No consumer validates public feeds against a version today.** advert-collector reads `lat` / `lon`
  from v1.1.0 and v1.2.0 feeds alike. So this version documents the contract and gives advertisers
  something to validate against; it does not gate anything.
- **The release check here was reading the wrong tag.** `git describe --tags --abbrev=0` returns
  `reconciled`, the reconcile marker tag, not the last release. `CLAUDE.md` and the reconcile
  `project.md` now pick the newest bare-SemVer tag instead.
