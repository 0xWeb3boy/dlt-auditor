# Root-Cause Card

## Metadata

- ID: `stacks-core-2019-11-18-stacks-core-storage-73eb572ac2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-equivocation-detection-gap`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `canonical-consensus-context-validation`

## Violated Invariant

- Invariant: Consensus decisions must validate evidence, fork context, canonical tip monotonicity, and signer sets against the authoritative chain view before accepting results.

## Trust Boundary

- Boundary: Persisted or peer-derived chain state crosses into storage-backed validation.

## Attack Surface

- Entrypoint type: `state_database_lookup_or_update`
- Sensitive sink: canonical state database, cached validation state, or durable index

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: fork-choice-divergence

## Short Reusable Lesson

- The supported finding is a protocol-level microblock equivocation detection fix. The patch broadens conflict handling so signed microblocks that share a parent are treated as conflicting, and PoisonMicroblock deserialization accepts evidence when headers share either sequence number or parent block hash.
