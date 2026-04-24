# Validation Card

## Metadata

- ID: `sui-2026-01-10-sui-consensus-f40b60f3a9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-finalization-hardening`

## What Confirmed The Issue

- Direct finalization now excludes blocks outside the GC bound computed from the commit leader.
- Patch comments state that voting or certifying blocks may not include votes for transactions below the leader's GC bound.
- Indirect finalization vote counting is aligned to skip accept votes when votes may have been GCed.
- A protocol feature flag is added specifically to skip GCed blocks in direct finalization.

## What Could Have Invalidated It

- No exploit scenario or attacker-controlled trigger is shown.
- No evidence of finalized invalid transactions, chain divergence, or safety violation is provided.
- No failing regression test or pre-patch reproduction is included in the supplied evidence.
- No direct evidence supports the original liveness-failure impact classification.

## Severity Guidance

- Expected impact band: consensus-integrity
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Classify as consensus hardening around GC-aware finalization, not a confirmed vulnerability fix.
- Do not claim malformed input handling, decoding safety, panic prevention, or remote denial of service.
- Do not claim proven liveness impact from the supplied patch alone.
- Do not claim exploitability beyond the conservative observation that consensus vote inference was tightened.
