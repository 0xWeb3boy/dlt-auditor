# Root-Cause Card

## Metadata

- ID: `stacks-core-2024-01-19-stacks-core-cryptography-62e698825c`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signer-request-validation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-domain-and-signer-binding`

## Violated Invariant

- Invariant: Every signed protocol message must be verified against the exact signer set, message domain, reward cycle, and payload hash that authorize the downstream action.

## Trust Boundary

- Boundary: Untrusted signed bytes or public-key material crosses into cryptographic verification.

## Attack Surface

- Entrypoint type: `signed_message_verification`
- Sensitive sink: signature verification result or authorized signer decision

## Impact Pattern

- Primary impact: invalid-signing-request-rejection
- Secondary impact: unauthorized-message-acceptance

## Short Reusable Lesson

- The patch appears to add signer-side validation and rejection reporting around block signing flow, but the provided evidence does not establish a concrete vulnerability or exploit path. The strongest grounded changes are that `SignatureShareRequest` handling now calls `validate_signature_share_request()` and drops invalid requests, and miner block proposals with invalid signature hashes now produce a `BlockRejection` with `RejectCode::InvalidSignatureHash`.
