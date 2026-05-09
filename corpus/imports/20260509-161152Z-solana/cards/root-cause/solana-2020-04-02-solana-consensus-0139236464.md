# Root-Cause Card

## Metadata

- ID: `solana-2020-04-02-solana-consensus-0139236464`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-vote-guard-hardening`
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

The grounded issue is inconsistent or under-enforced switch-threshold handling in the shown `ReplayStage` voting path. The evidence supports that the final vote decision previously did not include `switch_threshold`; it does not establish the concrete protocol impact of that omission.

## Impact Pattern

- Primary impact: consensus-integrity-risk
- Expected band: integrity_or_funds
- Severity guide: High

## Short Reusable Lesson

The patch changes Solana `ReplayStage` fork-voting logic so `switch_threshold` is computed with `tower.check_switch_threshold(...)`, failure is recorded explicitly, and the final vote predicate requires `switch_threshold`. This is consensus-relevant logic, but the supplied evidence does not prove a security vulnerability, exploit path, network split, or finalized consensus divergence. Treat as unclear rather than a confirmed or likely security fix.
