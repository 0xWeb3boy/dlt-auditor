# Code-Shape Card

## Metadata

- ID: `rippled-2018-10-08-rippled-rpc-client-api-7fe1d4b9c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-site-redirect-retry-hardening`

## Code Shape Summary

- The patch changes rippled's ValidatorSite fetch path to represent fetch targets as Resource objects, centralize URL parsing and http/https validation, honor redirect-oriented resource state, use per-site refresh intervals, reset redirect counts per cycle, and add explicit... Reusable shape: check for trust-root-and-freshness-validation was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: rpc-or-client-handler missing exact trust-root-and-freshness-validation check before node configuration, downloaded trust material, or externally visible service behavior
- Motif 2: security-sensitive path reaches node configuration, downloaded trust material, or externally visible service behavior before rejecting malformed, stale, or unauthorized input
- Motif 3: Model validator-site fetch targets as validated Resource objects and keep redirect/retry state explicit and bounded in the scheduler.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into node configuration, downloaded trust material, or externally visible service behavior unless the trust-root-and-freshness-validation gate runs before the state-changing branch.

## Patch Pattern

- Model validator-site fetch targets as validated Resource objects and keep redirect/retry state explicit and bounded in the scheduler.

## False Match Warnings

- No evidence shows an exploitable redirect vulnerability before the patch.
- No evidence shows attacker control over validator-site redirects in normal deployments.
