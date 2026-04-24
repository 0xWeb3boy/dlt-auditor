# Validation Card

## Metadata

- ID: `bor-2022-05-23-bor-rpc-client-api-1b5304405`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `privileged-api-exposure`

## What Confirmed The Issue

- Commit subject states an option was added to disable personal wallet endpoints.
- server.go replaces keystore registration on the shared stack account manager with a new scoped accounts.Manager used only for signing.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: confidentiality
- Expected severity band: medium

## False-Positive Cautions

- No patch evidence shows the exact pre-patch RPC exposure or default network reachability of personal endpoints.
- No test, exploit, or runtime trace demonstrates unauthorized signing or wallet use before the change.
