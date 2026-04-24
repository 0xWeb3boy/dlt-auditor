# Code-Shape Card

## Metadata

- ID: `sui-2022-11-30-sui-consensus-ba69502635`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-liveness-dos`

## Code Shape Summary

- This is a confirmed availability/liveness security fix in the checkpoint-consensus path. The commit describes a malicious client delivery pattern where a validator can receive and retain a certificate but never submit it because only a randomized subset of validators was responsible for submission.

## Search Motifs

- resource-accounting enforced after parsing but before consensus state mutation
- consensus handler accepts externally supplied protocol data
- unbounded loop/cache/retry path driven by remote input
- missing per-client or per-digest resource attribution

## Typical Asymmetry

- Cheap attacker-controlled submissions can force repeated validator work unless the path charges, attributes, or throttles before the expensive operation.

## Patch Pattern

- Replace exclusive randomized submitter responsibility with deterministic staggered eventual responsibility: validators may delay submission to reduce duplicate load, but every validator retains an eventual local submission fallback.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- A separate hard cap, authenticated quota, or upstream rate limit makes repeated work impossible.
- The value is only advisory and is recomputed from canonical local consensus state before use.
