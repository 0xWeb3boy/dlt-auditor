# Validation Card

## Metadata

- ID: `nibiru-2026-04-27-nibiru-transaction-processing-7395c52e`
- Bug family: `authz_and_role_gates`
- Bug class: `callback-context-access-control`

## What Confirmed The Issue

- Evidence 1: The patch changes the runtime path at the named sensitive sink: mutable native precompile method execution.
- Evidence 2: The validated finding ties the change to this invariant: A privileged or module-originated callback context must not be allowed to invoke mutable native precompile methods unless that context is explicitly authorized for the method.

## What Could Have Invalidated It

- Compensating control 1: Do not flag query/view precompiles that cannot mutate state
- Compensating control 2: Need evidence the context flag corresponds to privileged/module-originated execution

## Severity Guidance

- Expected impact band: `access_control`
- Expected severity band: `high`

## False-Positive Cautions

- Caution 1: Distinguish proven issues from likely hardening; this case is `likely` and `security-hardening`.
- Caution 2: Callback-context authorization failures can expose privileged native sinks, but the validated case remains likely hardening without demonstrated loss.
