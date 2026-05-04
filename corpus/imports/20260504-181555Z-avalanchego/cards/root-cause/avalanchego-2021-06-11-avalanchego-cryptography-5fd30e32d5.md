# Root-Cause Card

## Metadata

- ID: `avalanchego-2021-06-11-avalanchego-cryptography-5fd30e32d5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-canonicalization-mismatch`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-signature-binding`

## Violated Invariant

- Invariant: Consensus objects must be signed and verified over one canonical byte representation, with the same parent identity and signature field semantics used by construction, lookup, serialization, and verification.

## Trust Boundary

- Boundary: Local proposer block construction and consensus block verification cross from node-local staking credentials into peer-visible consensus messages.

## Attack Surface

- Entrypoint type: consensus block production and proposer block verification
- Sensitive sink: acceptance of a signed proposer block and its parent linkage

## Impact Pattern

- Primary impact: consensus-integrity, block-authentication
- Secondary impact: medium_high_integrity

## Root Cause

- The likely root cause was inconsistent use of proposer block header representations and signing key sources in the block authentication path. The evidence shows exported fields such as Signature and PrntID being replaced with internal fields signature and prntID, suggesting the bytes being signed, serialized, looked up, or validated could previously diverge.

## Short Reusable Lesson

- Signing and verification-sensitive code used inconsistent proposer block header fields and key sources. The reusable shape is a consensus object with duplicate internal/exported fields where signing, serialization, and lookup must all bind the same canonical representation.
