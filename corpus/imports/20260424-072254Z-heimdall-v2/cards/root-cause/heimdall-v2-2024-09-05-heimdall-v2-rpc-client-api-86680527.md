# Root-Cause Card

## Metadata

- ID: `heimdall-v2-2024-09-05-heimdall-v2-rpc-client-api-86680527`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-consensus-height-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: consensus-height binding for aggregated vote-extension payloads.

## Violated Invariant

- Invariant: votes or attestations counted during consensus must be bound to the exact height or round expected by that consensus step.

## Trust Boundary

- Boundary: validator-supplied vote-extension bytes crossing into local vote tallying.

## Attack Surface

- Entrypoint type: ABCI finalize/preblock vote-extension aggregation.
- Sensitive sink: side-transaction approval tally and consensus-derived state transition input.

## Impact Pattern

- Primary impact: consensus-integrity hardening.
- Secondary impact: replay and stale-attestation resistance.

## Short Reusable Lesson

- Aggregators should receive authoritative consensus context and reject payloads whose embedded context does not match before counting them. Leaving explicit validation-gap comments near height, round, or hash checks is a strong audit smell.
