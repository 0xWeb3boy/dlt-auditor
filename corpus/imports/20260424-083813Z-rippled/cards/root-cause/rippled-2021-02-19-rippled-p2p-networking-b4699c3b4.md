# Root-Cause Card

## Metadata

- ID: `rippled-2021-02-19-rippled-p2p-networking-b4699c3b4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-misbehavior-detection-gap`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: Untrusted protocol input must satisfy structural, semantic, and state-dependent invariants before it is admitted to ledger, consensus, storage, or trust-management state.

## Trust Boundary

- Boundary: remote peer message -> local node networking/resource manager

## Attack Surface

- Entrypoint type: p2p-message-handler
- Sensitive sink: peer session state, fetch scheduling, handshake slots, or local resource accounting

## Impact Pattern

- Primary impact: validator-misbehavior-detection
- Secondary impact: Primarily node-local resource, liveness, or peer-trust impact with possible network-level amplification.

## Short Reusable Lesson

- The patch expands Byzantine validation detector coverage from UNL-only validators to all validations received by the server and adds or tightens related validation and manifest checks.
