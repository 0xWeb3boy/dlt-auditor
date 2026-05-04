# Root-Cause Card

## Metadata

- ID: `avalanchego-2025-12-09-avalanchego-storage-e7bd4fb988`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `range-proof-boundary-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `requested-boundary-proof-binding`

## Violated Invariant

- Invariant: Range proofs over authenticated state must prove the caller-requested boundaries, including absent boundary keys, not only the first and last returned keys.

## Trust Boundary

- Boundary: A state proof request crosses from a client/query API into authenticated Merkle or trie proof generation.

## Attack Surface

- Entrypoint type: range proof generation for trie/Merkle state
- Sensitive sink: proof material returned to clients for verification of key-value range completeness

## Impact Pattern

- Primary impact: proof-verification-integrity, absence-proof-correctness
- Secondary impact: medium_high_integrity

## Root Cause

- The range proof code conflated yielded trie keys with requested range boundary keys. When a requested boundary key was absent, proving only the nearest yielded key did not provide proof material for the gap between the requested bound and the returned data. ## Walkthrough 1. A caller requests a range proof with optional lower and upper bounds. 2.

## Short Reusable Lesson

- Range proof boundaries were changed to bind requested start/end keys instead of only yielded keys. The reusable shape is proof generation where absence at range edges must be proven explicitly, especially when no exact boundary key exists.
