# Code-Shape Card

## Metadata

- ID: `rippled-2016-04-21-rippled-rpc-client-api-b5dbd7942`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `failed-handshake-resource-accounting`

## Code Shape Summary

- The patch fixes overlay handoff rejection paths for malformed or unverifiable HELLO messages. Reusable shape: check for accounting-integrity was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: rpc-or-client-handler missing exact accounting-integrity check before node configuration, downloaded trust material, or externally visible service behavior
- Motif 2: security-sensitive path reaches node configuration, downloaded trust material, or externally visible service behavior before rejecting malformed, stale, or unauthorized input
- Motif 3: Convert failed handshake validation paths from plain early returns into terminal rejection paths that release connection accounting, prevent handoff ownership transfer, send an explicit error response, and close persistence.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into node configuration, downloaded trust material, or externally visible service behavior unless the accounting-integrity gate runs before the state-changing branch.

## Patch Pattern

- Convert failed handshake validation paths from plain early returns into terminal rejection paths that release connection accounting, prevent handoff ownership transfer, send an explicit error response, and close persistence.

## False Match Warnings

- No proof that an attacker could exhaust slots or IP counters in practice.
- No evidence of a successful authentication, cryptographic, or replay bypass.
