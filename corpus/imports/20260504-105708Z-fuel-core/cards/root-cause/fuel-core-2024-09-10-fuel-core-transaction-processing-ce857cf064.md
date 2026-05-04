# Root-Cause Card

## Metadata

- ID: `fuel-core-2024-09-10-fuel-core-transaction-processing-ce857cf064`
- Bug family: `resource_accounting_and_limits`
- Bug class: `resource-limit-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Every user-facing simulation and execution path must reject or skip transactions whose declared maximum gas exceeds the active block budget.

## Trust Boundary

- Boundary: `user-transaction->executor-resource-budget`
- Entrypoint type: `transaction-handler`
- Sensitive sink: `block gas budget and dry-run execution resources`

## Attack Surface

- Submit transactions with max_gas values larger than remaining block gas or dry-run limits.
- Call GraphQL dry_run with crafted transaction batches.

## Exploit Preconditions

- Dry-run or executor loops process transactions before checking max_gas against active consensus parameters.
- The resource budget is shared across transactions or requests.

## Impact Pattern

- Primary impact: `denial-of-service`
- Secondary impact: `resource-exhaustion`
- Blast radius: `node-local`
- Severity guess: `medium`

## Short Reusable Lesson

- Resource limits must be enforced before expensive work in every equivalent execution entrypoint, including simulation APIs.
