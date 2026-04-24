# Root-Cause Card

## Metadata

- ID: `heimdall-v2-2024-06-24-heimdall-v2-rpc-client-api-316e7e65`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-id-reuse-guard`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: explicit state-existence check for validator ID uniqueness

## Violated Invariant

- Invariant: a registration path must reject identifiers already bound in canonical state; key presence must not be inferred from getter error semantics.

## Trust Boundary

- Boundary: externally submitted validator join message crossing into staking keeper state.

## Attack Surface

- Entrypoint type: state-changing staking message handler.
- Sensitive sink: validator ID to signer mapping and validator registration state.

## Impact Pattern

- Primary impact: validator-registration state integrity.
- Secondary impact: weakened identity reuse and signer-binding guarantees.

## Short Reusable Lesson

- For security-sensitive identity namespaces, separate `exists` checks from `get` operations. A getter can fail for absence, corruption, decoding, or backend errors; a uniqueness guard should use explicit key presence and reject reuse before mutating state.
