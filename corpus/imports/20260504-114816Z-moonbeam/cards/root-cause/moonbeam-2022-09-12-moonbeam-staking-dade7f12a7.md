# Root-Cause Card

## Metadata

- ID: `moonbeam-2022-09-12-moonbeam-staking-dade7f12a7`
- Bug family: `authz_and_role_gates`
- Bug class: `evm-precompile-access-control-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `precompile-caller-eligibility`

## Violated Invariant

- Invariant: Runtime-call precompiles must enforce caller-type policy at the boundary before decoding or dispatching sensitive selectors.

## Trust Boundary

- Boundary: EVM contract execution crosses into substrate runtime proxy/dispatch functionality.

## Attack Surface

- Entrypoint type: evm-precompile-call
- Sensitive sink: proxy/dispatch runtime call bridge

## Impact Pattern

- Primary impact: unauthorized-action
- Secondary impact: origin-confusion, runtime-call-bypass

## Short Reusable Lesson

- The EVM precompile boundary lacked a reusable caller eligibility check for code-bearing accounts. The fix queries AccountCodes before selector handling and removes the Dispatch precompile. Fail early for disallowed contract callers and narrow the runtime precompile surface by unregistering generic dispatch.
