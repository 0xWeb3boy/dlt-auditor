# Root-Cause Card

## Metadata

- ID: `oasis-core-2019-11-11-oasis-core-rpc-client-api-7816e47dd`
- Bug family: `staking_registry_and_accountability`
- Bug class: `validator-selection-policy`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `selection-policy-enforcement`

## Violated Invariant

- Invariant: Validator election should apply explicitly defined eligibility limits consistently at genesis and during validator selection; the evidence shows this limit became a separate configured parameter, but does not establish that the prior behavior violated safety or allowed an exploit.

## Trust Boundary

- Boundary: `remote-peer->rpc-verifier`

## Attack Surface

- Entrypoint type: `rpc-handler`
- Sensitive sink: `validator set composition`

## Impact Pattern

- Primary impact: `validator-selection-integrity`
- Secondary impact: `consensus-policy-enforcement`

## Short Reusable Lesson

- Validator election should apply explicitly defined eligibility limits consistently at genesis and during validator selection; the evidence shows this limit became a separate configured parameter, but does not establish that the prior behavior violated safety or allowed an exploit. In this pattern, the visible issue is that the entity-level cutoff used in validator election was not represented as its own explicit, validated consensus parameter. Instead, the election path used 'topN', and the patch separates that policy into 'ValidatorEntityThreshold' and requires it to be configured. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
