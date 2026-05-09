# Root-Cause Card

## Metadata

- ID: `solana-2020-04-02-solana-consensus-4649378f95`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-vote-gating`
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

The old ReplayStage logic kept switch-threshold state partly in side bookkeeping and did not include `switch_threshold` in the final vote-producing condition. The evidence supports a vote-gating logic bug, but not a proven exploitable security vulnerability.

## Impact Pattern

- Primary impact: consensus-safety-risk
- Expected band: integrity_or_funds
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch changes Solana ReplayStage fork vote selection so `tower.check_switch_threshold(...)` is evaluated for the heaviest candidate bank and `switch_threshold` is required in the final vote condition. This is consensus-sensitive and may be security relevant, but the supplied evidence does not establish a concrete vulnerability, exploit path, or confirmed safety impact.
