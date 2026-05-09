# Validation Card

## Metadata

- ID: `nibiru-2024-10-24-nibiru-rpc-client-api-dd27f4b6`
- Bug family: `resource_accounting_and_limits`
- Bug class: `evm-gas-resource-control-hardening`

## What Confirmed The Issue

- Evidence 1: The patch changes the runtime path at the named sensitive sink: EVM execution with gas consumption and cached-context commit behavior.
- Evidence 2: The validated finding ties the change to this invariant: System-mediated contract calls must run under a predictable gas cap and must not commit intermediate state when the contract reverts or errors.

## What Could Have Invalidated It

- Compensating control 1: Do not classify ordinary eth_call gas configuration as security without attacker-controlled contract execution
- Compensating control 2: Need evidence that helper is reachable from state-changing protocol code

## Severity Guidance

- Expected impact band: `resource_control`
- Expected severity band: `medium`

## False-Positive Cautions

- Caution 1: Distinguish proven issues from likely hardening; this case is `likely` and `security-hardening`.
- Caution 2: Resource exhaustion and accidental state commit are serious hardening targets, but the validated evidence did not show a concrete exploit or chain halt.
