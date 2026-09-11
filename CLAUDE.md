# CLAUDE.md — ifp/schemas

Canonical JSON Schemas for IFP advert data, plus the fixtures every consuming system tests
against. Two contracts live here:

- **Public** (`json/public/`) — what a third party sends *us*. A contract with agencies and
  syndicators; strict (`additionalProperties: false`, every key in `required` but nullable).
- **Internal** (`json/internal/`) — the envelope that moves *between* our own services
  (importer → checker → loader → search). Permissive where it needs to be, and carries the
  workflow/commercial layer the public schema has no business seeing.

It is also a Composer package, `ifp/schemas`, whose only PHP is
[`src/Fixtures/Loader.php`](src/Fixtures/Loader.php) — a thin reader for the fixture and enum
JSON files so consumers can pull them into their test suites.

## Project status — read at session start

- [`SITREP.md`](SITREP.md) — where the repo is right now, open questions, next actions
- [`docs/TODO.md`](docs/TODO.md) — forward-looking backlog, mostly contract decisions
- [`docs/README.md`](docs/README.md) — index of the internal docs

## The release model — read this before changing anything

**Merging to `master` releases nothing.** Consumers pin a Composer tag:

```
"repositories": [{"type": "vcs", "url": "https://github.com/ifp/schemas"}],
"require": {"ifp/schemas": "^1.16.0"}
```

`ifp/system` is the direct consumer; `french-property.com` and `loader.french-property.com`
register the VCS repository and pull it transitively. So any change that consumers need
requires **a new git tag** after the PR merges. Tags are bare SemVer, no `v` prefix
(`1.16.0`, not `v1.16.0`).

