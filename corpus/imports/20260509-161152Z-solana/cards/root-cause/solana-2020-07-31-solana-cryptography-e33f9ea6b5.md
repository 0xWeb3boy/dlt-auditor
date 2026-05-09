# Root-Cause Card

## Metadata

- ID: `solana-2020-07-31-solana-cryptography-e33f9ea6b5`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-role-confusion`
- Confidence tier: `tier_a_confirmed`

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

The root cause was using a generic transaction signer set to decide whether the custodian role had authorized a lockup waiver. Because withdraw authority, custodian, and fee-payer are distinct roles, signer-set membership could conflate those roles when the same pubkey appeared in the signer context.

## Impact Pattern

- Primary impact: lockup-bypass, authorization-bypass
- Expected band: defense_in_depth_or_input_hardening
- Severity guide: High

## Short Reusable Lesson

The patch fixes a stake lockup bypass caused by treating custodian authorization as membership in a generic signer set. The strongest grounded claim is authority-role confusion in stake withdrawal lockup enforcement, not replay, cryptography, network, or validator repair logic.
