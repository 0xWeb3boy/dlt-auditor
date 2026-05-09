# Root-Cause Card

## Metadata

- ID: `solana-2021-09-02-solana-validator-ops-afb87a386a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-key-reuse`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `stake-accountability-invariant`

## Violated Invariant

- Protocol input must satisfy stake accountability invariant before it can reach stake delegation, withdrawal, reward accounting, vote authority, or validator weight.

## Trust Boundary

- Boundary: signed stake/vote instruction to stake-weighted accounting state

## Attack Surface

- Entrypoint type: stake or vote program instruction
- Sensitive sink: stake delegation, withdrawal, reward accounting, vote authority, or validator weight

## Root Cause

The CLI create-vote-account path allowed a security-sensitive withdrawal authority to be omitted and silently defaulted it to the validator identity key, weakening key separation by default.

## Impact Pattern

- Primary impact: key-separation, authority-misconfiguration
- Expected band: defense_in_depth_or_input_hardening
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch hardens Solana CLI vote account creation by making `authorized_withdrawer` a required concrete pubkey instead of an optional value that defaulted to the validator identity. It also adds an unsafe-configuration override flag and, in the shown evidence, rejects the authorized withdrawer being identical to the vote account pubkey unless that override is used.
