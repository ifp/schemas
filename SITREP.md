---
title: ifp/schemas — situation report
updated: 2026-09-11
reconcile: 3
---

# ifp/schemas — situation report

Canonical JSON Schemas for IFP advert data. Read [CLAUDE.md](CLAUDE.md) first — it carries the
release model and the conventions that read as bugs but aren't.

## Right now

- **Released at `1.17.0`** (11 Sep 2026), covering [#138](https://github.com/ifp/schemas/pull/138),
  [#139](https://github.com/ifp/schemas/pull/139) and [#140](https://github.com/ifp/schemas/pull/140).
  This repo ships by tag, not by merge.
- **The repo validates itself** — `bin/validate.py` plus CI on every branch
  ([#141](https://github.com/ifp/schemas/pull/141)). Seven fixture/schema pairings, one warning.
- **The partner export contract now means something.** `simplified_export` previously validated
  `{}` and rejected our own output; both fixed.
- **The internal envelope matches the importer's actual queue message** for the first time.
- **The abandoned proximity WIP is deleted** — nine orphaned files, six of them empty.
- **Released at `1.18.0`** covering [#142](https://github.com/ifp/schemas/pull/142).
- **`floor_plans-schema_v1.2.0`** (and `internal_sale-advert-schema_v1.2.0`) — floor plans now
  describe the same lifecycle as images instead of requiring a CDN we dropped years ago.

## In flight

- `feat/floor-plans-schema-v1.2.0` — the v1.2.0 schemas, plus this reconcile. Unmerged.

## Settled — do not reopen

Two differences between the public and internal schemas were on this list as defects. They are
deliberate, and the write-ups are in [CLAUDE.md](CLAUDE.md):

- **`virtual_tours`** objects vs strings — floor plans go through Cloudinary, virtual tours are
  external links that don't.
- **`let`/`to_let` vs `rented`/`to_rent`** — and loosening the public enum, which was the plan,
  would have let rentals through `PublicAdvertMapper::isForSale` and been ingested as sales.

## Known open questions — decisions needed, not tasks

| Question | Why it isn't just a fix |
|---|---|
| **The fixtures describe a CDN we stopped using years ago.** `upsert_sale_advert.json` and both response fixtures carry `cloudinary_account: "test-account"` and no `cdn`/`path`. Every consuming repo's tests load these | Needs a real record from the loader box to copy the live shape from. **Biggest open item** — our test data has not matched production for years |
| `advert-collector` emits floor plans as bare URL strings and needs to emit objects | v1.2.0 makes the fix possible; nothing here forces it. Belongs to whoever owns the collector |
| `advert.first_visible_at` is `{"type": "array"}` with no `items` | Every producer emits a hardcoded `[]`; nothing populates it. May be vestigial |
| `unmapped_fields` may be vestigial | No producer emits it. Removing it needs confirmation nothing reads it |
| `locality-data-schema` validates `{}` | Content comes from the locality service; tightening needs that service's behaviour confirmed |
| `property.attributes` accepts any string, per [#137](https://github.com/ifp/schemas/pull/137) "temporary" | When the enums are restored, three files need updating — `attributes-schema`, and `simplified_export` which now carries its own copy |

## Next action

1. Merge `feat/floor-plans-schema-v1.2.0`, finalise the `reconciled` tag, cut `1.19.0`.
2. **Get a live advert record and rebuild the fixtures.** Everything else on this page is smaller
   than the fact that our test data describes a dead CDN.
3. Tell `advert-collector`'s owner that emitting floor plan objects is now possible.
4. Verify the three history docs currently `status: in-progress`.

## Roadmap

| Date | What shipped | History doc |
|---|---|---|
| 2026-09-11 | Floor plans schema v1.2.0 | [2026-09-11-floor-plans-schema-v1.2.0.md](docs/history/2026-09-11-floor-plans-schema-v1.2.0.md) |
| 2026-09-11 | Partner export contract, queue envelope, proximity WIP deleted | [2026-09-11-schema-contract-cleanup.md](docs/history/2026-09-11-schema-contract-cleanup.md) |
| 2026-09-11 | Schema validator + CI | [2026-09-11-schema-validator.md](docs/history/2026-09-11-schema-validator.md) |
