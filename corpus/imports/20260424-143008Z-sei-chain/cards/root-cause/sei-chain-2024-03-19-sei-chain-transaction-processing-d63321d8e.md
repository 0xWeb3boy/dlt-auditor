# Root-Cause Card

## Metadata

- ID: `sei-chain-2024-03-19-sei-chain-transaction-processing-d63321d8e`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `weak-signature-message-binding`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signed-message-binding`

## Violated Invariant

- Invariant: Signature recovery for account association must be bound to the exact message bytes and domain the signer intended.

## Trust Boundary

- Boundary: externally supplied association transaction -> account identity binding

## Attack Surface

- Entrypoint type: transaction-preprocess-or-ante-handler
- Sensitive sink: deriving or storing account association from recovered signer

## Impact Pattern

- Primary impact: authentication-integrity
- Secondary impact: protocol-state-integrity

## Short Reusable Lesson

- Carry the signed message in the transaction data and bind signature recovery to the hash of those bytes instead of using a constant placeholder hash. Keeps account association proofs tied to the message being verified. Avoids accepting signatures against a fixed empty hash for association recovery.
