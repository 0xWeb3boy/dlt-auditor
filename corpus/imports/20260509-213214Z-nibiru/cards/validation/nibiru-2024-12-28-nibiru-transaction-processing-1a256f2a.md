# Validation Card

## Metadata

- ID: `nibiru-2024-12-28-nibiru-transaction-processing-1a256f2a`
- Bug family: `resource_accounting_and_limits`
- Bug class: `recursive-gas-forwarding`

## What Confirmed The Issue

- Evidence 1: The patch changes the runtime path at the named sensitive sink: recursive CallContract execution and transaction gas meter.
- Evidence 2: The validated finding ties the change to this invariant: Nested contract calls made by protocol helpers must forward gas from the transaction remaining budget, not grant each recursive call a fresh fixed allowance.

## What Could Have Invalidated It

- Compensating control 1: Do not flag single non-recursive helper calls with bounded gas
- Compensating control 2: Need attacker-controlled callee code or reentry route

## Severity Guidance

- Expected impact band: `resource_control`
- Expected severity band: `medium`

## False-Positive Cautions

- Caution 1: Distinguish proven issues from likely hardening; this case is `likely` and `security-hardening`.
- Caution 2: Recursive gas grant bugs can amplify resource use; the evidence supports hardening but not theft or consensus failure.
