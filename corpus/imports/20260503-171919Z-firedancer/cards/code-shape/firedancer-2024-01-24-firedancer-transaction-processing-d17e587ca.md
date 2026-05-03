# Code-Shape Card

## Metadata

- ID: `firedancer-2024-01-24-firedancer-transaction-processing-d17e587ca`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `signing-key-isolation-hardening`

## Code Shape Summary

- The change reroutes protocol and shred signing through a keyguard client so key-holding behavior is removed from direct protocol handlers.

## Search Motifs

- Motif 1: direct signing replaced with keyguard client
- Motif 2: topology adds signer input link
- Motif 3: private-key operations moved out of protocol worker

## Typical Asymmetry

- Network-facing code wants a signature, but key ownership should stay confined to a smaller trusted component.

## Patch Pattern

- Insert a keyguard-mediated client boundary, validate the required topology wiring, and keep raw signing out of protocol-facing code.

## False Match Warnings

- No proof that private keys were exposed before the patch.
- No proof that arbitrary payload signing or signature forgery was possible before the patch.
