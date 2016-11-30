# Loading of Adverts

- All adverts coming onto system for first time will be given advert.approval:pending and advert.status:online, thus all adverts are put online prior to them being checked and possibly removed.

- When adverts are approved, they will be set to approval:approved and the significantly_updated_date will be updated, as this is the date field the Property Spy uses to find suitable adverts.

- Adverts within the system may have the following status and approval configurations:

    - advert.status:online && approval:pending
        - advert stored in the Search Engine Database and the Backing Database
        - part of advertisers **current** portfolio
        - advert has been selected to advertise
        - content and data has not yet been checked for quality by IFP
        - **available** to the Search Engine, but unlikely to be found in targeted searches due to missing information
        - **unavailable** to the Property Spy
        - full advert **available** directly by URL
        
    - advert.status:online && approval:deferred
        - advert stored in the Search Engine Database and the Backing Database
        - part of advertisers **current** portfolio
        - advert has been selected to advertise
        - content and data is not yet complete and awaiting input from advertiser to improve it, before approval from IFP
        - **available** to the Search Engine, but unlikely to be found in targeted searches due to missing information
        - **unavailable** to the Property Spy
        - full advert **available** directly by URL
        
    - advert.status:online && approval:approved
        - advert stored in the Search Engine Database and the Backing Database
        - part of advertisers **current** portfolio
        - advert has been selected to advertise
        - content / data quality is approved (or improved) by IFP
        - **available** to the Search Engine
        - **available** to the Property Spy
        - full advert **available** directly by URL
        
    - advert.status:offline
        - advert stored in the Search Engine Database and the Backing Database
        - part of advertisers **current** portfolio
        - advert has **not** been selected to advertise
        - **unavailable** to the Search Engine
        - **unavailable** to the Property Spy
        - full advert **available** directly by URL
        
    - advert.status:archived
        - advert stored in the Search Engine Database and the Backing Database
        - part of advertisers **old** portfolio
        - **unavailable** to the Search Engine
        - **unavailable** to Property Spy
        - minimal advert **available** directly by URL
        
    - advert.status:deleted
        - advert has been deleted by the advertiser
        - advert is deleted from the Search Engine Database
        - advert is retained in the Backing Database
        
    - advert.status:deleted && approval:denied
        - advert has been denied by IFP
        - advert is deleted from the Search Engine Database
        - advert is retained in the Backing Database

The queue from which the Loader will pull the adverts will be loaded by 3 separate systems:

1. Old IFP
2. Importer
3. Checker

Each system will load the adverts with a set combination of action and advert.status fields as follows:

## 1. Adverts coming from Old IFP

The adverts will be loaded with one of four states:

### A. Adverts to Upsert as 'Online'

```json
{
  "action": "upsert",
  "advert": {
    "status": "online",
    "approval": "pending
  }
}
```

### B. Adverts to Upsert as 'Offline'

```json
{
  "action": "upsert",
  "advert": {
    "status": "offline",
    "approval": "pending"
  }
}
```

### C. Adverts to Upsert as 'Archived'

```json
{
  "action": "upsert",
  "advert": {
    "status": "archived",
    "approval": "pending"
  }
}
```

### D. Adverts to Delete

```json
{
  "action": "delete"
}
```

## 2. Adverts coming from Importer

The adverts will be loaded with one of three states:

### A. Adverts to Upsert as 'Online'

```json
{
  "action": "upsert",
  "advert": {
    "status": "online",
    "approval": "pending"
  }
}
```

### B. Adverts to Upsert as 'Offline'

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

The adverts will be loaded with one of two states:

### A. Adverts to Upsert as 'Approved'

```json
{
  "action": "upsert",
  "advert": {
    "status": "online",
    "approval": "approved"
  }
}
```

### B. Adverts to Delete that have been Denied

```json
{
  "action": "delete",
  "advert": {
    "status": "deleted",
    "approval": "denied"
  }
}
```

Note: Adverts will never come through from the Checker with the approval of 'pending' or 'deferred', as these states represents the adverts which have not yet been approved, and therefore are not ready to leave the checker system.

## Approval Funnel Trap

All new adverts come onto the system as "approval": "pending", but then later on, some may be upgraded to "approval": "approved" in the Checker. If this happens and the original system that loaded the advert then upserts the advert again, it will be with "approval": "pending". As the advert has been set to "approval": "approved", the "approval" status will not change back to "pending". Thus, the change of "approval" can be seen a one-way action during the lifetime of the advert.
