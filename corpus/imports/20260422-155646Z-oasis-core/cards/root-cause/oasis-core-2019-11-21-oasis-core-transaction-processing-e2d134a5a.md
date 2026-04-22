# Root-Cause Card

## Metadata

- ID: `oasis-core-2019-11-21-oasis-core-transaction-processing-e2d134a5a`
- Bug family: `resource_accounting_and_limits`
- Bug class: `missing-gas-accounting`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `gas-accounting`

## Violated Invariant

- Invariant: Registry transactions that mutate on-chain state should apply the configured gas charges before continuing, and the node-registration charging path should remain consistent with the stated fee-payer model for entity-signed versus prepaid node-signed registrations.

## Trust Boundary

- Boundary: `user->mempool`

## Attack Surface

- Entrypoint type: `transaction-handler`
- Sensitive sink: `state-mutating transaction execution without full fee charge`

## Impact Pattern

- Primary impact: `denial-of-service`
- Secondary impact: `fee-bypass`

## Short Reusable Lesson

- Registry transactions that mutate on-chain state should apply the configured gas charges before continuing, and the node-registration charging path should remain consistent with the stated fee-payer model for entity-signed versus prepaid node-signed registrations. In this pattern, some registry transaction handlers did not perform the now-shown explicit per-operation gas charge before continuing with stateful processing. The evidence supports inconsistent or absent handler-level metering, not a signature or replay-validation defect. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
