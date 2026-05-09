# Validation Card

## Metadata

- ID: `solana-2019-02-15-solana-core-logic-132c664e18`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cross-program-state-mutation`

## What Confirmed The Issue

- Removed rewards-program calls to vote_state.clear_credits() and serialize() on keyed_accounts[0].account.userdata.
- Deleted comment explicitly stated the runtime should reject the write because the rewards program was not the owner of the VoteState account.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: state_integrity_or_policy_bypass
- Expected severity band: Medium
- Rationale: The issue was confirmed as a security fix, but the available evidence does not establish direct high-impact loss.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
