# Validation Card

## Metadata

- ID: `sui-2026-03-25-sui-core-logic-2265f3d6f8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `vm-recursion-bound-hardening`

## What Confirmed The Issue

- Commit subject and body explicitly describe VM hardening and bounding recursive callsites.
- VM type-processing functions such as load_type and abilities now use TypeSize::for_type_traversal().
- abilities_impl wraps recursive processing with type_size.enter_type(...), indicating explicit recursion or traversal accounting.
- Patch touches Move VM runtime dispatch/type verification paths, which are security-sensitive in a blockchain execution environment.

## What Could Have Invalidated It

- No concrete exploit, crash, timeout, or memory exhaustion proof is shown.
- No failing pre-patch regression test demonstrating a security failure is provided.
- No direct evidence proves attacker-controlled reachability from transactions or RPC inputs.
- No consensus divergence, privilege bypass, or data integrity impact is demonstrated.

## Severity Guidance

- Expected impact band: availability-hardening_or_resource-exhaustion-risk-reduction
- Expected severity band: low-medium
- Rationale: The primary risk is availability or resource amplification; severity depends on reachable volume, default exposure, and whether throttling exists elsewhere.

## False-Positive Cautions

- Classify as security hardening, not a confirmed security fix.
- Supported impact is reduced availability/resource-exhaustion risk only.
- Do not claim proven denial of service without additional evidence.
- Do not claim consensus, authorization, or data corruption impact from this patch alone.
