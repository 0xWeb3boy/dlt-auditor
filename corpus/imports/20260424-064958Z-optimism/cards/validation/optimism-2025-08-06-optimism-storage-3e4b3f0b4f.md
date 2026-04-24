# Validation Card

## Metadata

- ID: `optimism-2025-08-06-optimism-storage-3e4b3f0b4f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-state-rewind`

## What Confirmed The Issue

- The main code path now rejects rewinds where to.number <= local_safe.number.
- The new error RewindBeyondLocalSafeHead makes the forbidden boundary crossing explicit.
- The trait documentation now states that rewind_log_storage must not cross the local-safe head.
- A regression test was added for the rejected rewind-beyond-safe-head case.

## What Could Have Invalidated It

- No proof that untrusted or remote actors can invoke this rewind path.
- No demonstrated exploit chain from invalid rewind to consensus failure, forgery, or fund loss.
- No evidence that this bug was previously reachable in production deployments.
- No advisory, CVE, or security report tying the issue to an attacker scenario.

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that untrusted or remote actors can invoke this rewind path.
- No demonstrated exploit chain from invalid rewind to consensus failure, forgery, or fund loss.
- No evidence that this bug was previously reachable in production deployments.
