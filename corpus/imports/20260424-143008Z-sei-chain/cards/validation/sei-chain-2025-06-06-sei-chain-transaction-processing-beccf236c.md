# Validation Card

## Metadata

- ID: `sei-chain-2025-06-06-sei-chain-transaction-processing-beccf236c`
- Bug family: `authz_and_role_gates`
- Bug class: `validation-bypass-hardening`

## What Confirmed The Issue

- Evidence 1: Vote now constructs MsgVote, calls ValidateBasic, and dispatches through govMsgServer.Vote instead of directly calling govKeeper.AddVote.
- Evidence 2: Deposit now constructs MsgDeposit, calls ValidateBasic, and dispatches through govMsgServer.Deposit instead of directly calling govKeeper.AddDeposit.

## What Could Have Invalidated It

- Compensating control 1: The direct keeper method performs exactly the same validation.
- Compensating control 2: The precompile method is read-only or disabled.

## Severity Guidance

- Expected impact band: protocol-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: The direct keeper method performs exactly the same validation.
- Caution 2: The precompile method is read-only or disabled.
