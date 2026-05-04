# Root-Cause Card

## Metadata

- ID: `snarkos-2020-08-15-snarkos-transaction-processing-8b5ad567b`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-authentication`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `authentication`

## Violated Invariant

- Invariant: Record decoding, decryption, and raw-record APIs must cross an authentication gate before parameter parsing or dispatch.

## Trust Boundary

- Boundary: `remote-rpc-client->protected-node-api`

## Attack Surface

- Entrypoint type: `rpc-handler`
- Sensitive sink: record decode/decrypt or raw record access
- Attacker capability: reach the JSON-RPC endpoint; submit parameters to record-related methods without credentials.
- Preconditions: record RPC methods are exposed to the caller; record decoding/decryption output is sensitive or operator-scoped.

## Impact Pattern

- Primary impact: unauthorized record RPC access.
- Secondary impact: possible record data disclosure.
- Severity guide: `medium` for `privileged-disclosure` when the affected path is reachable from untrusted peers or RPC callers.

## Short Reusable Lesson

- Record decoding, decryption, and raw-record APIs must cross an authentication gate before parameter parsing or dispatch. The reusable lesson is to enforce the property at the boundary where untrusted data first becomes trusted state, and to keep the fix narrow enough that compensating controls remain visible during review.

## Evidence Anchor

- Raw finding summary: The evidence supports a likely security fix for missing authentication on snarkOS record RPC endpoints. The strongest grounded change is the addition of a protected decode_record wrapper that calls validate_auth(meta) before processing parameters, together with evidence that record handling such as decrypt_record was removed from the public RpcFunctions implementation area. The full endpoint list and exploitability details are not proven by the supplied hunks. 1. In `rpc/src/rpc_impl_protected.rs`, the patch replaces `/// Wrap authentication around 'create_account'` with `/// Wrap authentication around 'decode_record'`. 2. In `rpc/src/rpc_impl.rs`, the patch removes `// Record handling`. 3. 
