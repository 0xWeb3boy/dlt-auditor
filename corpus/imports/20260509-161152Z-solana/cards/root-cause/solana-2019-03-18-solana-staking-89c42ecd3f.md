# Root-Cause Card

## Metadata

- ID: `solana-2019-03-18-solana-staking-89c42ecd3f`
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

The prior code shown lacked locktower-aware fork-selection logic in replay-stage voting, but the provided evidence does not prove this was a vulnerability root cause. It is better described as missing or incomplete consensus vote-selection machinery.

## Impact Pattern

- Primary impact: consensus-integrity, validator-safety
- Expected band: integrity_or_funds
- Severity guide: High

## Short Reusable Lesson

The patch implements locktower voting in Solana's replay-stage vote path. Evidence supports a consensus-sensitive feature or hardening change: replay stage moves away from a TODO latest-slot vote selection path, `BankForks` exposes ancestor information, and `VoteState` gains recent-vote lookup plus duplicate-vote test coverage. The evidence does not prove a concrete vulnerability, attacker path, or demonstrated unsafe vote condition, so this should not...
