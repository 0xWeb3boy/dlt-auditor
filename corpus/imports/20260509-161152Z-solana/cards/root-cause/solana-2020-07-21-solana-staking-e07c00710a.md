# Root-Cause Card

## Metadata

- ID: `solana-2020-07-21-solana-staking-e07c00710a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `reward-accounting-invariant`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus-state-transition-invariant`

## Violated Invariant

- Protocol input must satisfy consensus state transition invariant before it can reach bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status.

## Trust Boundary

- Boundary: peer-provided ledger/vote evidence to local consensus and fork-choice state

## Attack Surface

- Entrypoint type: block replay, vote processing, fork-choice update, or duplicate-slot recovery
- Sensitive sink: bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status

## Root Cause

The grounded root cause is inconsistent or insufficiently checked reward accounting in the staking rewards path, including reward split ordering, numeric representation of point value, and lack of explicit post-payment validation against the allocated validator reward amount. The evidence does not prove malicious exploitability.

## Impact Pattern

- Primary impact: economic-integrity, state-integrity
- Expected band: integrity_or_funds
- Severity guide: High

## Short Reusable Lesson

The patch fixes reward-accounting correctness in Solana's staking reward path. The evidence supports changes to reward value representation, staker/voter reward ordering, reward point calculation support, and post-payment assertions that compare observed paid rewards with recorded and allocated rewards. It does not establish an exploitable vulnerability or attacker-controlled path, so the security classification should remain unclear rather than confirm...
