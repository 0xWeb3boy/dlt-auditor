# Root-Cause Card

## Metadata

- ID: `solana-2020-08-17-solana-staking-d9ae092637`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rent-exemption-recheck-bypass`
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

The old logic used the same `rent_epoch` advancement for actual rent collection and for temporary rent exemption. Because exemption is computed from mutable account state, advancing `rent_epoch` for an exempt account could suppress later rechecking in the same epoch.

## Impact Pattern

- Primary impact: protocol-accounting-integrity
- Expected band: defense_in_depth_or_input_hardening
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch likely fixes a protocol accounting issue in Solana's runtime rent handling. Previously, an existing account that was rent-exempt during collection could have `rent_epoch` advanced to the next epoch even though no rent was collected. The new behavior keeps exempt accounts at the current epoch, allowing exemption to be checked again later in that epoch.
