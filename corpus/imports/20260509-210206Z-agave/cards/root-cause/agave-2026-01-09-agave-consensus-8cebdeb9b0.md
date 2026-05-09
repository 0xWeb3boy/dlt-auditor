# Root-Cause Card

## Metadata

- ID: `agave-2026-01-09-agave-consensus-8cebdeb9b0`
- Bug family: `authz_and_role_gates`
- Bug class: `improper-vote-authorization-filtering`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `current-epoch-vote-authorization`

## Violated Invariant

- Invariant: Consensus vote buffering must verify that a vote is signed by the current authorized voter for the vote account before mutating latest-vote state.

## Trust Boundary

- Boundary: `validator-or-peer-vote-packet->consensus-vote-storage`

## Attack Surface

- Entrypoint type: `consensus-vote-ingestion`
- Sensitive sink: latest vote state update in vote storage
- Attacker capability: Submit or relay vote packets for a staked vote account.
- Key precondition: Vote storage checks stake presence but not the epoch authorized-voter mapping before state mutation.

## Impact Pattern

- Primary impact: `consensus-integrity`
- Secondary impact: `vote-state-integrity`
- Severity guidance: `high` because The confirmed missing authorization check sits before consensus-facing latest-vote mutation; downstream impact is not fully proven, so high is a conservative upper band rather than critical.

## Short Reusable Lesson

- A vote packet ingestion layer verifies that a vote account has stake but mutates latest-vote state without first matching the signer against the current epoch authorized-voter map.
- Structural fix: Filter votes at the vote-storage ingestion boundary by current epoch authorized-voter mapping before updating latest-vote state.
