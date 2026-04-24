# Root-Cause Card

## Metadata

- ID: `zksync-2022-09-13-zksync-transaction-processing-0bf5cd634`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `cross-domain-signature-replay`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `chain-domain-signature-binding`

## Violated Invariant

- Invariant: A signature authorizing account-control changes must be bound to the intended chain/domain and typed action so it cannot be replayed from another network or signing context.

## Trust Boundary

- Boundary: External wallet signature crosses into ChangePubKey transaction authorization and account key-control logic.

## Attack Surface

- Entrypoint type: `wallet_typed_data_signature`
- Sensitive sink: ChangePubKey signer recovery and account public-key update authorization

## Impact Pattern

- Primary impact: cross-domain replay hardening for account-control signatures
- Secondary impact: clearer signer scope and auth variant separation

## Short Reusable Lesson

- ChangePubKey Ethereum authorization moves from raw-message ECDSA toward EIP-712 typed data with an explicit chain_id domain, and the legacy SDK signing path is deprecated. The reusable shape is an account-control signature verified without sufficient domain/action binding.
