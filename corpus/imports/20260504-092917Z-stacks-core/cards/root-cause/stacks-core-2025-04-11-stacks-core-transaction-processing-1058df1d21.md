# Root-Cause Card

## Metadata

- ID: `stacks-core-2025-04-11-stacks-core-transaction-processing-1058df1d21`
- Bug family: `resource_accounting_and_limits`
- Bug class: `resource-limit-validation-inconsistency`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-bounds-and-error-containment`

## Violated Invariant

- Invariant: Untrusted inputs and execution paths must be bounded and must fail closed without panics, unmetered work, or inconsistent accounting.

## Trust Boundary

- Boundary: Externally supplied transaction, block proposal, or signer payload crosses into transaction validation.

## Attack Surface

- Entrypoint type: `transaction_or_block_proposal`
- Sensitive sink: transaction acceptance, block proposal evaluation, or signer coordination state

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: denial-of-service

## Short Reusable Lesson

- Commit 1058df1d21 changes block proposal replay validation so ChainError::BlockCostExceeded is inspected not only for TransactionResult::ProcessingError, but also for TransactionResult::Skipped and TransactionResult::Problematic. The evidence supports a likely validation bypass in a replay-sensitive resource-control path, but does not prove exploitability, consensus impact, or a broader transaction-processing flaw.
