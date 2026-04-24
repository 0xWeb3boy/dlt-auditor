# Root-Cause Card

## Metadata

- ID: `geth-arb-2022-03-17-go-ethereum-storage-368fbe57cb`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `validator-configuration-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `validator-configuration-preflight`

## Violated Invariant

- Invariant: Validator startup should fail closed when required chain, data-availability, or node-access configuration is missing or inconsistent with the selected validation mode.

## Trust Boundary

- Boundary: operator configuration -> validator runtime and chain access

## Attack Surface

- Entrypoint type: validator startup/configuration loader
- Sensitive sink: validator participation, block validation, or node-action generation

## Impact Pattern

- Primary impact: validator-safety
- Secondary impact: availability
- Severity guide: low-medium

## Short Reusable Lesson

- Validator mode selected security-sensitive behavior without enough preflight checks for data availability, L1 access, or block validation configuration. Add startup preflight checks that reject inconsistent or incomplete validator configuration before participation begins.
