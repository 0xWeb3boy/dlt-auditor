# Root-Cause Card

## Metadata

- ID: `bor-2023-07-04-bor-storage-0f9d7d61c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input validation and invariant enforcement`

## Violated Invariant

- Invariant: Persisted or peer-supplied state must be verified against its expected hash, path, or schema before being trusted by consensus or sync logic.

## Trust Boundary

- Boundary: persisted or peer-supplied state data to trusted local database boundary

## Attack Surface

- Entrypoint type: state import, trie/database read, or sync persistence path
- Sensitive sink: state commitment, canonical database write, or integrity decision

## Impact Pattern

- Primary impact: availability
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- Pending conditional transactions were not being revalidated against current state during txpool maintenance, and ValidateKnownAccounts assumed the storage trie existed in one validation branch instead of treating absence as an ordinary validation failure.
