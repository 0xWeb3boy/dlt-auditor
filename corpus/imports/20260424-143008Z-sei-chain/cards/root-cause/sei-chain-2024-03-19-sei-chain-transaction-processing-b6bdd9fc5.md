# Root-Cause Card

## Metadata

- ID: `sei-chain-2024-03-19-sei-chain-transaction-processing-b6bdd9fc5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-message-binding`
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

- Primary impact: authorization
- Secondary impact: signature-verification

## Short Reusable Lesson

- Carry the message used for signature recovery through transaction encoding and hash that message during preprocessing instead of using a constant placeholder hash. Avoids recovering AssociateTx addresses over a hard-coded empty hash. Aligns the tested recovery path with an Ethereum-prefixed signed message. May improve signature-message binding for EVM association.
