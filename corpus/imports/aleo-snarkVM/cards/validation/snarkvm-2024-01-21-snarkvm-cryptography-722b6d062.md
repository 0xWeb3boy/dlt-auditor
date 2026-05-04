# Validation Card

## Metadata

- ID: `snarkvm-2024-01-21-snarkvm-cryptography-722b6d062`
- Bug family: `resource_accounting_and_limits`
- Bug class: `resource-accounting-hardening`

## What Confirmed The Issue

- The aggregate constraint-count API changed from an unchecked sum to a checked `Result`.
- Circuit enforcement now consults an explicitly configured constraint limit.

## What Could Have Invalidated It

- All metadata is ignored and counts are recomputed from trusted circuit synthesis.
- Consensus already rejects deployments long before the limit can be approached.

## Severity Guidance

- Expected impact band: resource_limit_and_availability
- Expected severity band: medium_or_low

## False-Positive Cautions

- Constraint counts are recomputed from trusted proving keys before admission.
- Overflow or excess counts are impossible under consensus deployment size caps.
