# Validation Card

## Metadata

- ID: `bor-2026-01-27-bor-rpc-client-api-df8f2a879`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-peer-data-verification`

## What Confirmed The Issue

- Witness requests are rerouted through RequestWitnessesWithVerification(...) instead of ad hoc direct requests.
- createWitnessRequester() passes h.verifyPageCount and a peer-jailing callback into the witness request path.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: availability
- Expected severity band: medium

## False-Positive Cautions

- No snippet shows the internals of RequestWitnessesWithVerification or what security property it enforces.
- No provided diff proves a concrete pre-patch exploit such as acceptance of forged witness data or chain-state compromise.
