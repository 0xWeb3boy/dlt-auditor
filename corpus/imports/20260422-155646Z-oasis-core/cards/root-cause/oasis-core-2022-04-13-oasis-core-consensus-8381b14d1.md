# Root-Cause Card

## Metadata

- ID: `oasis-core-2022-04-13-oasis-core-consensus-8381b14d1`
- Bug family: `resource_accounting_and_limits`
- Bug class: `insufficient-resource-limits`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Invariant: Txpool admission should preserve any sender identity returned by CheckTx so sender-aware scheduling or admission rules can be applied consistently, and any downstream queue rejection should be returned to the submitter instead of being left as a log-only condition. The provided evidence does not establish a stronger invariant than local txpool resource control, and the hash-based fallback shows sender-based handling is not uniformly available across runtimes.

## Trust Boundary

- Boundary: `user->mempool`

## Attack Surface

- Entrypoint type: `transaction-handler`
- Sensitive sink: `transaction admission and scheduling state`

## Impact Pattern

- Primary impact: `denial-of-service`
- Secondary impact: `resource-exhaustion`

## Short Reusable Lesson

- Txpool admission should preserve any sender identity returned by CheckTx so sender-aware scheduling or admission rules can be applied consistently, and any downstream queue rejection should be returned to the submitter instead of being left as a log-only condition. The provided evidence does not establish a stronger invariant than local txpool resource control, and the hash-based fallback shows sender-based handling is not uniformly available across runtimes. In this pattern, the txpool's checked-transaction state was missing sender metadata that later sender-aware queue logic could use, and the post-CheckTx scheduling stage did not retain enough index information to surface queue-admission failure back to the correct caller. That is a local admission-path consistency gap. The provided evidence does not by itself prove a security vulnerability beyond that. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
