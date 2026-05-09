# Root-Cause Card

## Metadata

- ID: `solana-2023-09-05-solana-consensus-a8e83c8720`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-duplicate-slot-state-recovery`
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

Replay logic relied on in-memory duplicate-slot tracking in paths where duplicate-slot evidence could already be persisted in Blockstore. When the tracker did not contain the slot, initialization and state-transition handling could fail to reflect that persisted duplicate evidence in the replay state machine and fork choice.

## Impact Pattern

- Primary impact: consensus-safety-hardening
- Expected band: integrity_or_funds
- Severity guide: Low/Medium

## Short Reusable Lesson

Likely consensus security fix in Solana replay handling. The patch makes ReplayStage recover duplicate-slot records from Blockstore and feed them into duplicate-slot state checking and fork-choice invalidation. The evidence supports a consensus-state synchronization issue, but does not prove exploitability, finality failure, fund loss, or attacker control.
