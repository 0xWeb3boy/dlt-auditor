# Code-Shape Card

## Metadata

- ID: `snarkvm-2024-01-21-snarkvm-cryptography-722b6d062`
- Bug family: `resource_accounting_and_limits`
- Bug class: `resource-accounting-hardening`

## Code Shape Summary

- Deployment validation summed claimed constraint counts directly and circuit enforcement lacked an explicit per-circuit active limit.

## Search Motifs

- constraint_count += verifying_key.constraint_count
- claimed constraint count from deployment metadata
- global max constraints checked without local configured limit

## Typical Asymmetry

- The code accepted or derived security-sensitive state before proving the boundary property named in the record: `resource-accounting`.

## Patch Pattern

- Use checked Result-returning aggregate constraint accounting and enforce an explicit optional circuit constraint limit.

## False Match Warnings

- Constraint counts are recomputed from trusted proving keys before admission.
- Overflow or excess counts are impossible under consensus deployment size caps.
- The path is only developer tooling and cannot affect deployed programs.
