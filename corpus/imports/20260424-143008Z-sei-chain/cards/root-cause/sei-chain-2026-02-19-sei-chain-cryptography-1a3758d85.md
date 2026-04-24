# Root-Cause Card

## Metadata

- ID: `sei-chain-2026-02-19-sei-chain-cryptography-1a3758d85`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-proposal-validation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `proposal-role-and-range-validation`

## Violated Invariant

- Invariant: Consensus proposals must prove proposer role, committee lane range, signatures, and hash-linked certificate consistency at construction or verification boundaries.

## Trust Boundary

- Boundary: leader/proposer supplied proposal -> consensus proposal acceptance

## Attack Surface

- Entrypoint type: proposal-constructor-or-verifier
- Sensitive sink: accepting FullProposal or LaneQC data for consensus processing

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: protocol-state-integrity

## Short Reusable Lesson

- Move consensus proposal invariants into explicit construction and verification checks instead of relying on surrounding code to supply valid leader keys, committee lanes, signatures, or hash-linked data. Consensus proposal acceptance is security-sensitive. Non-leader proposal construction is now rejected in the shown code.
