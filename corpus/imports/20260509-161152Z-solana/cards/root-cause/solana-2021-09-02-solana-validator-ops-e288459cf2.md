# Root-Cause Card

## Metadata

- ID: `solana-2021-09-02-solana-validator-ops-e288459cf2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-authority-default`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization-and-privilege-check`

## Violated Invariant

- Protocol input must satisfy authorization and privilege check before it can reach stake delegation, withdrawal, reward accounting, vote authority, or validator weight.

## Trust Boundary

- Boundary: signed stake/vote instruction to stake-weighted accounting state

## Attack Surface

- Entrypoint type: stake or vote program instruction
- Sensitive sink: stake delegation, withdrawal, reward accounting, vote authority, or validator weight

## Root Cause

The CLI treated the vote account withdrawal authority as optional and supplied a convenience default to the validator identity key, collapsing distinct operational key roles by omission. The old parser excerpt does not show a guard against unsafe vote-account-key reuse in this path.

## Impact Pattern

- Primary impact: key-management, authority-separation
- Expected band: defense_in_depth_or_input_hardening
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch hardens Solana's create-vote-account CLI path by making `authorized_withdrawer` required and removing the previous fallback that used the validator identity key when the argument was omitted. The provided code also shows a new parser-side rejection when the authorized withdrawer equals the vote account pubkey unless `--allow-unsafe-authorized-withdrawer` is supplied.
