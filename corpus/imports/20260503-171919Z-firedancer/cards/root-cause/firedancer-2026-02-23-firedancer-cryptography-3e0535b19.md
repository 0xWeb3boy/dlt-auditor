# Root-Cause Card

## Metadata

- ID: `firedancer-2026-02-23-firedancer-cryptography-3e0535b19`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `malformed-block-resource-exhaustion`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `saturating-progress-accounting`

## Violated Invariant

- Invariant: Replay progress counters must saturate or reject malformed tick/hash counts before arithmetic wraparound can hide excess work.

## Trust Boundary

- Boundary: Malformed block progress and tick/hash counts crossing into replay scheduler accounting.

## Attack Surface

- Entrypoint type: replay scheduler progress update
- Sensitive sink: tick/hash accumulation and block validation progress

## Impact Pattern

- Primary impact: denial of service
- Secondary impact: resource exhaustion

## Short Reusable Lesson

- Replay accounting used ordinary unsigned accumulation in a path where malformed block input could make the counter wrap and mask excessive work.
