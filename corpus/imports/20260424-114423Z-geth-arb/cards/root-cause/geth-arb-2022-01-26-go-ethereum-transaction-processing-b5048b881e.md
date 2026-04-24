# Root-Cause Card

## Metadata

- ID: `geth-arb-2022-01-26-go-ethereum-transaction-processing-b5048b881e`
- Bug family: `authz_and_role_gates`
- Bug class: `sequencer-fee-policy-bypass`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `sequencer-admission-policy`

## Violated Invariant

- Invariant: Sequencer admission should enforce the authoritative fee-recipient or aggregator policy before accepting transactions into privileged ordering paths.

## Trust Boundary

- Boundary: user transaction -> sequencer admission policy

## Attack Surface

- Entrypoint type: sequencer transaction admission filter
- Sensitive sink: sequencer ordering and fee-routing decision

## Impact Pattern

- Primary impact: economic-policy-enforcement
- Secondary impact: sequencer-integrity
- Severity guide: medium

## Short Reusable Lesson

- The sequencer needed to reject transactions whose preferred aggregator did not match the configured sequencer fee recipient. Read the sender preference at admission and reject transactions whose aggregator does not match the sequencer address.
