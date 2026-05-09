# Root-Cause Card

## Metadata

- ID: `solana-2020-12-15-solana-consensus-75e9e321de`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-publication-race`
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

An ordering bug exposed tick_height as a synchronization signal before the state that ReplayStage would hash at that boundary was fully updated. The freeze guard was also weaker than the new invariant because it only checked the completed frozen state.

## Impact Pattern

- Primary impact: consensus-inconsistency
- Expected band: integrity_or_funds
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch fixes a race in Bank::register_tick where tick_height could be published before boundary-related account updates completed, while ReplayStage uses that boundary tick as a signal to start accounts delta hash calculation. The evidence supports a consensus/account-hash ordering bug, but does not establish remote exploitability, fund theft, signature bypass, or hash forgery.
