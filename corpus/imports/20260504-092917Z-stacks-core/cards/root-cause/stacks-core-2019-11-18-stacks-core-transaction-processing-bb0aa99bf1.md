# Root-Cause Card

## Metadata

- ID: `stacks-core-2019-11-18-stacks-core-transaction-processing-bb0aa99bf1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-validation-hardening`
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

- Primary impact: transaction-integrity
- Secondary impact: authorization-validation

## Short Reusable Lesson

- The patch changes transaction postcondition asset lookups from origin_account.principal to account.principal for STX, fungible-token, and non-fungible-token checks, and adds a guard that rejects sponsored token-transfer transactions before token-transfer processing. This is plausibly security-relevant validation logic, but the supplied evidence does not prove exploitability, consensus impact, loss of funds, or that the previous behavior was reachable in an unsafe way.
