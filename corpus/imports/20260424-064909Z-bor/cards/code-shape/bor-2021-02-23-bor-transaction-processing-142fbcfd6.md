# Code-Shape Card

## Metadata

- ID: `bor-2021-02-23-bor-transaction-processing-142fbcfd6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-replay-protection-check`

## Code Shape Summary

- The patch hardens the RPC transaction submission path by rejecting non-EIP-155-signed transactions unless the operator explicitly enables an override. The evidence supports a missing replay-protection check on this RPC boundary before the change, but it does not prove a broader protocol or consensus flaw. Root cause: The RPC submission boundary did not enforce replay protection by default. In the provided pre-patch snippet, unprotected transactions could pass the visible fee-cap checks and reach SendTx without a shown EIP-155 protection check.

## Search Motifs

- signed hash omits chain id, domain tag, nonce, signer scope, or payload type
- RPC signer accepts ambiguous raw bytes or transaction fields without explicit user-visible context
- verification recovers an address from a partially bound message and treats it as authorized

## Typical Asymmetry

- Attacker-controlled data crosses external RPC/user signing request to local signer boundary and reaches signature creation or signed transaction acceptance before the missing property is enforced.

## Patch Pattern

- Add an explicit security check at the external submission boundary, then plumb a narrowly scoped configuration override for deployments that intentionally need legacy behavior.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Signature findings need evidence that the omitted field is security-relevant and not bound by another mandatory envelope or transport context.
