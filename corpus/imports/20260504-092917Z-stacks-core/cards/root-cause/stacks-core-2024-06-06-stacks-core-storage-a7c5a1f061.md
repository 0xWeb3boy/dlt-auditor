# Root-Cause Card

## Metadata

- ID: `stacks-core-2024-06-06-stacks-core-storage-a7c5a1f061`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-signature-verification`
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

- Primary impact: network-message-integrity
- Secondary impact: unauthorized-block-propagation

## Short Reusable Lesson

- The patch is likely a security fix in the P2P Nakamoto block receipt and relay paths. The provided evidence shows that pushed-block validation previously could finish after sortition/PoX checks, while unsolicited block handling had an explicit signer-check unimplemented validation placeholder. The patch adds reward-cycle and reward-set lookup to these paths and extends the validation call site with the burnchain, sortdb, and chainstate context needed for that check.
