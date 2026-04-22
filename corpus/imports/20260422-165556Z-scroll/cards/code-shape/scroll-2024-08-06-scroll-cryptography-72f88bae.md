# Code-Shape Card

## Metadata

- ID: `scroll-2024-08-06-scroll-cryptography-72f88bae`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-preimage-mismatch`

## Code Shape Summary

- Short description of what the buggy code looked like: The evidence supports a targeted compatibility fix in coordinator authentication: the legacy Curie public-key recovery path was changed to hash a dedicated legacy identity payload instead of the current Message object. That shows a signer-recovery mismatch, but the provided diff does not establish that this caused acceptance of forged logins, replay, or an authorization bypass.

## Search Motifs

- Motif 1: signature recovery hashes a different struct than the one used for signing
- Motif 2: legacy compatibility branch rebuilds an identity payload separately from the canonical message type
- Motif 3: authentication code mixes current and legacy hash functions for the same public-key recovery decision

## Typical Asymmetry

- What was checked in one path but missing in another: One path or representation enforced the canonical rule, identity, or compatibility gate while another parallel path, legacy branch, or helper-derived value reached the sink without the same binding.

## Patch Pattern

- What the fix changed structurally: Reconstruct the legacy identity payload explicitly in the compatibility branch and recover the signer from that canonical legacy preimage instead of the current message object.

## False Match Warnings

- Warning 1: If the legacy and current payloads serialize identically or the compatibility path is disabled, the practical risk drops sharply.
- Warning 2: Message-shape cleanup alone is not enough; the important question is whether signer recovery and the prover signer bind to the same bytes.
- Warning 3: The evidence supports a compatibility hardening fix, not a demonstrated forged-login exploit.
