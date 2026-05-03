# Code-Shape Card

## Metadata

- ID: `firedancer-2024-07-15-firedancer-cryptography-22a0ab7f8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `quic-packet-validation-hardening`

## Code Shape Summary

- Protocol helpers consumed packet-number and packet-length state before proving the wire-format sizes and backing transport lengths were coherent.

## Search Motifs

- Motif 1: packet-number reconstruction adjusted near decode path
- Motif 2: IPv4 or UDP length check added before packet use
- Motif 3: wire-format size gate added near crypto or AEAD processing

## Typical Asymmetry

- The peer controls packet framing, but the crypto path assumes framing metadata has already been normalized.

## Patch Pattern

- Tighten packet-number handling and add explicit transport-length validation before decode and crypto state updates.

## False Match Warnings

- No advisory, CVE, exploit, or security-labeled commit message is provided.
- No supplied hunk proves out-of-bounds read, write, packet forgery, nonce reuse, or plaintext exposure.
