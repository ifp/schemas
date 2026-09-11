---
title: ifp/schemas — situation report
updated: 2026-09-11
reconcile: 2
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

## In flight

- `fix/schema-contract-cleanup` — the above, plus this reconcile. Unmerged.

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
| `advert-collector` emits the pre-importer shape but calls it `internal_sale-advert-schema`; internal `floor_plans-schema_v1.1.0` requires Cloudinary's `public_id`, which no producer can know pre-upload, while `images-schema` requires only three pre-CDN keys | One of the two is wrong and fixing either touches a live pipeline. No fixture exercises it — `floor_plans` is `[]` in the upsert fixture |
| `advert.first_visible_at` is `{"type": "array"}` with no `items` | Every producer emits a hardcoded `[]`; nothing populates it. May be vestigial |
| `unmapped_fields` may be vestigial | No producer emits it. Removing it needs confirmation nothing reads it |
| `locality-data-schema` validates `{}` | Content comes from the locality service; tightening needs that service's behaviour confirmed |
| `property.attributes` accepts any string, per [#137](https://github.com/ifp/schemas/pull/137) "temporary" | When the enums are restored, three files need updating — `attributes-schema`, and `simplified_export` which now carries its own copy |

## Next action

1. Merge `fix/schema-contract-cleanup`, then finalise the `reconciled` tag.
2. Verify the two history docs currently `status: in-progress` and tell Claude to promote them.
3. Take the `floor_plans` / `advert-collector` stage mismatch to whoever owns the collector —
   it is the only open item that touches a live pipeline.

## Roadmap

| Date | What shipped | History doc |
|---|---|---|
| 2026-09-11 | Partner export contract, queue envelope, proximity WIP deleted | [2026-09-11-schema-contract-cleanup.md](docs/history/2026-09-11-schema-contract-cleanup.md) |
| 2026-09-11 | Schema validator + CI | [2026-09-11-schema-validator.md](docs/history/2026-09-11-schema-validator.md) |
