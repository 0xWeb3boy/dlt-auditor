# Code-Shape Card

## Metadata

- ID: `bor-2018-09-25-bor-cryptography-d3441ebb5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signer-trust-boundary-hardening`

## Code Shape Summary

- The supplied evidence supports a security-hardening change in the Clef signer API, not a demonstrated exploit fix. The grounded changes are fail-closed handling of transaction-validation warnings, removal of the externally exposed EcRecover helper, and stricter password handling in new-account creation. Root cause: The signer API was too permissive at the trust boundary: validator warnings were not enforced as blocking conditions by default, the remote API exposed an extra helper operation, and account-creation password input handling was weaker than the patched version.

## Search Motifs

- signed hash omits chain id, domain tag, nonce, signer scope, or payload type
- RPC signer accepts ambiguous raw bytes or transaction fields without explicit user-visible context
- verification recovers an address from a partially bound message and treats it as authorized

## Typical Asymmetry

- Attacker-controlled data crosses untrusted signed payload to verifier or signer boundary and reaches signer recovery, authorization, or replay-protection decision before the missing property is enforced.

## Patch Pattern

- Harden a signer trust boundary by failing closed on validator warnings, reducing exposed remote API surface, and tightening validation around sensitive account-creation inputs.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Signature findings need evidence that the omitted field is security-relevant and not bound by another mandatory envelope or transport context.
