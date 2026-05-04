# Root-Cause Card

## Metadata

- ID: `moonbeam-2022-09-12-moonbeam-staking-c7d8fc12f2`
- Bug family: `authz_and_role_gates`
- Bug class: `evm-precompile-authorization-boundary-hardening`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `precompile-caller-eligibility`

## Violated Invariant

- Invariant: An EVM precompile that bridges to privileged runtime dispatch must explicitly reject caller classes that are not allowed to originate those actions.

## Trust Boundary

- Boundary: Smart-contract code crosses the EVM/runtime boundary into proxy or generic dispatch behavior.

## Attack Surface

- Entrypoint type: evm-precompile-call
- Sensitive sink: proxy/dispatch runtime call bridge

## Impact Pattern

- Primary impact: unauthorized-action
- Secondary impact: runtime-call-bypass, origin-confusion

## Short Reusable Lesson

- The proxy precompile entered selector handling before checking caller code, and runtimes exposed a generic Dispatch precompile. The patch added caller-code rejection and removed Dispatch registration. Add an early caller-code guard in the precompile and remove broad generic dispatch exposure from runtime precompile sets.
