# Root-Cause Card

## Metadata

- ID: `rippled-2026-03-21-rippled-core-logic-311719dae`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `invariant-state-overwrite`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-and-state-invariant-validation`

## Violated Invariant

- Invariant: Untrusted protocol input must satisfy structural, semantic, and state-dependent invariants before it is admitted to ledger, consensus, storage, or trust-management state.

## Trust Boundary

- Boundary: protocol-controlled input -> core ledger/application invariant

## Attack Surface

- Entrypoint type: state-transition-or-core-validation-path
- Sensitive sink: ledger invariant, protocol state, or node safety decision

## Impact Pattern

- Primary impact: ledger-integrity, consensus-safety
- Secondary impact: Potentially network-wide safety or trust impact for nodes that accept the affected state or trust decision.

## Short Reusable Lesson

- Likely security fix in rippled transaction invariant enforcement. The evidence supports a consensus-sensitive invariant bug where boolean violation state could use last-entry overwrite semantics instead of latching any observed violation.
