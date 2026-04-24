# Validation Card

## Metadata

- ID: `sui-2022-07-04-sui-transaction-processing-362bc47867`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-response-handling`

## What Confirmed The Issue

- Commit message explicitly says requesters know which authorities have checkpoints and certs/effects and can refuse absence claims strictly.
- Cert/effects download now derives voters for the effects digest and passes that authority set into the aggregator fetch API.
- Checkpoint fetching now delegates to an aggregator call using the known available authorities with no retry limit.
- Changed code is in validator gossip, checkpoint, and authority aggregation paths.

## What Could Have Invalidated It

- No aggregator internals are shown to prove exact refusal or quorum behavior.
- No evidence shows invalid certificates or effects could previously be accepted.
- No evidence shows a direct external attacker path or asset-impacting exploit.
- No evidence proves client-view divergence or state representation corruption.

## Severity Guidance

- Expected impact band: availability_or_protocol-liveness
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Keep the finding as hardening, not a proven vulnerability fix.
- Limit impact claims to availability and protocol liveness under faulty or unhelpful authority responses.
- Do not claim signature validation, double-spend prevention, finality safety, or confidentiality impact.
- Do not retain the original serialization-or-state-representation bug class.
