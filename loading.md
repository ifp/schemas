Notes:

- all adverts coming onto system for first time will be approval:pending
- when adverts are approved, they will go approval:approved and the significantly_updated_date will be updated, which the property spy uses as the date
- everything goes online at Loading, then will be dealt with after to see whether it is pulled down

# Loading states

The queue from which the Loader will pull the adverts will be loaded by 3 separate systems:

1. Old IFP
2. Advert Import
3. Checker

Each system will load the adverts with a set combination of action and advert.status fields. This document details these and how they will be processed by the Loader.

## 1. Adverts coming from Old IFP

## 2. Adverts coming from Advert Import

The adverts will only have three pertinent states:

### A. Adverts to Insert or Update (online)

```json
{
  "action": "upsert",
  "advert": {
    "status": "online",
    "approval": "pending"
  }
}
```

### B. Adverts to Insert or Update (offline)

```json
{
  "action": "upsert",
  "advert": {
    "status": "offline",
    "approval": "pending"
  }
}
```

### C. Adverts to Delete

```json
{
  "action": "delete"
}
```

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
