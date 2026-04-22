# Root-Cause Card

## Metadata

- ID: `base-2026-03-07-base-transaction-processing-3e0b436b4`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-signature-validation`

## Violated Invariant

- Invariant: The proof blob sent toward verifier initialization should use the shared TEE proof format and reject structurally invalid signatures, including unsupported ECDSA recovery-byte (`v`) values, before forwarding.

## Trust Boundary

- Boundary: `transaction, batch, or proof input->execution or derivation pipeline`

## Attack Surface

- Entrypoint type: `transaction-or-batch-validation`
- Sensitive sink: `acceptance of a proof, signature, or derived state transition`

## Impact Pattern

- Primary impact: `malformed-input-acceptance`
- Secondary impact: `none`

## Short Reusable Lesson

- The proof blob sent toward verifier initialization should use the shared TEE proof format and reject structurally invalid signatures, including unsupported ECDSA recovery-byte (`v`) values, before forwarding. The visible issue is inconsistent ownership of proof encoding and validation in a sensitive path: proposer-local code performed ad hoc assembly with length checking, while stricter structural validation was not shown there. The patch centralizes that logic in a shared encoder. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
