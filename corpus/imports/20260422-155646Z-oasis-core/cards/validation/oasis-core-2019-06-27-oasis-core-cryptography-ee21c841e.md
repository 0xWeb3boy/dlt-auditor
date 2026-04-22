# Validation Card

## Metadata

- ID: `oasis-core-2019-06-27-oasis-core-cryptography-ee21c841e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `predictable-beacon-entropy`

## What Confirmed The Issue

- Evidence 1: The patch introduces an explicit 'debugDeterministic' flag in the beacon application, warns when that mode is used, adjusts epoch-change logic to distinguish production entropy handling from deterministic behavior, removes the scheduler's injected beacon-backend dependency, and removes a direct ABCI beacon getter in the Tendermint backend.
- Evidence 2: The source finding states the invariant explicitly: Production beacon generation should use the canonical Tendermint beacon path and should not silently rely on deterministic or debug entropy behavior.

## What Could Have Invalidated It

- Compensating control 1: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
- Compensating control 2: Not a match if the compared fields are aliases with identical semantics throughout the subsystem.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: Not a match if malformed or incomplete inputs are normalized and rejected before they can reach the sensitive sink.
- Caution 2: Not a match if the compared fields are aliases with identical semantics throughout the subsystem.
