# Code-Shape Card

## Metadata

- ID: `oasis-core-2020-01-23-oasis-core-cryptography-d5cc58f88`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `insufficient-signature-verification`

## Code Shape Summary

- Short description of what the buggy code looked like: Node registration validation was centered on a single accepted descriptor signer instead of requiring proof that specific security-relevant keys embedded in the descriptor had actually signed it, and the transaction authorization check was tied to the descriptor signer rather than directly to the authorized node/entity principal.

## Search Motifs

- Motif 1: signature verification without signer-set or committee binding
- Motif 2: valid signature reused across runtime, role, or domain scope
- Motif 3: message accepted after verify but before signer authorization

## Typical Asymmetry

- What was checked in one path but missing in another: The code checked that something was signed, but did not bind the signature to the correct signer set, runtime, committee, or domain.

## Patch Pattern

- What the fix changed structurally: The fix introduces multisigned descriptor verification in the node registration path. The shown code now requires signatures from the node identity key and consensus key, accumulates the allowed signer set, rejects descriptors with unexpected signers, and authorizes the transaction based on the node or authorized entity instead of the descriptor's generic signer field.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if signer membership, runtime binding, and domain separation are enforced before the sink on every path.
