# Root-Cause Card

## Metadata

- ID: `stacks-core-2024-05-06-stacks-core-transaction-processing-81e451bf7b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-context-binding`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-input-validation`

## Violated Invariant

- Invariant: Protocol inputs must be normalized and validated in their canonical context before they influence state, signatures, or consensus outcomes.

## Trust Boundary

- Boundary: Externally supplied transaction, block proposal, or signer payload crosses into transaction validation.

## Attack Surface

- Entrypoint type: `transaction_or_block_proposal`
- Sensitive sink: transaction acceptance, block proposal evaluation, or signer coordination state

## Impact Pattern

- Primary impact: cross-context-message-processing
- Secondary impact: protocol-integrity

## Short Reusable Lesson

- The patch changes signer message handling so messages carry a reward_cycle and consumers check or unwrap that reward-cycle-scoped structure before processing payloads. The evidence supports a protocol-context binding improvement, but it does not establish an exploitable vulnerability or concrete security impact.
