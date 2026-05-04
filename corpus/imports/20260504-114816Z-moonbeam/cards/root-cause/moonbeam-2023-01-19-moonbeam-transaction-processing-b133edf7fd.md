# Root-Cause Card

## Metadata

- ID: `moonbeam-2023-01-19-moonbeam-transaction-processing-b133edf7fd`
- Bug family: `resource_accounting_and_limits`
- Bug class: `gas-accounting-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `gas-limit-overhead-accounting`

## Violated Invariant

- Invariant: Precompile paths must account for their own overhead and downstream subcall costs before accepting work that can consume execution resources.

## Trust Boundary

- Boundary: User-selected gas limits and EVM call gas cross into runtime randomness fulfillment/request logic.

## Attack Surface

- Entrypoint type: randomness-precompile-request-or-fulfillment
- Sensitive sink: randomness request/fulfillment subcall execution

## Impact Pattern

- Primary impact: denial-of-service
- Secondary impact: resource-accounting, unexpected-revert

## Short Reusable Lesson

- The precompile compared caller gas to request limits without adding subcall overhead and lacked a conservative remaining-gas check for fulfillment. The fix uses checked_add and upfront max-cost checks. Use checked arithmetic for gas-plus-overhead and reject calls early when remaining gas cannot cover worst-case preparation and finish costs.
