# Code-Shape Card

## Metadata

- ID: `bor-2026-02-26-bor-cryptography-b69ad46c1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `timestamp-validation`

## Code Shape Summary

- The patch adds a missing upper bound on Rio-era block timestamps in verifyHeader. The shown evidence supports a consensus-liveness issue where a validator-supplied far-future header could pass the relaxed Rio checks before this change; after the patch, headers more than 30 seconds ahead of local time are rejected with ErrFutureBlock. Root cause: After Rio relaxed timestamp validation to allow flexible block times, verifyHeader no longer enforced an upper bound on validator-controlled header.Time relative to the local clock.

## Search Motifs

- input decoder feeds state-changing logic before semantic validation
- error path logs or ignores invalid data instead of failing closed
- security-relevant state changes occur before all invariants are checked

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Restore a missing validation invariant at the consensus boundary by bounding acceptable future timestamp skew before later scheduling logic runs.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Treat as hardening when the patch only improves error reporting, refactoring, or defensive checks without attacker reachability.
