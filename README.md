# IFP Schemas

This schema represents the Advert object used within the IFP systems. Currently it only supports Sale Adverts.

## Public Schemas:

- [Public Sale Advert JSON Schema v1.0.0](https://github.com/ifp/schemas/blob/master/json/public_sale-advert-schema_v1.0.0.json) - please use this schema when sending us sale adverts.

### Public Document Examples:

- [Public Sale Advert JSON v1.0.0 example](https://github.com/ifp/schemas/blob/master/json/examples/public_sale-advert-schema_v1.0.0-example.json)
- [Public Sale Advert JSON v1.0.0 notes](https://github.com/ifp/schemas/blob/master/json/examples/public_sale-advert-schema_v1.0.0-notes.json) - This document provides notes about the use for each field. There are two top-level objects:
    - advert: Information about the advert, i.e. the advertising details.
    - property: Information about the actual property being advertised.
    
There is some logic to the required field of the property.geo.user_data which is required to follow in order ensure the advert is validated: It is necessary to supply one of the following combinations as a minimum:
- post_code
- commune_name + department_name
- commune_name + department_code

- [Public Sale Advert JSON v1.0.0 list of enums available](https://github.com/ifp/schemas/blob/master/json/examples/public_sale-advert-schema_v1.0.0-example.json) - see this for the full list of the enums in the schema that can be used for the lookup values in their respective keys.

### JSON resources:

- [Tutorials](https://www.google.co.uk/search?q=json%20tutorial)
- [JSON Validator](http://www.jsonschemavalidator.net/) - paste our public schema into the left box, then paste your JSON document into the right to validate that it adheres to the schema.

-----

## Internal Schemas:

- [Internal Sale Advert JSON Schema v1.0.0](https://github.com/ifp/schemas/blob/master/json/internal_sale-advert-schema_v1.0.0.json)

-----

### Versioning (loosely) follows:

- [SchemaVer](https://github.com/ifp/iglu/wiki/SchemaVer)
- [Self-Describing JSON Schema](https://github.com/ifp/iglu/wiki/Self-describing-JSON-Schemas)
- [Self-Describing JSONs](https://github.com/ifp/iglu/wiki/Self-describing-JSONs)
