# Root-Cause Card

## Metadata

- ID: `moonbeam-2023-10-31-moonbeam-transaction-processing-456027eece`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `proxy-call-filter-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `proxy-target-account-policy`

## Violated Invariant

- Invariant: A proxy call filter must reject target account classes that are not valid delegated real accounts before dispatching on behalf of them.

## Trust Boundary

- Boundary: Delegated proxy calls cross from a proxy origin into actions attributed to a real account that may be an EVM contract.

## Attack Surface

- Entrypoint type: runtime-call-filter
- Sensitive sink: proxy dispatch to EVM contract account

## Impact Pattern

- Primary impact: unauthorized-action
- Secondary impact: origin-confusion, contract-account-policy-bypass

## Short Reusable Lesson

- The NormalFilter denied a few proxy variants but let proxy calls fall through. The patch adds an AccountCodes lookup on the real account and rejects proxy calls targeting contract accounts. Add explicit call-filter logic for proxy targets with deployed EVM code and charge the extra storage read in weights.
