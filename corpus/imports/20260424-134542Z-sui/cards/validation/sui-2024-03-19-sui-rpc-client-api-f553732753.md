# Validation Card

## Metadata

- ID: `sui-2024-03-19-sui-rpc-client-api-f553732753`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-rpc-epoch-filter-hardening`

## What Confirmed The Issue

- Consensus RPC routing already used `RequireAuthorizationLayer` for allowed peers and now adds `RequireAuthorizationLayer::new(AllowedEpoch::new(...))`.
- `AllowedEpoch` rejects requests with a missing epoch header using `BadRequest`.
- `AllowedEpoch` rejects requests whose epoch header differs from the node's current committee epoch.
- Commit body explicitly mentions adding a network filter for requests from different epochs.

## What Could Have Invalidated It

- No concrete exploit path is shown for cross-epoch requests.
- No evidence proves prior behavior caused consensus safety, liveness, or authorization failure.
- No evidence shows the metrics or excessive-message-size changes enforce blocking security policy.
- No evidence shows an `AllowedPeers` bypass or unauthenticated access issue.

## Severity Guidance

- Expected impact band: network-request-filtering_or_consensus-epoch-isolation
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Treat as hardening of consensus RPC epoch separation, not a confirmed vulnerability fix.
- Do not claim DoS, crash, privilege escalation, or consensus compromise from the supplied patch alone.
- Do not treat non-blocking excessive-message-size metrics as resource-control enforcement.
- Do not classify as liveness-failure based on the provided evidence.
