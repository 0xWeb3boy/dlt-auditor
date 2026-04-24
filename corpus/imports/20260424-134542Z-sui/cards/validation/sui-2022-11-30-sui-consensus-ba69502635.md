# Validation Card

## Metadata

- ID: `sui-2022-11-30-sui-consensus-ba69502635`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-liveness-dos`

## What Confirmed The Issue

- Commit body describes a malicious user selectively delivering certificates to validators to block epoch-boundary progress.
- Commit body states the repeated trick can cause denial of service on the network as a whole.
- Patch replaces randomized selected-submitters behavior with per-validator deterministic position and eventual delayed submission.
- submit_and_wait now waits for either prior consensus processing or local delay expiry, then submits if needed.

## What Could Have Invalidated It

- No evidence of consensus safety violation or state divergence.
- No evidence of signature forgery, authorization bypass, or privilege escalation.
- No evidence of asset loss or unauthorized transaction execution.
- No evidence that Byzantine validators are required; the described actor is a malicious client/user.

## Severity Guidance

- Expected impact band: denial-of-service
- Expected severity band: medium
- Rationale: The primary risk is availability or resource amplification; severity depends on reachable volume, default exposure, and whether throttling exists elsewhere.

## False-Positive Cautions

- Classify as consensus liveness denial of service, not consensus safety.
- Security impact is availability of epoch/checkpoint progress.
- The base_types change is supporting deterministic seeding, not the vulnerability root cause.
- The patch proves an eventual submission hardening/fix, not that the delay distribution is optimal.
