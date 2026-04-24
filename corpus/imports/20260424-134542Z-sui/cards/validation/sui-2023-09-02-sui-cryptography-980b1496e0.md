# Validation Card

## Metadata

- ID: `sui-2023-09-02-sui-cryptography-980b1496e0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `multisig-input-validation`

## What Confirmed The Issue

- Commit subject and body explicitly tie the patch to a security audit and named audit findings.
- Multisig public key construction now rejects threshold values below 1.
- Constructor now rejects duplicate public keys in a multisig key map.
- Constructor now rejects thresholds greater than total signer weight and too few signers.

## What Could Have Invalidated It

- No audit report details are provided for Medium-1 or Low-1.
- No exploit scenario or proof of transaction forgery is shown.
- No evidence shows malformed SDK multisig artifacts would be accepted by validators or full nodes.
- No consensus-layer, node-side, or on-chain authorization change is shown.

## Severity Guidance

- Expected impact band: sdk-cryptographic-integrity-hardening
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Keep the finding scoped to SDK-side multisig validation hardening.
- Do not claim a proven request-forgery, replay, fund-loss, or consensus vulnerability.
- The verify signature type narrowing is API tightening and not strong standalone vulnerability evidence.
- The evidence supports security relevance because invalid cryptographic multisig states are rejected earlier, not because a concrete exploit is demonstrated.
