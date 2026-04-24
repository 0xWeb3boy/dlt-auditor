# Code-Shape Card

## Metadata

- ID: `bor-2020-12-08-bor-transaction-processing-ed0670cb1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `replay-protection`

## Code Shape Summary

- The evidence supports a security-hardening change in the ABI binding transaction-signing helpers. Before this patch, the convenience path shown here used types.HomesteadSigner{}; the patch adds chain-ID-aware helper entry points and updates some callers to use them. The code supports a replay-protection rationale, but not a claim of a demonstrated exploit or full removal of legacy signing paths. Root cause: The helper layer for contract transaction creation was centered on a legacy Homestead-based signer, so convenience-generated signing options did not carry an explicit chain-specific replay-protection domain through those APIs.

## Search Motifs

- signed hash omits chain id, domain tag, nonce, signer scope, or payload type
- RPC signer accepts ambiguous raw bytes or transaction fields without explicit user-visible context
- verification recovers an address from a partially bound message and treats it as authorized

## Typical Asymmetry

- Attacker-controlled data crosses untrusted signed payload to verifier or signer boundary and reaches signer recovery, authorization, or replay-protection decision before the missing property is enforced.

## Patch Pattern

- Add chain-ID-aware signer constructors, thread chainID through higher-level transaction-option helpers, and update representative callers to use the chain-aware path.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Signature findings need evidence that the omitted field is security-relevant and not bound by another mandatory envelope or transport context.
