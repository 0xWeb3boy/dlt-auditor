# Code-Shape Card

## Metadata

- ID: `bor-2021-04-06-bor-transaction-processing-706683ea7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `replay-protection-gating`

## Code Shape Summary

- The evidence supports an API-correctness fix for eth_chainId, not a confirmed vulnerability fix. Before the patch, two different implementations existed with different behavior: one returned the configured chain ID unconditionally as *hexutil.Big, while another gated on IsEIP155(...) but returned hexutil.Uint64. The patch removes the duplicate path and makes internal/ethapi the canonical implementation with EIP-155 gating and bigint return semantics. Root cause: Duplicated eth_chainId implementations had diverged in behavior. One path enforced the EIP-155 activation check but narrowed the value type; the other preserved bigint width but skipped the activation check entirely.

## Search Motifs

- signed hash omits chain id, domain tag, nonce, signer scope, or payload type
- RPC signer accepts ambiguous raw bytes or transaction fields without explicit user-visible context
- verification recovers an address from a partially bound message and treats it as authorized

## Typical Asymmetry

- Attacker-controlled data crosses external RPC/user signing request to local signer boundary and reaches signature creation or signed transaction acceptance before the missing property is enforced.

## Patch Pattern

- Remove inconsistent duplicate API implementations and consolidate behavior in one canonical path that enforces the same state gate and value representation.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Signature findings need evidence that the omitted field is security-relevant and not bound by another mandatory envelope or transport context.
