# Loading of Adverts

- All adverts coming onto system for first time will be given advert.status:active & advert.approval:pending; thus all adverts are put online prior to them being checked and possibly removed.

- When adverts are approved, they will be set to advert.approval:approved and the significantly_updated_date will be updated, as this is the date field the Property Spy uses to find suitable adverts.

### action => advert.status

- upsert => active (default)
    - advert is currently advertised
    - advert stored in the Search Engine Database and the Backing Database
- archive => archived; 
    - advert is no longer advertised
    - advert stored in the Search Engine Database and the Backing Database
- delete => deleted; 
    - advert is soft deleted from system (deleted from Search Engine Database, but retained in Backing Database)
- purge
    - advert is hard deleted from system (deleted from both Search Engine Database and Backing Database). There is no associated advert.status, as the advert will be physically deleted, meaning there can be no adverts with this status

### advert.approval

- pending (default); 
    - advert has not yet been reviewed by IFP
    - **available** to the Search Engine (but possibly unlikely to be found in targeted searches if missing information)
    - **unavailable** to the Property Spy
    - full advert **available** directly by URL
    - enquiries can be made to the advert
- approved;
    - content / data quality is approved (or improved) by IFP
    - **available** to the Search Engine
    - **available** to the Property Spy
    - full advert **available** directly by URL
    - enquiries can be made to the advert
- conflict; 
    - advert has been changed by IFP in Checker, but then said changes have been overwritten by changes (that are different to the original information supplied) by the advertiser
    - content and data has been approved by IFP, but since updated by the advertiser
    - **available** to the Search Engine
    - **available** to the Property Spy (but as previously approved, it has probably already been sent out)
    - full advert **available** directly by URL
    - enquiries can be made to the advert
- to_review; 
    - advert has been approved, but the data has been changed by advertiser and may need to be reviewed by IFP
    - content and data has been approved by IFP, but since updated by the advertiser
    - **available** to the Search Engine
    - **available** to the Property Spy (but as previously approved, it has probably already been sent out)
    - full advert **available** directly by URL
    - enquiries can be made to the advert
- denied; 
    - advert is not suitable and has been denied advertising by IFP
    - **unavailable** to the Search Engine
    - **unavailable** to the Property Spy
    - full advert **unavailable** directly by URL
    - if the advert is upserted with a different approval, then it will be ignored and the status not changed
    - if the advert needs to be "un-denied", then it will have to be purged from the system and re-uploaded

### advert.valid (boolean)

Each advert loaded will be validated to ensure it meets the minimum required amount of data. If it passes validation, then this flag will be set to true and it will be included in searches by default. If it is not valid, then the advert will still be loaded, but with this flag set to false, in which case it can only be found in searches that specifically include invalid adverts.

## Loading Process

The queue from which the Loader will pull the adverts will be loaded by 3 separate systems:

1. Old IFP
2. Importer
3. Checker

Each system will load the adverts with a set combination of action and advert.status fields as follows:

### 1. Adverts coming from Old IFP

The adverts will be loaded with one of four states:

#### A. Adverts to load as 'Active'

```json
{
  "action": "upsert"
}
```

This will load the adverts with advert.status=active.

#### B. Adverts to load as 'Archived'

```json
{
  "action": "archive"
}
```

This will load the adverts with advert.status=archived.

#### C. Adverts to delete

```json
{
  "action": "delete"
}
```

This will delete the advert document from the Search Engine Database and update the Backing Database record with advert.status=deleted.

#### D. Adverts to purge

```json
{
  "action": "purge"
}
```

This will delete both the document from the Search Engine Database and the record from the Backing Database.

### 2. Adverts coming from Importer

The adverts will be loaded with one of three states:

#### A. Adverts to load as 'Active'

```json
{
  "action": "upsert"
}
```

This will load the adverts with advert.status=active.

#### B. Adverts to load as 'Archived'

```json
{
  "action": "archive"
}
```

This will load the adverts with advert.status=archived.

### 3. Adverts coming from Checker

The adverts will be loaded with one of two states:

#### A. Adverts to load as 'Approved'

```json
{
  "action": "upsert",
  "advert": {
    "approval": "approved"
  }
}
```

#### B. Adverts to load as 'Denied'

```json
{
  "action": "upsert",
  "advert": {
    "approval": "denied"
  }
}
```

Note: Adverts will never come through from the Checker with the approval of 'pending', as this state represents the adverts which have not yet been approved, and therefore are not ready to leave the checker system.

## Approval Funnel Trap

All new adverts come onto the system as "approval": "pending", but then later on, some may be upgraded to "approval": "approved" in the Checker. If this happens and the original system that loaded the advert then upserts the advert again, it will be with "approval": "pending". As the advert has been set to "approval": "approved", the "approval" status will not change back to "pending". Thus, the change of "approval" can be seen a one-way action during the lifetime of the advert.

## Denied Adverts

If an advert has been denied in the Checker, then any time it is re-uploaded via the Importer or the Exporter, it will not be upserted into ElasticSearch. If there is a legitimate need to re-upload the advert, then it will need to be purged prior to re-uploading via the originating system.
