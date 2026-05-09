# Validation Card

## Metadata

- ID: `agave-2026-04-27-agave-validator-ops-7b7ffdd747`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `cli-validator-info-signer-check`

## What Confirmed The Issue

- parse_validator_info now returns a signer boolean with the validator pubkey and metadata.
- publish selection requires Some((validator_pubkey, true, _)) and malformed accounts return None rather than panicking.

## What Could Have Invalidated It

- CLI output never influences operator decisions or transaction construction.
- All displayed records already come from a query that enforces signer authenticity.

## Severity Guidance

- Expected impact band: `operator metadata authenticity`
- Expected severity band: `low`
- Rationale: The issue affects CLI trust and robustness around validator metadata, with no proven protocol-state, fund, consensus, or takeover impact.

## False-Positive Cautions

- CLI-only authenticity fixes are usually low severity unless they affect automated operations.
- Do not infer validator takeover or protocol authorization bypass from metadata display hardening.
