# Root-Cause Card

## Metadata

- ID: `agave-2024-09-11-agave-transaction-processing-f0a77e94bf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `durable-nonce-consumption`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `nonce-consumption-on-rollback`

## Violated Invariant

- Invariant: A replay-protection nonce that has entered fee-paying transaction handling must remain consumed even if execution rolls back or only fees are charged.

## Trust Boundary

- Boundary: `user-transaction->banking-stage`

## Attack Surface

- Entrypoint type: `transaction-handler`
- Sensitive sink: durable nonce account rollback state and transaction age fallback
- Attacker capability: Submit durable-nonce transactions that fail after fee charging or enter a fee-only path.
- Key precondition: The implementation advances or checks nonce state before a later rollback path constructs account state.

## Impact Pattern

- Primary impact: `replay-protection`
- Secondary impact: `state-integrity`
- Severity guidance: `medium` because Nonce reuse can undermine replay protection for affected durable-nonce transactions, but the source evidence did not prove successful production replay, fund theft, or consensus divergence.

## Short Reusable Lesson

- A durable-nonce path checks transaction age and charges fees, then uses rollback account construction that can accidentally restore pre-advance nonce data for failed or fee-only transactions.
- Structural fix: Move nonce advancement into the fallback/fee-paying path and ensure rollback copies the already-advanced nonce data when reconstructing accounts.
