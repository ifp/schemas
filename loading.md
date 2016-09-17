# Loading of Adverts

- All adverts coming onto system for first time will be given advert.approval:pending, yet they will have the advert.status:online, thus all adverts are put online prior to them being checked and possibly removed.
- When adverts are approved, they will go approval:approved and the significantly_updated_date will be updated, which the Property Spy uses as the date to find suitable adverts.
- Adverts in the system have the following statuses:
    - advert.status:online && approval:approved
        - part of advertisers live portfolio
        - content and data is approved / improved by IFP
        - in full circulation on the Search Engine and available to Property Spy
    - advert.status:online && approval:deferred -> in full circulation, but not available to Property Spy
    - advert.status:online && approval:pending -> in full circulation, but not available to Property Spy
    - advert.status:offline -> unable to find in searches, but minimal advert can be access directly by URL
    - advert.status:archived -> unable to find in searches, but minimal advert can be access directly by URL

The queue from which the Loader will pull the adverts will be loaded by 3 separate systems:

1. Old IFP
2. Advert Import
3. Checker

Each system will load the adverts with a set combination of action and advert.status fields. This document details these and how they will be processed by the Loader.

## 1. Adverts coming from Old IFP

The adverts will only have four pertinent states:

### A. Adverts to Insert or Update as 'Online'

```json
{
  "action": "upsert",
  "advert": {
    "status": "online"
  }
}
```

### B. Adverts to Insert or Update as 'Offline'

```json
{
  "action": "upsert",
  "advert": {
    "status": "offline"
  }
}
```

### C. Adverts to Insert or Update as 'Archived'

```json
{
  "action": "upsert",
  "advert": {
    "status": "archived"
  }
}
```

### D. Adverts to Delete

```json
{
  "action": "delete"
}
```

## 2. Adverts coming from Advert Import

The adverts will only have three pertinent states:

### A. Adverts to Insert or Update as 'Online'

```json
{
  "action": "upsert",
  "advert": {
    "status": "online",
    "approval": "pending"
  }
}
```

### B. Adverts to Insert or Update as 'Offline'

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

## 3. Adverts coming from Checker

The adverts will only have three pertinent states:

### A. Adverts to Insert or Update as 'Approved'

```json
{
  "action": "upsert",
  "advert": {
    "status": "online",
    "approval": "approved"
  }
}
```

### B. Adverts to Insert or Update as 'Deferred'

```json
{
  "action": "upsert",
  "advert": {
    "status": "online",
    "approval": "deferred"
  }
}
```

### C. Adverts to Delete

```json
{
  "action": "delete",
  "advert": {
    "status": "deleted",
    "approval": "denied"
  }
}
```

Notes: Adverts will never come through from the Checker with the approval of 'pending', as this state represents the adverts which have not yet been checked.
