# Validation Card

## Metadata

- ID: `sui-2025-07-18-sui-cryptography-5dce17a946`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-commitment-gap`

## What Confirmed The Issue

- Adds an IndirectStateObserver that serializes observed indirect state into a running hash.
- Conditionally folds the indirect-state hash into the additional consensus digest recorded in the consensus commit prologue.
- Threads the observer into consensus transaction processing around shared-object congestion transaction-cost decisions.
- Adds a protocol feature flag described as including indirect state in the additional consensus digest.

## What Could Have Invalidated It

- No concrete external attacker path is shown.
- No proof of unauthorized execution, theft, signature bypass, or cryptographic primitive weakness is provided.
- No specific prior production incident or exploit scenario is included in the supplied evidence.
- The excerpts do not fully show every indirect state source or prove complete coverage.

## Severity Guidance

- Expected impact band: consensus-integrity_or_state-integrity
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Classify as consensus/state-integrity hardening only.
- Do not claim a confirmed exploitable vulnerability.
- Do not describe this as a signature, RPC, snapshot, or cryptographic primitive fix.
- Runtime effect depends on the added protocol flag being enabled.
