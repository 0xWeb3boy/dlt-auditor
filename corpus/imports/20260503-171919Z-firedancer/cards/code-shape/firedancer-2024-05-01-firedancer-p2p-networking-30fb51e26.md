# Code-Shape Card

## Metadata

- ID: `firedancer-2024-05-01-firedancer-p2p-networking-30fb51e26`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-input-validation`

## Code Shape Summary

- Handshake logic consumed Retry-related connection IDs before proving their encoded lengths matched protocol limits.

## Search Motifs

- Motif 1: connection ID length check added before handshake state update
- Motif 2: protocol parser distinguishes actual wire length from allowed maximum
- Motif 3: Retry-token or CID fields accepted without explicit size gate

## Typical Asymmetry

- The peer controls wire-format lengths, but the state machine assumes those lengths are already specification-compliant.

## Patch Pattern

- Add explicit per-field length checks and reject malformed Retry packets before any stateful processing.

## False Match Warnings

- No advisory, CVE, exploit, test case, or commit body explains a concrete security impact.
- No evidence shows resource exhaustion, connection hijacking, authentication bypass, or memory corruption.
