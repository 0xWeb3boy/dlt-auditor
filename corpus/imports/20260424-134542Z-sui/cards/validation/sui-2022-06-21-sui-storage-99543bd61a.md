# Validation Card

## Metadata

- ID: `sui-2022-06-21-sui-storage-99543bd61a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `non-finalized-state-retention`

## What Confirmed The Issue

- Epoch finalization now iterates over checkpoints.extra_transactions and calls revert_state_update for each transaction digest.
- The new rollback helper is documented as removing certificates/effects, parent_sync entries, new object states, and owner_index changes.
- The reverted transactions are described as locally executed on the validator but not included in the last checkpoint.
- The changed path is part of epoch reconfiguration, checkpoint handling, validator state, and authority storage.

## What Could Have Invalidated It

- No evidence shows a remote or malicious actor can cause extra_transactions to exist.
- No advisory, CVE, incident, or vulnerability description is provided.
- No proof of theft, unauthorized signing, access-control bypass, or externally visible exploit impact is shown.
- No evidence demonstrates network-wide consensus divergence occurred in practice.

## Severity Guidance

- Expected impact band: state-integrity
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Supports a claim that non-finalized local execution effects could remain in durable validator state before this patch.
- Supports checkpoint-finality and state-integrity hardening claims.
- Does not support classifying the issue as a concrete exploitable security fix with high confidence.
- Does not support access-control or privilege-check claims despite one generated evidence reason saying so.
