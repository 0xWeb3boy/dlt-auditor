# Validation Card

## Metadata

- ID: `optimism-2026-04-14-optimism-transaction-processing-f491292ace`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validation-configuration-mismatch`

## What Confirmed The Issue

- Commit message says supernode interop used a hardcoded expiry value instead of the dependency set, breaking cross-safe validation overrides.
- Supernode construction now extracts MessageExpiryWindow() from DependencySet and passes it into interop.New(...).
- Runtime setup now preserves overridden dependency sets instead of always using the original builder dependency set.
- Test support explicitly models a malicious sequencer injecting an expired exec transaction by bypassing mempool filtering.

## What Could Have Invalidated It

- No downstream expiry-checking logic or interop.New(...) implementation is shown.
- No evidence that production deployments used non-default expiry-window overrides.
- No proof of concrete exploit, fund loss, chain safety failure, or broad acceptance of expired messages.
- Much of the diff is test migration and scaffolding rather than direct fix logic.

## Severity Guidance

- Expected impact band: security-hardening-or-correctness
- Expected severity band: low_or_informational

## False-Positive Cautions

- No downstream expiry-checking logic or interop.New(...) implementation is shown.
- No evidence that production deployments used non-default expiry-window overrides.
- No proof of concrete exploit, fund loss, chain safety failure, or broad acceptance of expired messages.
