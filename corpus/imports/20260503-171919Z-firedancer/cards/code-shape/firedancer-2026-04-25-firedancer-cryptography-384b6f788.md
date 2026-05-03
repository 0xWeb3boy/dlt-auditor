# Code-Shape Card

## Metadata

- ID: `firedancer-2026-04-25-firedancer-cryptography-384b6f788`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cryptographic-transcript-validation`

## Code Shape Summary

- The verifier built its hash input differently from the documented protocol transcript and lacked an explicit bound on the message size it hashed.

## Search Motifs

- Motif 1: H(msg || public_key, DST) alignment change in verifier
- Motif 2: proof verifier transcript shape adjusted to match upstream spec
- Motif 3: verifier adds explicit current-message-size cap

## Typical Asymmetry

- Protocol designers define one transcript, but implementation shortcuts can silently verify a different statement.

## Patch Pattern

- Construct the transcript exactly as specified, then bound the message size before hashing and verification.

## False Match Warnings

- No exploit path through the vote program is shown.
- No evidence demonstrates prior acceptance of an attacker-controlled invalid proof.
