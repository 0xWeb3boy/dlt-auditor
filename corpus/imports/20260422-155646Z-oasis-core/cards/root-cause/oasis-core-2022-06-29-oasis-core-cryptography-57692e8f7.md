# Root-Cause Card

## Metadata

- ID: `oasis-core-2022-06-29-oasis-core-cryptography-57692e8f7`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-query-verification`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `query-verification`

## Violated Invariant

- Invariant: Historical query state access should only use consensus state derived from a runtime header that has been checked against the expected runtime identity and associated consensus block.

## Trust Boundary

- Boundary: `client->query-verifier`

## Attack Surface

- Entrypoint type: `query-verification-path`
- Sensitive sink: `historical query trust state`

## Impact Pattern

- Primary impact: `query-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Historical query state access should only use consensus state derived from a runtime header that has been checked against the expected runtime identity and associated consensus block. In this pattern, historical-query handling did not have a clearly enforced verification step in the shown interface/dispatch path, so query consumers could rely on weaker validation than the normal verifier path. The evidence supports missing or insufficient query-time binding checks, not stronger claims such as signature bypass or replay exploitation. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
