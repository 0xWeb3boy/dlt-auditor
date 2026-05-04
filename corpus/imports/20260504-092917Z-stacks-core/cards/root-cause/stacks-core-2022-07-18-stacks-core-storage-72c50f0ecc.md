# Root-Cause Card

## Metadata

- ID: `stacks-core-2022-07-18-stacks-core-storage-72c50f0ecc`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-domain-binding`
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

- Primary impact: signature-integrity
- Secondary impact: validator-integrity

## Short Reusable Lesson

- The patch changes validator block proposal signing from a constant placeholder hash toward structured proposal-data signing that also takes a multiparty contract identifier, and it threads that contract through connection configuration into the RPC path. This is security-relevant cryptographic plumbing, but the provided evidence does not establish a concrete vulnerability, exploitability, or that pre-fix signatures were accepted in a dangerous context.
