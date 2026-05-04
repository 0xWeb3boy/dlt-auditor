# Root-Cause Card

## Metadata

- ID: `moonbeam-2020-05-13-moonbeam-cryptography-fb437475f4`
- Bug family: `authz_and_role_gates`
- Bug class: `improper-authorization`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization-bound-dispatch`

## Violated Invariant

- Invariant: Only payloads that have passed the runtime's unsigned validation/signature gate should be able to persist validator selections or session snapshots.

## Trust Boundary

- Boundary: Untrusted extrinsic submitters cross into session-authority storage that influences validator selection and reward/accounting state.

## Attack Surface

- Entrypoint type: unsigned-transaction-validation-path
- Sensitive sink: session validator and snapshot storage writes

## Impact Pattern

- Primary impact: unauthorized-action
- Secondary impact: state-integrity, validator-set-integrity

## Short Reusable Lesson

- A dispatchable accepted a signed origin and raw caller-provided vectors, then wrote session-critical storage directly. The patch moved the state update behind unsigned payloads plus a signature-bearing validation boundary. Replace raw signed-origin persistence calls with unsigned signed-payload calls validated by the runtime before session storage is mutated.
