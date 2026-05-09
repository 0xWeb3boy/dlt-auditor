# Root-Cause Card

## Metadata

- ID: `solana-2020-06-30-solana-cryptography-88eeb817e4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-restart-precondition-hardening`
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

The visible restart helper treated all non-equal supermajority-slot cases as no-op returns, without distinguishing a harmless already-past condition from the unsafe-looking case where the local ledger was behind the configured restart slot.

## Impact Pattern

- Primary impact: consensus-safety, validator-startup-safety
- Expected band: integrity_or_funds
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch adds restart guard rails for Solana validator startup. `wait_for_supermajority` now returns an error signal when the configured wait slot is greater than the local bank slot, and startup exits on that signal. The validator config path also begins parsing `expected_bank_hash`. The evidence supports operational restart safety hardening, but does not establish a concrete vulnerability, attacker path, or exploitable consensus failure.
