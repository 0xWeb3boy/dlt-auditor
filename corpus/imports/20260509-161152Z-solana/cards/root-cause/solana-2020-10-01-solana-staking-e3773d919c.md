# Root-Cause Card

## Metadata

- ID: `solana-2020-10-01-solana-staking-e3773d919c`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `integer-overflow`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `checked-arithmetic-bounds`

## Violated Invariant

- Protocol input must satisfy checked arithmetic bounds before it can reach bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status.

## Trust Boundary

- Boundary: peer-provided ledger/vote evidence to local consensus and fork-choice state

## Attack Surface

- Entrypoint type: block replay, vote processing, fork-choice update, or duplicate-slot recovery
- Sensitive sink: bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status

## Root Cause

The root cause was an overflow-prone intermediate multiplication in rent-share accounting: both `staked` and `rent_to_be_distributed` were `u64`, and their product was calculated before division. The provided evidence does not show that an attacker can control these values, trigger a crash, steal funds, or cause consensus divergence.

## Impact Pattern

- Primary impact: economic-integrity, consensus-integrity
- Expected band: integrity_or_funds
- Severity guide: High

## Short Reusable Lesson

The provided evidence supports an overflow-prone rent distribution calculation in Solana runtime accounting, but it does not establish an exploitable security vulnerability. The patch replaces `u64` intermediate multiplication in validator rent-share calculation with feature-gated `u128` arithmetic and tightens leftover lamport handling. This is plausibly security-relevant consensus/economic hardening, but the vulnerability thesis is not proven from the...
