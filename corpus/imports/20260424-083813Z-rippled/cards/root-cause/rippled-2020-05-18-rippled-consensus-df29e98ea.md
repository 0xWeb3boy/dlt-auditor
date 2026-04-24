# Root-Cause Card

## Metadata

- ID: `rippled-2020-05-18-rippled-consensus-df29e98ea`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-threshold-rounding`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `accounting-integrity`

## Violated Invariant

- Invariant: Ledger accounting updates must preserve balance, reserve, fee, and yield invariants across every accepted transaction shape and lifecycle transition.

## Trust Boundary

- Boundary: peer/validator consensus data -> local consensus and ledger-close machinery

## Attack Surface

- Entrypoint type: consensus-message-or-ledger-close-path
- Sensitive sink: ledger close decision, validator set decision, or consensus safety state

## Impact Pattern

- Primary impact: protocol-governance-integrity
- Secondary impact: Potentially network-wide safety or trust impact for nodes that accept the affected state or trust decision.

## Short Reusable Lesson

- The provided evidence supports a consensus-amendment threshold rounding fix. The commit message explicitly says amendment ballot counting could allow majority with slightly less than 80% support due to integer arithmetic and rounding semantics.
