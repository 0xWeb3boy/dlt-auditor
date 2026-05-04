# Root-Cause Card

## Metadata

- ID: `snarkos-2020-06-19-snarkos-transaction-processing-79edbb851`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rpc-attack-surface-reduction`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `rpc-surface-minimization`

## Violated Invariant

- Invariant: RPC APIs should not expose sensitive transaction-building or record-access helpers on a public surface unless an explicit auth boundary protects them.

## Trust Boundary

- Boundary: `remote-rpc-client->node-api`

## Attack Surface

- Entrypoint type: `rpc-handler`
- Sensitive sink: transaction construction and record access RPC methods
- Attacker capability: reach the JSON-RPC service; call transaction or record helper methods.
- Preconditions: RPC service exposes the removed methods; methods are unauthenticated or not intended for public callers.

## Impact Pattern

- Primary impact: unnecessary privileged API exposure.
- Secondary impact: possible record metadata disclosure or transaction helper misuse.
- Severity guide: `low` for `access-surface-hardening` when the affected path is reachable from untrusted peers or RPC callers.

## Short Reusable Lesson

- RPC APIs should not expose sensitive transaction-building or record-access helpers on a public surface unless an explicit auth boundary protects them. The reusable lesson is to enforce the property at the boundary where untrusted data first becomes trusted state, and to keep the fix narrow enough that compensating controls remain visible during review.

## Evidence Anchor

- Raw finding summary: The patch removes several JSON-RPC methods from the exported `RpcFunctions` trait and their shown implementations from `RpcImpl`, including `createrawtransaction` and record-access methods such as `fetchrecordcommitments` and `getrawrecord`. A nearby note mentions adding password guarding, so the change may be security-motivated RPC surface reduction. However, the evidence does not establish a concrete vulnerability, exploit path, deployment exposure, or actual secret disclosure. Treat this as unclear security relevance rather than a confirmed or likely security fix. 1. In `rpc/src/rpc_impl.rs`, the patch replaces `fn create_raw_transaction(&self, transaction_input: TransactionInputs) -> Res
