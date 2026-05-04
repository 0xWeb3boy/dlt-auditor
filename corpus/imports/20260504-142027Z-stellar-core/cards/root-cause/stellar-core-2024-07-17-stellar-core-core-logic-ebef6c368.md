# Root-Cause Card

## Metadata

- ID: `stellar-core-2024-07-17-stellar-core-core-logic-ebef6c368`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `hash-collision-dos-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `collision-resistant-bounded-hash-structure-construction`

## Violated Invariant

- Invariant: Collision-sensitive structures built from attacker-influenced keys should use keyed hashing and bounded retry behavior.

## Trust Boundary

- Boundary: ledger-key-or-query-inputs -> hash-filter-construction-and-lookup

## Attack Surface

- Entrypoint type: data-structure-construction
- Sensitive sink: BinaryFuseFilter population and lookup CPU work
- Attacker capability: Influence keys inserted into or queried against collision-sensitive filters.
- Main precondition: The filter uses predictable non-keyed hash mixing for placement.

## Impact Pattern

- Primary impact: denial-of-service
- Secondary impact: resource-exhaustion, algorithmic-complexity-hardening
- Severity guess: medium because Keyed hashing and retry caps reduce algorithmic DoS risk, but the finding does not prove a concrete production exploit path.

## Short Reusable Lesson

- Hash-based performance assumptions become security assumptions when inputs can be chosen; use keyed hashing and bounded retries for collision-sensitive paths.
