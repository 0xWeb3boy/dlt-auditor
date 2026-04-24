# Root-Cause Card

## Metadata

- ID: `sui-2022-06-21-sui-storage-99543bd61a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `non-finalized-state-retention`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: Persisted ledger state must remain authenticated, epoch-scoped, and consistent with the executed transition that produced it.

## Trust Boundary

- Boundary: executed effects or checkpoint data -> authenticated persistent state

## Attack Surface

- Entrypoint type: state-transition-storage-update
- Sensitive sink: persisting or serving authenticated ledger state

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch fixes a missing rollback in Sui epoch finalization. Before the change, `finish_epoch_change` detected non-empty `checkpoints.extra_transactions` but only had a deferred guard for reverting them.
