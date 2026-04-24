# Validation Card

## Metadata

- ID: `rippled-2025-04-30-rippled-access-control-ceeb11aee`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `ledger-state-invariant-hardening`

## What Confirmed The Issue

- Evidence 1: Patch adds an sfOwnerCount != 0 check to AccountRootsDeletedClean::finalize for deleted accounts.
- Evidence 2: The new check follows existing invariant enforcement behavior with fatal logging, XRPL_ASSERT, and false return when enforce is enabled.

## What Could Have Invalidated It

- Compensating control 1: No supplied evidence shows normal transaction processing could previously delete such an account.
- Compensating control 2: No concrete exploit path, attacker-controlled trigger, fund loss, or denial-of-service impact is shown.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: ledger-state-integrity
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No supplied evidence shows normal transaction processing could previously delete such an account.
- Caution 2: No concrete exploit path, attacker-controlled trigger, fund loss, or denial-of-service impact is shown.
