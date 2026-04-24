# Validation Card

## Metadata

- ID: `bor-2016-11-24-bor-storage-12d654a6f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-inconsistency`

## What Confirmed The Issue

- Commit subject/body explicitly describe a consensus issue and syncing with another client's chain behavior.
- Patch adds explicit journaling for account touch state via touchChange and corresponding undo logic.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No concrete adversarial trigger or exploit scenario is shown in the provided patch.
- No evidence quantifies whether the bug caused remote chain split, DoS, or real-world exploitation.
