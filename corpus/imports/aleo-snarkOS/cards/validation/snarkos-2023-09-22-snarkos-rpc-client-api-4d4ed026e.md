# Validation Card

## Metadata

- ID: `snarkos-2023-09-22-snarkos-rpc-client-api-4d4ed026e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-request-response-correlation`

## What Confirmed The Issue

- The raw finding was validated by phase 4 as `security-hardening` with verdict `likely` and kept in the security corpus.
- The patch pattern matches the missing property: Track outbound validator requests per peer, reject responses without a matching request, and decrement the counter when accepted.
- Root-cause evidence from the finding: The grounded root cause is missing peer-specific request/response correlation in the shown Narwhal ValidatorsResponse handling. The evidence supports that unsolicited or excess validator responses could reach follow-on validator connection logic after only a size check. It does not establish consensus compromise, cryptographic bypass, or a concrete exploit beyond influence over validator-discovery connection behavior. 1. A peer sends a ValidatorsResponse containing a validators list. 2. The pre-

## What Could Have Invalidated It

- Connection attempts independently verify each validator and rate limit peers.
- Discovery protocol is trusted/closed-membership only.

## Severity Guidance

- Expected impact band: `discovery-integrity`
- Expected severity band: `medium`
- Rationale: Medium severity is appropriate when the affected boundary is reachable and the sink controls unsolicited discovery response processing; reduce severity when the change is only hardening or a compensating control already enforces the invariant.

## False-Positive Cautions

- Broadcast announcements intentionally processed without request are different
- If response data is ignored unless separately verified, severity drops
- A global request flag is weaker than peer-specific correlation
