# Root-Cause Card

## Metadata

- ID: `firedancer-2026-04-25-firedancer-cryptography-384b6f788`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cryptographic-transcript-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-specified-transcript-construction`

## Violated Invariant

- Invariant: Cryptographic proof verification must hash exactly the transcript shape mandated by the protocol and bound the message size it accepts.

## Trust Boundary

- Boundary: Peer- or state-supplied proof bytes crossing into a BLS proof-of-possession verifier.

## Attack Surface

- Entrypoint type: cryptographic proof verifier
- Sensitive sink: proof acceptance against a public key

## Impact Pattern

- Primary impact: signature validation risk
- Secondary impact: cryptographic correctness

## Short Reusable Lesson

- The verifier built its hash input differently from the documented protocol transcript and lacked an explicit bound on the message size it hashed.
