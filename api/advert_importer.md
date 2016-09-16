# API for adverts outgoing from the Advert Importer

The adverts put onto the message queue by the Advert Importer will only have three pertinent states:

## 1. Adverts to Insert or Update

### State

- action: upsert
- advert.status: online | offline

### Outcome when processed by the Loader

- Search engine database: upsert
    - advert.status: online | offline
- Backing database: upsert

## 2. Adverts to mark as Deleted

### State

- action: delete

### Outcome when processed by the Loader

- Search engine database: upsert
    - advert.status: delete
- Backing database: upsert
