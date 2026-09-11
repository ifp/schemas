# TODO

Forward-looking only. What shipped lives in [`docs/history/`](history/) and the
[SITREP](../SITREP.md) roadmap table.

Most of what follows is a **contract decision**, not a task — the schemas here are consumed by
third parties and by our own pipeline, so "just fix it" usually means "pick a direction and cut a
version". Two items that sat on this list turned out not to be defects at all; they are now
recorded in [CLAUDE.md](../CLAUDE.md) as deliberate, and one of them would have caused a
production bug if "fixed". Check there before adding anything back.

## Decisions needed

- [ ] **`RentalSearchControllerTest` (french-property.com) needs five expected URLs updated**
  once this repo's rebuilt fixture reaches it. Verified with `php83`: the five Bunny-native images
  now render `/agency_123456/...` instead of `/cloudinary-2020-11/agency_testimmo/...`. The five
  legacy images are unchanged. Blocked on a release and a `composer update ifp/schemas` there.

- [ ] **`ifp/system` has its own Cloudinary-shaped test data.**
  `AdvertHelper::setImageTitlesOnAdvertData` builds an `$example_image` with `cloudinary_account`,
  `public_id` and `version`, and replaces the fixture's images with it — so rebuilding our
  fixtures does not reach it. Legitimate as legacy coverage, but it should say so.

## Tooling

- [ ] **`bin/validate.py` pins `jsonschema~=4.25` because it uses `RefResolver`,** deprecated since
  4.18 and slated for removal. Port to the `referencing` library before a major bump forces it.
- [ ] **Add a fixture that exercises `floor_plans` and `virtual_tours`.** Both are `[]` in
  `upsert_sale_advert.json`, which is why the stage mismatch above went unnoticed. Blocked on
  settling that question first.
- [ ] **Consider validating the downstream response fixtures.**
  `elasticsearch_single_sale_advert_result.json` and `search_engine_single_sale_advert_result.json`
  wrap an advert in `hits.hits[]._source` and `data` and are maintained by hand, so they can drift
  from the schema without anything noticing.
