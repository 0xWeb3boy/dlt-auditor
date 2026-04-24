# Code-Shape Card

## Metadata

- ID: `bor-2021-12-15-bor-cryptography-e2b938562`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-domain-mismatch`

## Code Shape Summary

- The patch corrects Bor's seal-hash computation around the Jaipur fork by making the signed header encoding fork-aware. The provided evidence shows that the pre-fix Bor seal hash omitted BaseFee in the relevant post-EIP-1559 path, and the fix propagates fork config into SealHash and ecrecover so signer recovery uses the updated encoding. Root cause: A fork-unaware canonicalization bug in the Bor seal-hash path caused post-fork signer hashing to omit the BaseFee field that Jaipur-era rules expected.

## Search Motifs

- signed hash omits chain id, domain tag, nonce, signer scope, or payload type
- RPC signer accepts ambiguous raw bytes or transaction fields without explicit user-visible context
- verification recovers an address from a partially bound message and treats it as authorized

## Typical Asymmetry

- Attacker-controlled data crosses untrusted signed payload to verifier or signer boundary and reaches signer recovery, authorization, or replay-protection decision before the missing property is enforced.

## Patch Pattern

- Make the canonical signature-domain encoding fork-aware and thread the active chain configuration through all seal-hash and signer-recovery call sites.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Signature findings need evidence that the omitted field is security-relevant and not bound by another mandatory envelope or transport context.
