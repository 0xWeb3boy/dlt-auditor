# Validation Card

## Metadata

- ID: `thor-2025-10-24-thor-core-logic-7c638e51`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `unchecked-numeric-conversion`

## What Confirmed The Issue

- IncreaseStake, DecreaseStake, and AddDelegation now check ToVET conversion errors before state changes.
- ContractBalanceCheck now returns conversion errors before continuing reconciliation.
- Phase 4 kept the finding as likely `security-hardening`, not as a confirmed vulnerability.

## What Could Have Invalidated It

- ToVET cannot overflow or fail for all possible externally supplied amounts.
- The downstream staking methods independently validate the original unconverted amount.

## Severity Guidance

- Expected impact band: medium accounting integrity hardening
- Expected severity band: `medium_or_low`
- Rationale: Unchecked conversion on consensus-executed staking state is security-relevant and could affect accounting integrity, but the validated finding does not prove theft, validator takeover, or consensus divergence.

## False-Positive Cautions

- No issue if conversion is total and cannot fail for any reachable input.
- No issue if the unchecked value is used only for display or logging.
- Do not flag call sites that already revert or return on conversion error.
