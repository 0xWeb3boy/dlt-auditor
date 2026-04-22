# Root-Cause Card

## Metadata

- ID: `oasis-core-2020-02-06-oasis-core-staking-635fcfd29`
- Bug family: `staking_registry_and_accountability`
- Bug class: `missing-stake-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `stake-enforcement`

## Violated Invariant

- Invariant: When runtime deposit enforcement is enabled, runtime registration and continued runtime operation are intended to require the owning entity to satisfy the relevant stake thresholds.

## Trust Boundary

- Boundary: `operator->registry`

## Attack Surface

- Entrypoint type: `registration-path`
- Sensitive sink: `runtime registry admission`

## Impact Pattern

- Primary impact: `policy-bypass`
- Secondary impact: `improper-runtime-admission`

## Short Reusable Lesson

- When runtime deposit enforcement is enabled, runtime registration and continued runtime operation are intended to require the owning entity to satisfy the relevant stake thresholds. In this pattern, the affected paths previously lacked explicit runtime stake/deposit checks at the shown admission and lifecycle transition points. From the provided evidence alone, it is not proven whether that absence was a vulnerability or simply behavior that this change intentionally tightened. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
