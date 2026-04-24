# Validation Card

## Metadata

- ID: `sui-2023-10-26-sui-transaction-processing-89049572df`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-control-hardening`

## What Confirmed The Issue

- Adds run_query_async_with_cost, documented as determining query cost before execution and executing only if within limits.
- Routes transaction, object, and epoch database lookup paths through the new cost-aware execution wrapper.
- Updates SQL normalization for cost estimation, including LIMIT placeholders and ANY($N) array expressions.
- Changed subsystem is GraphQL RPC backed by PostgreSQL queries, an externally reachable resource-consumption surface.

## What Could Have Invalidated It

- No exploit scenario or attacker-controlled query example is shown.
- No pre-patch query cost bypass, threshold configuration, or expensive query proof is supplied.
- No evidence shows authentication, authorization, replay protection, signature validation, consensus, or validator state-transition behavior.
- No evidence proves full coverage of all GraphQL query paths.

## Severity Guidance

- Expected impact band: denial-of-service
- Expected severity band: low-medium
- Rationale: The primary risk is availability or resource amplification; severity depends on reachable volume, default exposure, and whether throttling exists elsewhere.

## False-Positive Cautions

- Classify as resource-control hardening only, not a confirmed vulnerability fix.
- Do not retain the original replay-or-signature-validation classification.
- Do not claim consensus or validator safety impact from the supplied evidence.
- Do not claim proven denial-of-service exploitability; only DoS-oriented hardening is supported.
