# Code-Shape Card

## Metadata

- ID: `sei-chain-2026-01-12-sei-chain-cryptography-cbd47b343`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `traffic-analysis-hardening`

## Code Shape Summary

- The supplied evidence supports a security-hardening interpretation around encrypted transport metadata leakage, specifically message length analysis. It does not establish a concrete vulnerability, exploit path, authentication failure, nonce-reuse bug, malformed transaction crash, or plaintext disclosure.

## Search Motifs

- Motif 1: buffering occurs outside secret connection
- Motif 2: ciphertext frame size follows application write size
- Motif 3: evil secret connection test detects message length pattern

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Move buffering into the encrypted connection so frame emission follows transport framing rules rather than raw writes.

## False Match Warnings

- The protocol does not attempt to hide message sizes.
- Transport framing already pads or batches writes below this layer.
