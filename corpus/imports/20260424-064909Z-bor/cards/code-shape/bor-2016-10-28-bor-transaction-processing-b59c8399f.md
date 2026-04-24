# Code-Shape Card

## Metadata

- ID: `bor-2016-10-28-bor-transaction-processing-b59c8399f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `message-signing-domain-separation`

## Code Shape Summary

- The provided evidence supports a security hardening change in the RPC signing path: eth_sign was changed to sign a prefixed-and-hashed message instead of a raw caller-provided digest, and the codebase now separates raw signing from Ethereum-formatted signing. The evidence does not support stronger claims about transaction replay handling, nonce validation, or a demonstrated private-key extraction exploit. Root cause: The RPC/account signing boundary was too close to the low-level raw signing primitive, so user-supplied signing requests were not clearly forced into the Ethereum message-signing domain before signature generation.

## Search Motifs

- signed hash omits chain id, domain tag, nonce, signer scope, or payload type
- RPC signer accepts ambiguous raw bytes or transaction fields without explicit user-visible context
- verification recovers an address from a partially bound message and treats it as authorized

## Typical Asymmetry

- Attacker-controlled data crosses external RPC/user signing request to local signer boundary and reaches signature creation or signed transaction acceptance before the missing property is enforced.

## Patch Pattern

- Separate low-level cryptographic primitives from RPC-facing signing APIs, and enforce message-domain separation by prefixing and hashing user-supplied messages before signing.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Signature findings need evidence that the omitted field is security-relevant and not bound by another mandatory envelope or transport context.
