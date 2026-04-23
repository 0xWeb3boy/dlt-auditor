# Code-Shape Card

## Metadata

- ID: `go-ethereum-2016-10-28-go-ethereum-transaction-processing-b59c8399f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-domain-separation`

## Code Shape Summary

- A wallet-facing signing path used raw hash-signing semantics, and the fix separates external message signing from the low-level primitive by prefixing and hashing messages in an explicit domain first.

## Search Motifs

- Motif 1: `eth_sign` or equivalent API changes from raw hash signing to prefixed message signing.
- Motif 2: Comments warn that raw signing on adversary-chosen input is unsafe.
- Motif 3: A dedicated domain-specific signing helper is introduced next to the low-level sign primitive.

## Typical Asymmetry

- The attacker controls message bytes at the API boundary, but the defender controls the key and must prevent those bytes from escaping their intended signing domain.

## Patch Pattern

- Prefix and hash user messages at the RPC boundary, keep raw signing as a lower-level helper, and document that the helper must not be exposed to adversary-chosen input.

## False Match Warnings

- Documentation-only changes are not enough without an accompanying externally reachable signing-semantics change.
- Do not claim replay or theft if the evidence only proves stronger message-signing scoping.
