# Validation Card

## Metadata

- ID: `sui-2024-06-26-sui-rpc-client-api-a025ca0517`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `traffic-control-accounting-gap`

## What Confirmed The Issue

- Commit states traffic controller spam classification is being changed for request types that do not consume gas.
- Authority service responses now carry a spam_weight alongside successful RPC response payloads.
- handle_traffic_resp extracts spam_weight for traffic-controller accounting instead of deriving only error information from the RPC result.
- Already-executed certificate handling now returns response data together with a Weight, covering a gasless read-and-return path.

## What Could Have Invalidated It

- No proof that the previous behavior enabled a practical remote denial-of-service attack.
- No demonstrated bypass threshold, attacker workflow, or resource exhaustion measurement is provided.
- No evidence of consensus failure, state corruption, authorization bypass, or client-view divergence.
- Only selected snippets are supplied, so the full traffic-controller policy effect is inferred from metadata and changed types.

## Severity Guidance

- Expected impact band: resource-exhaustion
- Expected severity band: low-medium
- Rationale: The primary risk is availability or resource amplification; severity depends on reachable volume, default exposure, and whether throttling exists elsewhere.

## False-Positive Cautions

- Classify as anti-abuse traffic-control hardening, not a confirmed vulnerability fix.
- Do not claim serialization, canonical state representation, or state consistency repair.
- Do not claim economic loss, consensus compromise, or incorrect transaction execution.
- Supported claim is limited to improved accounting/classification of successful gasless validator/RPC work.
