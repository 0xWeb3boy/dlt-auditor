# Validation Card

## Metadata

- ID: `sui-2023-01-09-sui-consensus-4c780d87db`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `finality-rollback`

## What Confirmed The Issue

- Commit message explicitly states a final transaction could be reverted during epoch transition after state sync.
- Checkpoint execution now persists all executed transaction digests with checkpoint sequence information.
- End-of-epoch rollback now skips pending consensus transactions already executed in a checkpoint.
- The affected code is in validator authority, checkpoint executor, checkpoint builder, and epoch store paths.

## What Could Have Invalidated It

- No attacker-controlled trigger path is shown.
- No direct theft, authorization bypass, signature bypass, or confidentiality impact is shown.
- No proof of permanent network-wide fork or chain-wide consensus halt is provided.

## Severity Guidance

- Expected impact band: state-integrity
- Expected severity band: high
- Rationale: Confirmed integrity or authorization impact on a consensus/state path generally warrants high severity unless a narrow deployment condition reduces reachability.

## False-Positive Cautions

- Supported claim: checkpoint-executed transactions could be incorrectly reverted during reconfiguration/state sync ordering.
- Supported claim: the fix preserves finality/state integrity by recording and checking checkpoint execution status before rollback.
- Unsupported claim: this proves direct remote exploitability or guaranteed chain-wide consensus failure.
