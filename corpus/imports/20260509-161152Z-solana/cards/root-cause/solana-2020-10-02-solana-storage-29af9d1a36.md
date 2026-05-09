# Root-Cause Card

## Metadata

- ID: `solana-2020-10-02-solana-storage-29af9d1a36`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `integer-overflow-accounting`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `checked-arithmetic-bounds`

## Violated Invariant

- Protocol input must satisfy checked arithmetic bounds before it can reach stake delegation, withdrawal, reward accounting, vote authority, or validator weight.

## Trust Boundary

- Boundary: signed stake/vote instruction to stake-weighted accounting state

## Attack Surface

- Entrypoint type: stake or vote program instruction
- Sensitive sink: stake delegation, withdrawal, reward accounting, vote authority, or validator weight

## Root Cause

The root cause was proportional rent-share accounting that multiplied two `u64` values before widening. If `staked * rent_to_be_distributed` overflowed, the derived validator share could be incorrect before later leftover handling.

## Impact Pattern

- Primary impact: state-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The evidence supports a likely security-relevant accounting fix in Solana Bank rent distribution. The patch changes validator rent-share computation from `u64` intermediate multiplication to feature-gated `u128` arithmetic, then asserts that no leftover lamports remain under the corrected path. The provided evidence does not establish remote exploitability, attacker control of the required values, or a demonstrated consensus split, so the finding should...
