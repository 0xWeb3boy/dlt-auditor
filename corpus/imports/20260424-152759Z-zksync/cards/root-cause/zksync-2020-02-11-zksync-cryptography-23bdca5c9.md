# Root-Cause Card

## Metadata

- ID: `zksync-2020-02-11-zksync-cryptography-23bdca5c9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `nonce-binding-in-circuit`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `nonce-state-binding`

## Violated Invariant

- Invariant: A transaction nonce exposed in witness data, public data, or authorization material must be constrained equal to the account nonce consumed by the state transition.

## Trust Boundary

- Boundary: Transaction witness/public-data fields cross into circuit constraints for account key-change execution.

## Attack Surface

- Entrypoint type: `zk_circuit_transaction_witness`
- Sensitive sink: ChangePubKey circuit constraints and emitted public data

## Impact Pattern

- Primary impact: replay/order integrity hardening
- Secondary impact: account key-change authorization consistency

## Short Reusable Lesson

- The patch carries the ChangePubKey nonce through witness data, operation arguments, and pubdata, then constrains it equal to the current account nonce. The reusable shape is a replay/order field present in transaction semantics but absent or unconstrained in proof/public-data plumbing.
