# Root-Cause Card

## Metadata

- ID: `rippled-2025-11-16-rippled-core-logic-248d267f2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `numeric-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `numeric-bounds`

## Violated Invariant

- Invariant: Numeric protocol values must be range checked and rounded deterministically before they affect ledger accounting or eligibility decisions.

## Trust Boundary

- Boundary: protocol-controlled input -> core ledger/application invariant

## Attack Surface

- Entrypoint type: state-transition-or-core-validation-path
- Sensitive sink: ledger invariant, protocol state, or node safety decision

## Impact Pattern

- Primary impact: state-integrity, consensus-integrity
- Secondary impact: Potentially network-wide safety or trust impact for nodes that accept the affected state or trust decision.

## Short Reusable Lesson

- The evidence supports a vault numeric-validation change, not an established vulnerability fix.
