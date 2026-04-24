# Validation Card

## Metadata

- ID: `sui-2026-03-30-sui-rpc-client-api-54e640f65d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-traffic-control-accounting`

## What Confirmed The Issue

- Commit subject says gasless transactions are counted for DoS protection.
- Commit body says gasless transactions should be counted because they have no cost to the sender.
- Patch adds `spam_weight` tracking in the validator submit path.
- Patch sets `spam_weight = Weight::one()` when `is_gasless_transaction()` is true.

## What Could Have Invalidated It

- No caller-side traffic-controller enforcement logic is shown.
- No regression test contents are provided.
- No demonstrated exploit, attack volume, or practical network-level DoS impact is shown.
- No evidence of signature bypass, consensus safety failure, unauthorized state change, or client-view divergence is shown.

## Severity Guidance

- Expected impact band: denial-of-service_or_resource-exhaustion
- Expected severity band: medium
- Rationale: The primary risk is availability or resource amplification; severity depends on reachable volume, default exposure, and whether throttling exists elsewhere.

## False-Positive Cautions

- Validate only as DoS-oriented traffic-control hardening/accounting.
- Do not classify as serialization, state representation, signature, consensus, or RPC client-view divergence.
- Do not claim proven exploitability or confirmed service outage from the patch alone.
- Do not claim economic loss or unauthorized transaction execution.
