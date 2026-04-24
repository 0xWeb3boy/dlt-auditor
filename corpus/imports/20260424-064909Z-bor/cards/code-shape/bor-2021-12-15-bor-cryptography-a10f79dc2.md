# Code-Shape Card

## Metadata

- ID: `bor-2021-12-15-bor-cryptography-a10f79dc2`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `insufficient-signature-coverage`

## Code Shape Summary

- This patch makes Bor seal-hash computation fork-aware and adds BaseFee to the signed header encoding at Jaipur. The provided evidence supports a consensus-integrity hardening claim: before the change, signer recovery used a seal hash that the added test describes as incorrectly omitting BaseFee after the EIP-1559-related fork. Root cause: The seal-hash path was not fork-aware, so post-fork header hashing could omit BaseFee even when the protocol expected it to matter.

## Search Motifs

- signed hash omits chain id, domain tag, nonce, signer scope, or payload type
- RPC signer accepts ambiguous raw bytes or transaction fields without explicit user-visible context
- verification recovers an address from a partially bound message and treats it as authorized

## Typical Asymmetry

- Attacker-controlled data crosses untrusted signed payload to verifier or signer boundary and reaches signer recovery, authorization, or replay-protection decision before the missing property is enforced.

## Patch Pattern

- Make consensus signature hashing fork-aware and include newly relevant header fields in the signed serialization when the active protocol version requires them.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Signature findings need evidence that the omitted field is security-relevant and not bound by another mandatory envelope or transport context.
