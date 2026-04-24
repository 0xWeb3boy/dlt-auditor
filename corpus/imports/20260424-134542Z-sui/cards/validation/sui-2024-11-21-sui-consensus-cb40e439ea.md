# Validation Card

## Metadata

- ID: `sui-2024-11-21-sui-consensus-cb40e439ea`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-limit-accounting`

## What Confirmed The Issue

- Consensus transaction selection now checks aggregate block bytes against max_transactions_in_block_bytes.
- Consensus transaction selection now checks selected-plus-incoming transaction count against max_num_transactions_in_block.
- Commit message states the prior behavior could go over the max limit and produce invalid blocks rejected by block verification.
- The changed code is in consensus block construction and verification paths, which enforce protocol validity limits.

## What Could Have Invalidated It

- No evidence that an external attacker can force the oversized batch condition.
- No evidence of signature, authorization, transaction semantic validation, or verifier bypass.
- No evidence of chain safety failure, finality violation, or sustained network denial of service.
- No test output or incident details showing practical exploitability.

## Severity Guidance

- Expected impact band: invalid-block-production_or_consensus-liveness-risk
- Expected severity band: low-medium
- Rationale: The primary risk is availability or resource amplification; severity depends on reachable volume, default exposure, and whether throttling exists elsewhere.

## False-Positive Cautions

- Classify as security-hardening, not security-fix.
- Limit the impact claim to invalid block production and possible consensus liveness risk.
- Do not claim client-view divergence or serialization/state-representation flaws from this evidence.
- Treat metrics additions as non-security support changes.
