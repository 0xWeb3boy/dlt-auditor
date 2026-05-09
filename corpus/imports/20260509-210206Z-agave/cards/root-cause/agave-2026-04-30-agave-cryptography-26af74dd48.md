# Root-Cause Card

## Metadata

- ID: `agave-2026-04-30-agave-cryptography-26af74dd48`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-protocol-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consistent-recovered-data-validation`

## Violated Invariant

- Invariant: Data recovered through erasure or repair paths must satisfy the same protocol validity rules as directly received consensus data before ledger insertion.

## Trust Boundary

- Boundary: `erasure-recovered-shred->blockstore`

## Attack Surface

- Entrypoint type: `ledger-recovery-path`
- Sensitive sink: recovered shred acceptance and blockstore insertion
- Attacker capability: Influence shred sets used for recovery or produce data that yields recovered shreds with unexpected metadata.
- Key precondition: Recovered shreds follow a separate path that omits feature-gated data-complete flag validation.

## Impact Pattern

- Primary impact: `consensus-integrity`
- Secondary impact: `ledger-integrity`
- Severity guidance: `medium` because Recovered shreds are consensus-sensitive ledger data; inconsistent validation can matter, but no exploit, signature bypass, or state-corruption scenario was proven.

## Short Reusable Lesson

- The ledger recovery path constructs or inserts recovered shreds through a separate code path that may not apply the current protocol rule for unexpected data-complete flags.
- Structural fix: Route recovered shreds through protocol-aware recovery context and add regression coverage that feature-gated invalid recovered data shreds are discarded.
