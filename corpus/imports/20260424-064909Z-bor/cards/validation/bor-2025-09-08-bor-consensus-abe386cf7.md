# Validation Card

## Metadata

- ID: `bor-2025-09-08-bor-consensus-abe386cf7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-set-validation`

## What Confirmed The Issue

- A new pre-Rio gate was added before seal verification to check validator or producer bytes against expected snapshot or span state.
- Sprint-start validator derivation changed from reconstructing from span-store producer data to GetCurrentValidatorsByHash(...), which is a stricter context-aware source.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No advisory, test, or commit text states a concrete vulnerability or exploit scenario.
- No proof that seal verification could previously be bypassed or that invalid blocks were accepted.
