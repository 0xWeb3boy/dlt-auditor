# Root-Cause Card

## Metadata

- ID: `geth-arb-2022-06-01-go-ethereum-transaction-processing-37c04d56b5`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `hardening-or-correctness-fix`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `withdrawal-destination-authority`

## Violated Invariant

- Invariant: Privileged withdrawal helpers should derive their destination from trusted contract or staker state, not from a caller-controlled parameter passed into the sensitive sink.

## Trust Boundary

- Boundary: validator/staker control flow -> privileged withdrawal sink

## Attack Surface

- Entrypoint type: validator withdrawal or staker fund-recovery path
- Sensitive sink: withdrawal of staker funds to a destination address

## Impact Pattern

- Primary impact: funds-safety
- Secondary impact: authorization-bypass-prevention
- Severity guide: low-medium

## Short Reusable Lesson

- The withdrawal path was hardened by removing configurable withdrawal destinations from the staker flow and relying on the privileged sink to use its trusted destination semantics. Narrow the sensitive sink signature by removing caller-controlled destination input and route withdrawals through the fixed trusted-destination helper.
