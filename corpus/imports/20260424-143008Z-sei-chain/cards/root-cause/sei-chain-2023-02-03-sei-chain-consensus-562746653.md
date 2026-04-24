# Root-Cause Card

## Metadata

- ID: `sei-chain-2023-02-03-sei-chain-consensus-562746653`
- Bug family: `staking_registry_and_accountability`
- Bug class: `oracle-validator-slashing-enforcement-bypass`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `validator-participation-accounting`

## Violated Invariant

- Invariant: All protocol-defined invalid participation categories must count toward validator accountability and slashing thresholds.

## Trust Boundary

- Boundary: validator oracle vote behavior -> staking/slashing accountability state

## Attack Surface

- Entrypoint type: oracle-slashing-endblocker
- Sensitive sink: calculating valid-vote rate and applying slash/jail penalties

## Impact Pattern

- Primary impact: economic-enforcement-bypass
- Secondary impact: validator-accountability-bypass

## Short Reusable Lesson

- Include all counted invalid oracle participation categories in the same slashing threshold calculation. Validators can no longer avoid oracle participation penalties by abstaining instead of missing votes. The slashing calculation now matches the threshold behavior asserted by the updated tests.
