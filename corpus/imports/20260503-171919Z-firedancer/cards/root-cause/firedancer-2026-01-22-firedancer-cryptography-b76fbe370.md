# Root-Cause Card

## Metadata

- ID: `firedancer-2026-01-22-firedancer-cryptography-b76fbe370`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-poh-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `pre-execution-tick-verification`

## Violated Invariant

- Invariant: Replay must verify PoH tick and hash constraints before a completed block is emitted for normal execution.

## Trust Boundary

- Boundary: Ledger and snapshot PoH metadata crossing into block completion.

## Attack Surface

- Entrypoint type: replay scheduler / block completion
- Sensitive sink: block-end task emission and bank death/continuation decisions

## Impact Pattern

- Primary impact: consensus integrity
- Secondary impact: none

## Short Reusable Lesson

- Block completion treated PoH verification as an implicit later assumption instead of a required gate before normal replay progression.
