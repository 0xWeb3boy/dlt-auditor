# Validation Card

## Metadata

- ID: `sui-2022-06-30-sui-consensus-992af87ebf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `byzantine-availability-hardening`

## What Confirmed The Issue

- New helper is documented for cases where Byzantine authorities can time out or slow-loris but cannot provide false answers because the response is digest-authenticated or quorum-signed.
- Node sync changes transaction/effects download from a direct peer client request to AuthorityAggregator.handle_transaction_and_effects_info_request.
- Removed comment states the prior path depended on a validator that may be Byzantine and refuse to provide the cert and effects.
- TimeoutError is added as part of the new timeout-aware authority aggregation path.

## What Could Have Invalidated It

- No evidence that forged or invalid transaction/effects data could previously be accepted.
- No evidence of consensus divergence, state corruption, or safety violation.
- No exploit scenario or vulnerability advisory is provided.
- No proof that the change fully covers all object-fetch or node-sync paths.

## Severity Guidance

- Expected impact band: availability-degradation_or_liveness-degradation
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Classify as Byzantine availability/liveness hardening, not consensus-safety.
- Impact should be limited to reducing single-peer withholding, timeout, or slow-response risk.
- The evidence supports one-success authenticated fetch behavior only where correctness is anchored by known digests or quorum signatures.
- Do not claim an integrity bypass, signature failure, or concrete exploitable consensus bug from this patch alone.
