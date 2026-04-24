# Code-Shape Card

## Metadata

- ID: `zksync-2019-09-03-zksync-cryptography-136c8d4e5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-signature-message-binding`

## Code Shape Summary

- The patch reconstructs serialized transaction bits in the circuit and verifies they match allocated signature-message data for transfer-to-new. The reusable pattern is a signature verifier constrained over witness-supplied bytes without proving those bytes equal the transaction being executed.

## Search Motifs

- verify_signature_message_construction introduced near circuit signature checks
- serialized transaction bits compared to allocated signed message
- transfer_to_new or account-creation transfer signature message rebuilt in-circuit

## Typical Asymmetry

- The dangerous value originates outside the trusted state model, while the vulnerable code treats it as already canonical, authenticated, or uniquely identified.

## Patch Pattern

- Reconstruct the canonical signed message from constrained transaction fields and add equality checks against the bytes used by signature verification.

## False Match Warnings

- Storage formatting or unrelated cleanup hunks should not support this case.
- If signed bytes are already constrained by a shared helper on all paths, the patch may only deduplicate checks.
- Presence of signature verification alone is not enough; the important signal is binding to operation fields.
