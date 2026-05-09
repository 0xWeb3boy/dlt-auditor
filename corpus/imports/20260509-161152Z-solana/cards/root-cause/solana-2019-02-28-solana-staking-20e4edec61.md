# Root-Cause Card

## Metadata

- ID: `solana-2019-02-28-solana-staking-20e4edec61`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `vote-account-binding-confusion`
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

The grounded issue is an unsafe or underspecified vote-account binding assumption in the old registration flow. The code evidence supports concern about positional account confusion, but does not fully establish that arbitrary account ordering was exploitable in practice or that the shown checks alone close the entire issue.

## Impact Pattern

- Primary impact: consensus-integrity, authorization-integrity
- Expected band: integrity_or_funds
- Severity guide: High

## Short Reusable Lesson

The patch is plausibly security hardening for Solana vote account setup. The strongest evidence is the removed TODO in `sdk/src/vote_program.rs`, which explicitly warned that the old `register` flow assumed `keyed_accounts[0]` was the account creator for `keyed_accounts[1]` and that a different signed instruction in that slot could allow vote-account hijacking and leader-rotation insertion. The patch refactors the vote account setup path, adds explicit...
