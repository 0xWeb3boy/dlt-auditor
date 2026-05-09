# Root-Cause Card

## Metadata

- ID: `solana-2019-03-18-solana-staking-61a4b998fa`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-vote-safety-hardening`
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

No proven vulnerability root cause is established. The strongest grounded pre-change issue is that replay-stage voting used a placeholder latest-slot selection instead of the newly implemented locktower voting mechanism.

## Impact Pattern

- Primary impact: consensus-integrity, validator-safety
- Expected band: integrity_or_funds
- Severity guide: High

## Short Reusable Lesson

The evidence supports that this commit implements Solana locktower voting and related VoteState helpers/tests. It replaces placeholder latest-slot voting with locktower-oriented bank selection inputs, but the provided evidence does not establish a concrete vulnerability, attacker path, or exploitable consensus failure. Treat this as security-relevant protocol mechanism work, not a validated vulnerability fix.
