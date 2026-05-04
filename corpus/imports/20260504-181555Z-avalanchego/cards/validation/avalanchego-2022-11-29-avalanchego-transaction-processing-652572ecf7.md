# Validation Card

## Metadata

- ID: `avalanchego-2022-11-29-avalanchego-transaction-processing-652572ecf7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `replay-protection-bypass-hardening`

## What Confirmed The Issue

- Evidence: `UnprotectedAllowed` now receives the transaction being evaluated instead of returning only a global boolean policy.
- Evidence: When the global unprotected-transaction flag is false, the patched path checks an exact transaction hash allowlist.
- Evidence: Backend initialization builds a read-only `allowUnprotectedTxHashes` map from configuration.

## What Could Have Invalidated It

- Compensating control: No evidence that unprotected transactions were accepted by default.
- Compensating control: No demonstrated remote attacker path or exploit scenario.
- Compensating control: No proof of consensus validation bypass or state corruption.

## Severity Guidance

- Expected impact band: medium_or_low_hardening
- Expected severity band: medium_or_low
- Severity rationale: The change narrows a risky compatibility exception, but the finding does not prove arbitrary replay acceptance in the default configuration.

## False-Positive Cautions

- Caution: Validate only as security hardening around replay-protection-sensitive transaction admission.
- Caution: Do not claim a confirmed exploitable vulnerability.
- Caution: Do not claim consensus-layer transaction validation was broken.
