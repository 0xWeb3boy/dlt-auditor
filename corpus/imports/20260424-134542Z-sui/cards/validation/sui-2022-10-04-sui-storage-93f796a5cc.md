# Validation Card

## Metadata

- ID: `sui-2022-10-04-sui-storage-93f796a5cc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-resource-control-hardening`

## What Confirmed The Issue

- Adds resource_exhausted rejection when user consensus in-flight transactions exceed MAX_PENDING_CONSENSUS_TRANSACTIONS.
- Comments explicitly distinguish droppable user transactions from system/checkpoint consensus traffic.
- Consensus listener no longer uses the shown 1,000,000 pending transaction capacity, matching the commit body's lower-capacity resilience goal.
- Commit body states consensus transaction timeouts can cause amplified traffic and changes to a uniform 60 second timeout to avoid that scenario.

## What Could Have Invalidated It

- No proof of a concrete attacker-triggered denial-of-service exploit.
- No evidence of replay, signature validation, authorization, or request-forgery behavior changing.
- No demonstrated consensus safety, ordering, or integrity failure before the patch.
- No severity, exposure model, or exploit reproduction is supplied.

## Severity Guidance

- Expected impact band: denial-of-service-mitigation
- Expected severity band: low-medium
- Rationale: The primary risk is availability or resource amplification; severity depends on reachable volume, default exposure, and whether throttling exists elsewhere.

## False-Positive Cautions

- Classify as security-hardening only, not a confirmed security-fix.
- Do not claim replay, signature validation, request forgery, or authorization impact.
- Do not claim a consensus safety violation was fixed.
- Impact should be limited to resource exhaustion or traffic-amplification mitigation in consensus-adapter handling.
