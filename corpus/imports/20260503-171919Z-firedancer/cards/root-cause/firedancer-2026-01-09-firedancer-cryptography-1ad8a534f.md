# Root-Cause Card

## Metadata

- ID: `firedancer-2026-01-09-firedancer-cryptography-1ad8a534f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `merkle-root-validation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `confirmed-root-consistency-checking`

## Violated Invariant

- Invariant: Repair logic must not combine or continue validating data shreds once a conflicting merkle root is observed for the same FEC context.

## Trust Boundary

- Boundary: Peer-supplied repair shreds crossing into repaired-FEC validation state.

## Attack Surface

- Entrypoint type: repair shred ingestion
- Sensitive sink: confirmed-root state and repaired FEC completion

## Impact Pattern

- Primary impact: consensus integrity
- Secondary impact: data integrity

## Short Reusable Lesson

- Repair/FEC logic accepted new shreds without binding them tightly enough to a previously confirmed merkle root for that set.
