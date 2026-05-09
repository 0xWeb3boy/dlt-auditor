# Root-Cause Card

## Metadata

- ID: `solana-2021-12-06-solana-consensus-e123883b26`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-rent-exemption-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `rent-exemption-invariant`

## Violated Invariant

- Protocol input must satisfy rent exemption invariant before it can reach bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status.

## Trust Boundary

- Boundary: peer-provided ledger/vote evidence to local consensus and fork-choice state

## Attack Surface

- Entrypoint type: block replay, vote processing, fork-choice update, or duplicate-slot recovery
- Sensitive sink: bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status

## Root Cause

The withdraw path did not have Rent context in the dispatcher call, so the shown implementation could not enforce a rent-exemption lifecycle check for partial withdrawals. The precise rejection branch is not included in the supplied excerpt, so the root cause should be limited to missing Rent-aware validation rather than broader state corruption or consensus failure.

## Impact Pattern

- Primary impact: state-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch hardens Solana vote-account withdrawal handling by adding feature-gated Rent sysvar plumbing and making the post-withdraw balance explicit. The provided evidence supports that the change is intended to reject withdrawals that would create non-rent-exempt vote accounts, but it does not establish unauthorized withdrawal, fund theft, lamport creation, or a concrete consensus failure.
