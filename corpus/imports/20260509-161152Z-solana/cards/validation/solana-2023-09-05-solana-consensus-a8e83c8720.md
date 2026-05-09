# Validation Card

## Metadata

- ID: `solana-2023-09-05-solana-consensus-a8e83c8720`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-duplicate-slot-state-recovery`

## What Confirmed The Issue

- ReplayStage now checks Blockstore for previously recorded duplicate slots when the in-memory duplicate_slots_tracker lacks the slot.
- Recovered duplicate states are passed into check_slot_agrees_with_cluster on Dead and BankFrozen slot transitions.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: integrity_or_funds
- Expected severity band: Low/Medium
- Rationale: The finding is useful security-hardening evidence; severity depends on reachability and missing compensating controls.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
