# Root-Cause Card

## Metadata

- ID: `bor-2025-10-01-bor-storage-83ab606c4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `network peer authenticity and protocol state validation`

## Violated Invariant

- Invariant: Persisted or peer-supplied state must be verified against its expected hash, path, or schema before being trusted by consensus or sync logic.

## Trust Boundary

- Boundary: remote peer to node networking boundary

## Attack Surface

- Entrypoint type: inbound p2p message, handshake, or sync response handler
- Sensitive sink: peer table mutation, sync scheduling, or message acceptance

## Impact Pattern

- Primary impact: correctness-or-hardening
- Secondary impact: low severity conditions

## Short Reusable Lesson

- Missing validation of peer-controlled witness pagination fields in receiveWitnessPage. The code used page.Page and page.TotalPages to drive local witness-page accounting without enforcing basic consistency constraints.
