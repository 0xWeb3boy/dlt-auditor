# Root-Cause Card

## Metadata

- ID: `fuel-core-2024-03-09-fuel-core-storage-a31f64be15`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `txpool-blacklist-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `policy-gating`

## Violated Invariant

- Every transaction-admission path must apply configured deny policies to all referenced spendable resources before the transaction enters local pool or gossip state.

## Trust Boundary

- Boundary: `user-transaction->mempool-policy`
- Entrypoint type: `transaction-handler`
- Sensitive sink: `txpool insertion and propagation eligibility`

## Attack Surface

- Submit a transaction referencing a UTXO or resource that local policy intends to block.
- Reach a node txpool through RPC or p2p transaction submission.

## Exploit Preconditions

- The node operator has configured blacklisted UTXO identifiers.
- The txpool path checks syntactic validity but did not enforce the blacklist for coin inputs.

## Impact Pattern

- Primary impact: `policy-bypass`
- Secondary impact: `mempool-pollution`
- Blast radius: `node-local`
- Severity guess: `medium`

## Short Reusable Lesson

- Admission policy must be enforced at the shared boundary, not only in optional callers or operator tooling.
