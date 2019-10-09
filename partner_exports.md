# Partner Simplified Export Schema

We export an array of JSON properties according to the following JSON schema:

[Simplified Export Sale Advert JSON v1.0.0 example](https://github.com/ifp/schemas/blob/master/json/public/simplified_export_sale-advert-schema_v1.0.0.json)

The fields in the schema are as follows:

- id : our internal ID (not to be displayed)
- reference : the advertisers reference for the property (to be displayed)
- title_en : the title of the property in English
- description_en : the property description in English
- department_code : the official code of the department that the property resides in (please note that we use the old codes of 2A / 2B for Corsican properties which now has the department code of 20)
- post_code : the postcode of the property's commune
- commune_name : the name of the commune that the property resides in
- location : a brief description about the location of the property
- price_eur : integer of property price in Euros
- bathrooms : number of bathrooms, shower rooms and en-suite bathrooms (does not include separate WCs)
- bedrooms : number of bedrooms
- floor_size_m2 : habitable surface area of property in metres squared
- land_size_m2 : land size of the plot of the property
- dpe_number : the diagnostic de performance énergétique value of the property 
- ges_number : the gaz à effet de serre value of the property
- attributes : an object of arrays of tags about the property
  -- features : internal and external features of the property
  -- types : property types included within the advert (may contain multiple if property has different buildings, e.g. residential, house, barn)
  -- tags : other tags about the property (more abstract in nature - such as location, condition, usage etc.)
- images : an array of image objects composed of
  -- title : the title of the image
  -- url : url of the image
