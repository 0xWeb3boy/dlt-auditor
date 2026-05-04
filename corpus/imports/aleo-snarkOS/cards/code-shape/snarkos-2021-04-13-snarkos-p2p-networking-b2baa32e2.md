# Code-Shape Card

## Metadata

- ID: `snarkos-2021-04-13-snarkos-p2p-networking-b2baa32e2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-block-sync-state-hardening`

## Code Shape Summary

- The handler computes whether a Sync payload is expected but ignores the boolean and forwards the payload into consensus sync handling anyway.

## Search Motifs

- expecting_sync_blocks result ignored
- consensus.received_sync called after unused validation boolean
- outstanding sync counters not cleared before new sync source

## Typical Asymmetry

- The code has a validation, authentication, sizing, correlation, or peer-enforcement concept nearby, but the specific inbound path either does not call it, ignores its result, signs too little data, or maps failure to a log/return instead of a state-changing rejection.

## Patch Pattern

- Use the expectation check as a control-flow guard and reset stale sync counters before registering a new mutually exclusive sync attempt.

## False Match Warnings

- If consensus.received_sync independently validates peer expectation, impact is reduced
- Purely local sync tests are not a peer boundary
- No issue if duplicate/unexpected payloads are idempotent
