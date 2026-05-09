# Root-Cause Card

## Metadata

- ID: `solana-2020-12-15-solana-consensus-ef9f54b3d4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-race`
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

An ordering race in Bank::register_tick: tick_height served as a signal to ReplayStage, but it could be incremented before all state needed for the slot boundary and accounts hash calculation was committed. The previous is_frozen guard also did not cover the period where freezing had started but was not complete.

## Impact Pattern

- Primary impact: consensus-failure
- Expected band: integrity_or_funds
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch likely fixes a consensus-runtime race in Solana Bank tick registration. The grounded evidence is that tick_height was previously advanced before the blockhash/recent-blockhash sysvar boundary work completed, while the added comment states ReplayStage begins accounts delta hash calculation after observing the boundary tick height. The patch reorders tick publication after those updates and rejects tick registration once freezing has started.
