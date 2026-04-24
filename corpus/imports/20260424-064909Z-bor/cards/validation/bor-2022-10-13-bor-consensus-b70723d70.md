# Validation Card

## Metadata

- ID: `bor-2022-10-13-bor-consensus-b70723d70`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-chain-validation`

## What Confirmed The Issue

- milestone.Lock now rejects locking at or below an existing whitelisted milestone and rejects backward relocking.
- Forward relocking now purges old milestone IDs and clears stale lock state before advancing.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: low

## False-Positive Cautions

- No commit message, advisory, or patch note describes an attack, exploit, or reported vulnerability.
- The supplied excerpts do not show the full production path where LockedSprintHash is consumed for enforcement.
