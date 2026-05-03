# Code-Shape Card

## Metadata

- ID: `firedancer-2026-01-09-firedancer-cryptography-1ad8a534f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `merkle-root-validation-hardening`

## Code Shape Summary

- Repair/FEC logic accepted new shreds without binding them tightly enough to a previously confirmed merkle root for that set.

## Search Motifs

- Motif 1: confirmed merkle root tracked in repair state
- Motif 2: reject incoming shred when root conflicts with confirmed root
- Motif 3: verify chained roots before resuming incomplete FEC

## Typical Asymmetry

- Peers can provide repaired data opportunistically, but the validator must keep one authoritative root per repair context.

## Patch Pattern

- Persist the confirmed root, reject conflicting shreds, and require every resumed validation step to chain from the already confirmed root.

## False Match Warnings

- No concrete attacker flow or exploit sequence is shown.
- No evidence of signature forgery or cryptographic primitive failure is provided.
