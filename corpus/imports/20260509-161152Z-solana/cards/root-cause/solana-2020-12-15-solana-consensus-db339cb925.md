# Root-Cause Card

## Metadata

- ID: `solana-2020-12-15-solana-consensus-db339cb925`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-ordering-race`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-root-consistency`

## Violated Invariant

- Protocol input must satisfy state root consistency before it can reach bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status.

## Trust Boundary

- Boundary: peer-provided ledger/vote evidence to local consensus and fork-choice state

## Attack Surface

- Entrypoint type: block replay, vote processing, fork-choice update, or duplicate-slot recovery
- Sensitive sink: bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status

## Root Cause

The supported root cause is an ordering race in `Bank::register_tick`: boundary tick height could become visible before slot-boundary blockhash-related updates were complete. The added code comment ties that ordering directly to ReplayStage starting accounts delta hash computation when it observes the boundary tick height. The previous `is_frozen()` guard also left a narrower lifecycle window where tick registration could proceed after freezing had star...

## Impact Pattern

- Primary impact: consensus-integrity-risk
- Expected band: integrity_or_funds
- Severity guide: High

## Short Reusable Lesson

The patch likely fixes a consensus-relevant race in Solana's bank runtime. `Bank::register_tick` previously made the boundary tick height visible before completing blockhash queue and recent blockhashes sysvar updates, while ReplayStage could use that boundary tick height as the signal to begin accounts delta hash calculation. The patch reorders the tick-height increment after those updates and strengthens the guard to reject tick registration once free...
