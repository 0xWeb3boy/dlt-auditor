# Validation Card

## Metadata

- ID: `firedancer-2025-10-01-firedancer-core-logic-fd99d9175`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `hardening-or-correctness-fix`

## What Confirmed The Issue

- Evidence 1: Commit subject says the change fixes guarded account uninitialized reads.
- Evidence 2: Patch changes uninitialized stack declarations of `fd_guarded_borrowed_account_t` to `= {0}` before borrow-helper calls.

## What Could Have Invalidated It

- Compensating control 1: No macro or helper implementation is provided to show the exact field read before initialization.
- Compensating control 2: No exploit path, attacker-controlled stale stack data, or privilege impact is demonstrated.

## Severity Guidance

- Expected impact band: low
- Expected severity band: low

## False-Positive Cautions

- Caution 1: No macro or helper implementation is provided to show the exact field read before initialization.
- Caution 2: No exploit path, attacker-controlled stale stack data, or privilege impact is demonstrated.
