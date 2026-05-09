# Validation Card

## Metadata

- ID: `nibiru-2026-01-22-nibiru-rpc-client-api-59336f71`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-nondeterminism`

## What Confirmed The Issue

- Evidence 1: The patch changes the runtime path at the named sensitive sink: validator miss counters, reward distribution, and emitted validator performance events.
- Evidence 2: The validated finding ties the change to this invariant: Consensus-visible state updates and event outputs must be derived from deterministic iteration over collections on every validator.

## What Could Have Invalidated It

- Compensating control 1: Map iteration in read-only RPC code is not consensus-critical
- Compensating control 2: Sorting only for presentation does not fix state write nondeterminism elsewhere

## Severity Guidance

- Expected impact band: `consensus_safety`
- Expected severity band: `critical`

## False-Positive Cautions

- Caution 1: Distinguish proven issues from likely hardening; this case is `confirmed` and `security-fix`.
- Caution 2: Confirmed nondeterministic consensus execution can produce AppHash mismatches and halt/fork the network.
