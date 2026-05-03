# Root-Cause Card

## Metadata

- ID: `movement-2024-10-04-movement-p2p-networking-cc8857336`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-sequence-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `committed-state-bounded-future-sequence-window`

## Violated Invariant

- Invariant: The upper bound for future transaction sequence numbers must be anchored to committed account state plus a fixed tolerance; attacker-influenced local or default sequence state must not widen that future window.

## Trust Boundary

- Boundary: Network or client-submitted transactions entering the node transaction admission path.

## Attack Surface

- Entrypoint type: transaction gossip/RPC admission into mempool validation
- Sensitive sink: too-new transaction acceptance and resource allocation in transaction admission

## Impact Pattern

- Primary impact: Availability hardening against too-new transaction queue inflation.
- Secondary impact: More predictable transaction admission semantics across nodes.

## Short Reusable Lesson

- The too-new sequence-number ceiling used the same max(local used sequence, committed sequence) base as the stale lower bound. The fix separates those sources: local state can raise the stale lower bound, but the future upper bound stays committed_sequence_number plus tolerance. Use local used-sequence state for stale lower-bound checks only, compute the too-new ceiling from committed state plus tolerance, and log the computed bounds for diagnosis.
