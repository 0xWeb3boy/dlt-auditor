# Validation Card

## Metadata

- ID: `bor-2023-01-11-bor-transaction-processing-793f0f9ec`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-control-hardening`

## What Confirmed The Issue

- Adds an explicit max initcode size check before contract creation execution.
- Adds per-word initcode gas charging in intrinsic gas calculation under EIP-3860.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: availability
- Expected severity band: medium

## False-Positive Cautions

- No proof of a preexisting vulnerability or exploit is shown in the patch.
- No incident, CVE, advisory, or bug report ties the change to an actual attack.