> **Check `git log $(git describe --tags --abbrev=0)..master` before assuming a merged change is
> live.** This has bitten already: [#138](https://github.com/ifp/schemas/pull/138) and
> [#139](https://github.com/ifp/schemas/pull/139) sat merged and untagged, reaching no consumer,
> until `1.17.0` was cut on 11 Sep 2026.

### Two version axes, easily confused

| Axis | Where | Changes when |
|---|---|---|
| **Package tag** | `git tag` | Any release to consumers, including a docs-only fix |
| **Schema file version** | `_v1.1.0` in the filename, `self.version` inside the file | Only when a schema's *shape* changes; old versions stay published and readable |

A package tag bump is routine. A schema file version bump is a new file plus a changelog
entry, and the old file is never deleted — third parties are still validating against it.
Versioning loosely follows [SchemaVer](https://github.com/ifp/iglu/wiki/SchemaVer).

Fix in place instead of bumping only when the affected version was **impossible to satisfy**,
so no valid consumer feed could have depended on the old behaviour
([#138](https://github.com/ifp/schemas/pull/138) is the precedent, and the reasoning is in the
changelog entry).

## `$ref`s point at `master`, not at your tag

Every cross-file reference is an absolute URL:

```json
{"$ref": "https://raw.githubusercontent.com/ifp/schemas/master/json/internal/property/geo-schema_v1.0.0.json"}
```

Two consequences worth holding on to:

1. **A tagged release is not self-consistent.** Install `1.15.0` and its `$ref`s still resolve
   to whatever is on `master` today. Changing a `$ref`'d sub-schema therefore affects every
   released version at once.
2. **Local validation needs a URL rewrite.** Point the resolver at the working tree, or you
   validate against `master` rather than your branch — which silently hides the change you are
   testing.

## Validating a change

```bash
cd /Users/ingram/code/schemas && python3 bin/validate.py
```

Needs `pip install 'jsonschema~=4.25'` once. CI runs the same script on every branch
(`.github/workflows/validate.yml`). It checks that every live schema is valid draft-07, that
every `$ref` resolves, and that each fixture still satisfies its schema — with the
`master`-pinned `$ref` URLs rewritten to the working tree, so you are testing your branch and
not `master`.

Two things it deliberately only warns about: **orphaned files** (nothing live `$ref`s them, so
they cannot break a consumer — the abandoned proximity WIP under `geo/` lives here), and
**hollow schemas** (`type: object` with no `required` and open `additionalProperties`, which
validate any object including `{}`).

**A green run is necessary, not sufficient.** Always check the change in both directions: that
the fixtures still pass, *and* that the change actually rejects what it is meant to reject. A
loosening that passes every fixture may have loosened nothing. Add the new pairing to `PAIRS`
in `bin/validate.py` if you add a fixture.

`elasticsearch_single_sale_advert_result.json` and `search_engine_single_sale_advert_result.json`
are downstream response shapes, not schema-validated — they wrap an advert in `hits.hits[]._source`
and `data` respectively, and they still have to be updated by hand when a field moves.

## Images and floor plans — one lifecycle, three CDN generations

An image or floor plan arrives from the agency's feed with only a source URL and maybe a title.
Everything else is added later, by whichever CDN processed it. The `cdn` integer says which:

| `cdn` | CDN | Fields it populates |
|---|---|---|
| 2 | Cloudinary — **legacy**, dropped years ago | `cloudinary_account`, `public_id`, `version` |
| 3, 4 | Bunny — current (`precache_cdns` in the loader) | `path` |

`IFP\Basebox\AdvertImage\Cdn2AdvertImage` still reads the Cloudinary trio, which is why those
fields survive in the schemas. Both `images-schema` and `floor_plans-schema_v1.2.0` therefore
require **only `listing_position` and `title`** (images also requires `title_fr`) and leave
everything else optional.

**Two shapes occur in live data, and anything you write must accept both:**

| Source | `cdn` | Carries |
|---|---|---|
| Feed-imported | 3 | `path`, `original_url`, `original_bytes`, `archived_at`, `width`, `height` |
| Private vendor | 4 | `path`, `width`, `height` — **no `original_url`**, no bytes, no `archived_at` |

Private-vendor files are uploaded to us directly, so there is no source URL to record. This has
now caused the same bug twice: v1.1.0 required `cloudinary_account` (unknowable before upload),
and v1.2.0's first cut required `original_url` (never exists for private vendors). **Do not add
anything to a `required` list here without checking it against a live advert** —
`https://config.french-property.com/adverts/full_json/{advert_id}` (login required); `1-IFPC47364`
is a private vendor and `1634-BVI84819` is feed-imported. Note also that `format` and `bytes`
appear in `images-schema` but in neither live sample.

**`floor_plans-schema_v1.1.0` is the exception, and it is wrong** — it requires all eleven keys
including `cloudinary_account` and `public_id`, so it mandates a dead vendor and values no
producer can know before upload. Use v1.2.0 (via `internal_sale-advert-schema_v1.2.0`). Both old
versions stay published.

## Layout

```
json/public/          the third-party feed contract + examples + changelog
json/internal/        the pipeline envelope; advert-schema and metadata-schema sit here
  property/           one file per property sub-object (price, geo, images, attributes, …)
    geo/              French admin hierarchy: locality, department, region, commune, ski
      distances_from/ airports, autoroutes, eurotunnel, TGV, train, ferry — ALL 0 BYTES,
                      abandoned proximity WIP; locality*-wip / -nearest files here are broken too
    enums/            types / features / tags: the enum + singular/plural EN/FR lookups
json/fixtures/        canonical documents the consuming systems test against
src/Fixtures/         the Composer package's only PHP — loadFixture() / loadEnum()
systems/              how each system uses the schema (loader.md, importer.md are real;
                      checker.md and quota.md are 0 bytes)
```

## Conventions that are not obvious from the files

- **The public schema requires everything but allows null.** "Required" here means *send the
  key*, not *send a value*. A feed omitting a key fails; a feed sending `null` passes. This is
  deliberate — it forces producers to be explicit about absent data.
- **The internal schema pairs as-supplied with normalised values.** `user_size`/`size`,
  `user_unit`/`unit`, `user_amount`/`amount`, `geo.user_data.*` vs `geo.locality.data.*`. The
  `user_*` copy is the feed's own value and is loosely typed on purpose (a CSV feed sends
  `"46.2561"` as a string); the normalised copy is strictly typed. **Don't "fix" a loose
  `user_*` type** — the looseness is the feature.
- **Enum files do double duty.** `enums/*-schema-enum.json` is the validating schema;
  `enums/*-schema-lookup-{singular,plural}[-fr].json` are display-label maps consumed via
  `Loader::loadEnum()`. Adding an enum value means touching the enum file *and* four lookups.
- **`property.attributes` currently accepts any string** for types/features/tags —
  [#137](https://github.com/ifp/schemas/pull/137) loosened it and the PR title says
  *temporary*. `advert.pre_attributed` `$ref`s the same file so the two cannot drift apart;
  when the enums are restored, both tighten together. **`simplified_export` is the third place
  this vocabulary appears** and it deliberately does *not* share the definition — a public
  schema should not reach into internal enum files, and doing so leaked the `_unclassified` /
  `_unmapped` sentinels to partners. It carries its own any-string arrays, so restoring the
  enums means updating it too.
- **Empty placeholder files are a habit here.** `systems/checker.md`, `systems/quota.md` and
  all six `geo/distances_from/*.json` are 0 bytes. Check a file has content before citing it.

## Public and internal differ on purpose — don't "fix" these

The public schema is the agency-facing contract; the internal one is our pipeline envelope.
Where they disagree it is usually because something converts between them. Two cases look like
bugs and are not:

- **`virtual_tours` is `[{title, original_url}]` in public and `string[]` in internal.**
  Deliberate. Floor plans and images go through Cloudinary, so internally they become objects
  carrying `public_id`, dimensions and bytes. Virtual tours are external video links that never
  touch our CDN, so only the URL survives. `PublicAdvertMapper::flatUrls`
  (`advert-collector`) does the conversion and says so in its docblock. Changing either side
  would break the importer, which sifts `virtual_tours` alongside `highlights` as a flat list.
- **`property.status` says `let`/`to_let` in public and `rented`/`to_rent` in internal.**
  Deliberate, and **do not loosen the public enum to accept the internal spellings.**
  `PublicAdvertMapper::isForSale` drops rentals by testing for exactly `['let', 'to_let']`, so a
  record arriving as `to_rent` would sail past that filter and be ingested as a sale. The
  loader canonicalises to the internal spelling (`DefaultValueTransformer:55`).

Genuinely open, and each needing a decision rather than a patch:

- `advert.first_visible_at` is `{"type": "array"}` with no `items`; every producer found emits
  a hardcoded `[]` and nothing populates it.
- `self.version` says `1-0-0` in every published schema regardless of its filename — public and
  internal, v1.0.0 and v1.1.0 alike. `internal_sale-advert-schema_v1.2.0.json` is the first to
  carry its real version. The older files are left alone; don't copy their value into new ones.

Background and the full external cross-reference: Company Memory
`reports/schemas/atlas-cross-reference/report.md`. Current state and next actions:
[SITREP.md](SITREP.md).

## Stack

No framework, no build, no test suite, no CI. `composer.json` declares autoload only — no
`require`, and **no `require.php` constraint**, so the IFP stack standard (Laravel 13 / PHP 8.5
/ Node 24) does not apply here; the package is framework-agnostic and its consumers run PHP 8.3.
Changes are JSON edits validated by hand per the recipe above.

## Git

Standard IFP policy — see the global `CLAUDE.md`. Trunk is `master`; never commit to it
directly; every change goes via a branch and a PR.

### Reconcile — fold into the feature PR

Before a feature branch's PR is opened or merged, run `reconcile-everything` **on that branch**
so the reconcile docs ride in the same PR as the code. If asked to merge, dance, or push
un-reconciled feature work, stop and fold the reconcile in first. A standalone post-merge
reconcile is only for catching up several already-merged PRs at once.

### After the PR merges

Cutting the release tag is a separate, easily-forgotten step:

```bash
cd /Users/ingram/code/schemas && git checkout master && git pull && git tag 1.17.0 && git push origin 1.17.0
```

Then bump the constraint in `ifp/system`'s `composer.json` if the consumer needs the change.
