# Root-Cause Card

## Metadata

- ID: `geth-arb-2015-01-13-go-ethereum-transaction-processing-82beaabf6a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-rule-mismatch`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus-rule-consistency`

## Violated Invariant

- Invariant: All nodes must apply the same edge-case consensus rules for gas charging, error propagation, uncle eligibility, and state commitment so the same block produces the same validity decision and state root.

## Trust Boundary

- Boundary: untrusted block or transaction data -> consensus execution rules

## Attack Surface

- Entrypoint type: block execution or transaction state-transition path
- Sensitive sink: consensus validity decision and state-root calculation

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: state-integrity
- Severity guide: medium

## Short Reusable Lesson

- Consensus-sensitive edge cases used inconsistent local error propagation or boundary constants, so equivalent nodes could disagree about whether execution should continue or which relatives are valid. Scope nested errors locally, align boundary constants with the protocol rule, and add regression coverage for the consensus edge case.
