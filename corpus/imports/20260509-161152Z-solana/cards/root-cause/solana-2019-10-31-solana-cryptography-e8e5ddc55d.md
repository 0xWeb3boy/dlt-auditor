# Root-Cause Card

## Metadata

- ID: `solana-2019-10-31-solana-cryptography-e8e5ddc55d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-ledger-validation`
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

The supported root cause is incomplete validation of PoH tick structure in ledger replay/blocktree processing paths. The evidence does not support broader claims such as memory corruption, signature verification bypass, fund loss, double spend, validator takeover, or proven remote exploitability.

## Impact Pattern

- Primary impact: ledger-integrity, consensus-integrity
- Expected band: integrity_or_funds
- Severity guide: High

## Short Reusable Lesson

The patch adds explicit PoH/tick validation in Solana replay and blocktree processing paths. The strongest grounded claim is that replayed or loaded entries were missing explicit checks for tick hash counts and slot tick counts in the shown paths, and the patch rejects mismatches with typed block errors. The evidence supports a consensus/ledger-integrity hardening or likely security fix, but not a proven exploit or demonstrated network-level compromise.
