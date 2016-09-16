# Loading states

The queue from which the Loader will pull the adverts will be loaded by 3 separate systems:

A. Old IFP
B. Advert Import
C. Checker

Each system will load the adverts with a set combination of action and advert.status fields. This document details these and how they will be processed by the Loader.

## A. Adverts coming from the Advert Importer

The adverts put onto the message queue by the Advert Importer will only have three pertinent states:

### 1. Adverts to Insert or Update (online)

- action: upsert
- advert.status: online

### 2. Adverts to Insert or Update (offline)

- action: upsert
- advert.status: offline

## 3. Adverts to Delete

- action: delete

## B. API for adverts

### Outcome when processed by the Loader

- Search engine database: upsert
- Backing database: upsert

## B. Adverts to mark as Deleted

### State

- action: delete

### Outcome when processed by the Loader

- Search engine database: upsert
    - advert.status: delete
- Backing database: upsert
    - advert.status: delete
