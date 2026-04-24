# Root-Cause Card

## Metadata

- ID: `sei-chain-2024-05-09-sei-chain-transaction-processing-b36bfe41b`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `replay-or-signature-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `replay-domain-validation`

## Violated Invariant

- Invariant: Transaction admission must reject signatures whose chain or replay domain does not match the configured execution domain.

## Trust Boundary

- Boundary: externally submitted EVM transaction -> ante signature verification

## Attack Surface

- Entrypoint type: transaction-ante-handler
- Sensitive sink: accepting transaction for execution under local chain state

## Impact Pattern

- Primary impact: request-forgery-or-replay
- Secondary impact: authorization-or-identity-integrity

## Short Reusable Lesson

- Add explicit validation of a replay-domain field in the transaction admission path, while preserving legacy transaction compatibility and failing closed on mismatches. Chain ID is part of the EVM transaction replay/signature domain. Rejecting mismatched chain IDs earlier reduces ambiguity in transaction admission behavior.
