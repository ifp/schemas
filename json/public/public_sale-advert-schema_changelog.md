# Public Sale Advert Schema Changelog

### Fix (2026-08-26)

- Remove `agency_microsite` from `advert.required` in v1.0.0 and v1.1.0. It was listed as
  required but never defined in `advert.properties`, and with `additionalProperties: false`
  this made the schema unsatisfiable — no feed (including our own published example) could
  validate. Fixed in place: the versions were impossible to satisfy, so no valid consumer
  feed relied on the broken behaviour.

### v1.1.0 (2016-10-12)

- Change of {property.floor_plans} from array of strings, to an array of objects
- Change of {property.floor_virtual_tours} from array of strings, to an array of objects

### v1.0.0 (2016-09-01)

Initial Release
