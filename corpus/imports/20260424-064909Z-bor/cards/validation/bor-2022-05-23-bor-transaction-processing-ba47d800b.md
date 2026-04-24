# Validation Card

## Metadata

- ID: `bor-2022-05-23-bor-transaction-processing-ba47d800b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `panic-on-invalid-input`

## What Confirmed The Issue

- Multiple tracer helper paths replace panic(err) with vm.Interrupt(err) or do.vm.Interrupt(err) and return nil.
- The slice helper changes out-of-bounds access from logging a warning and continuing to interrupting execution immediately.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: availability
- Expected severity band: medium

## False-Positive Cautions

- No evidence that these panic paths could crash the entire node or escape higher-level recovery.
- No evidence of remote or unauthenticated reachability in deployment from the patch alone.
