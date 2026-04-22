# Root-Cause Card

## Metadata

- ID: `base-2024-11-06-base-transaction-processing-9200d03dc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `replay-protection-state-inconsistency`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-coordinate-consistency`

## Violated Invariant

- Invariant: Legacy transaction signature fields should be represented consistently during decode and re-encoding: protection state and parity-derived signature data should not describe contradictory transaction semantics. Deposit transactions should also decode through one structurally checked RLP path.

## Trust Boundary

- Boundary: `transaction, batch, or proof input->execution or derivation pipeline`

## Attack Surface

- Entrypoint type: `transaction-or-batch-validation`
- Sensitive sink: `security-sensitive execution or state transition`

## Impact Pattern

- Primary impact: `transaction-validation-inconsistency`
- Secondary impact: `parser-hardening`

## Short Reusable Lesson

- Legacy transaction signature fields should be represented consistently during decode and re-encoding: protection state and parity-derived signature data should not describe contradictory transaction semantics. Deposit transactions should also decode through one structurally checked RLP path. The root cause shown by the provided material is an internal representation problem: replay/protection-related legacy transaction semantics were split across separate fields and a later reconstruction step, allowing inconsistent combinations to exist in memory. A secondary issue was duplicated deposit decode logic instead of a single canonical RLP decode entrypoint. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
