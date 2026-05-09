# Root-Cause Card

## Metadata

- ID: `solana-2020-04-16-solana-consensus-66abe45ea1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-consistency-monitoring`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `snapshot-integrity-binding`

## Violated Invariant

- Protocol input must satisfy snapshot integrity binding before it can reach bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status.

## Trust Boundary

- Boundary: peer-provided ledger/vote evidence to local consensus and fork-choice state

## Attack Surface

- Entrypoint type: block replay, vote processing, fork-choice update, or duplicate-slot recovery
- Sensitive sink: bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status

## Root Cause

Accounts hash scheduling was coupled to snapshot generation configuration and sender availability. The provided evidence shows this could make accounts hash calculation depend on snapshot setup, but does not prove a resulting security breach.

## Impact Pattern

- Primary impact: integrity-monitoring-bypass, validator-state-divergence-detection-gap
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch decouples accounts hash calculation from snapshot package generation and adds interval validation. The evidence supports a correctness and state-monitoring improvement in the accounts-hash/snapshot path, but it does not establish an exploitable vulnerability or a concrete security failure. Treat it as security-relevant but unproven rather than a confirmed security fix.
