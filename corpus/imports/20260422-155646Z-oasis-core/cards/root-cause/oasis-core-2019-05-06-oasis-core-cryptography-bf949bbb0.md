# Root-Cause Card

## Metadata

- ID: `oasis-core-2019-05-06-oasis-core-cryptography-bf949bbb0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: When building epoch node lists, the scheduler should only derive runtime and TEE classification from known runtime entries and capability data that passes local verification at the current timestamp; unknown runtimes and invalid or absent TEE capability data should not be treated as normal eligible inputs.

## Trust Boundary

- Boundary: `committee-member->consensus`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: `validator set composition`

## Impact Pattern

- Primary impact: `integrity-risk`
- Secondary impact: `none`

## Short Reusable Lesson

- When building epoch node lists, the scheduler should only derive runtime and TEE classification from known runtime entries and capability data that passes local verification at the current timestamp; unknown runtimes and invalid or absent TEE capability data should not be treated as normal eligible inputs. In this pattern, the only grounded issue visible in the provided diff is that this scheduler path previously consumed runtime capability metadata with weaker local validation. The stronger claim that the system as a whole lacked attestation verification is not established from the provided evidence, because earlier registration-time or other validation is not shown. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
