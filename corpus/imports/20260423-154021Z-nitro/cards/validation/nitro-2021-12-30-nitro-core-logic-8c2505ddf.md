# Validation Card

## Metadata

- ID: `nitro-2021-12-30-nitro-core-logic-8c2505ddf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-state-management`

## What Confirmed The Issue

- Evidence 1: The supplied diff supports validator-machine state-management hardening: validation now fetches a host-IO machine before cloning, and mutators now reject frozen machines.
- Evidence 2: Fetch the canonical base object at use time and add fail-closed guards to mutating APIs so shared or frozen instances cannot be modified silently.

## What Could Have Invalidated It

- Compensating control 1: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
- Compensating control 2: If the path is test-only or offline tooling only, treat similar issues as lower-severity hardening.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
- Caution 2: Do not claim chain-wide divergence without evidence that the wrong state can be persisted, signed, or submitted onward.
