# Validation Card

## Metadata

- ID: `stellar-core-2015-08-07-stellar-core-storage-983043fc7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-consensus-configuration`
- Security verdict: `confirmed`
- Validated as: `security-hardening`

## What Confirmed The Issue

- Config parsing moved from THRESHOLD to bounded THRESHOLD_PERCENT.
- Effective qset.threshold is computed from quorum-set size.
- Config gained FAILURE_SAFETY and UNSAFE_QUORUM validation.

## What Could Have Invalidated It

- If the repo only stores sample configs and not runtime validation, this becomes documentation hardening.
- If downstream deployment tooling already rejects unsafe configs, duplicate checks reduce severity.

## Severity Guidance

- Expected impact band: high
- Expected severity band: high_or_medium
- Rationale: Unsafe quorum configuration can undermine Byzantine fault tolerance. This is confirmed hardening, not a remote exploit, so high but configuration-scoped.

## False-Positive Cautions

- Do not treat every config knob as attacker-controlled.
- Do not label as storage corruption just because the generated subsystem says storage.
