# Validation Card

## Metadata

- ID: `rippled-2026-04-09-rippled-storage-87e951470`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## What Confirmed The Issue

- Evidence 1: Transactor::checkPermission now reads the delegate ledger entry and rejects missing delegate permission with terNO_DELEGATE_PERMISSION.
- Evidence 2: The central permission path distinguishes full transaction permission from granular permissions before allowing delegated execution.

## What Could Have Invalidated It

- Compensating control 1: No regression test excerpt demonstrates the pre-patch unauthorized behavior.
- Compensating control 2: No attacker preconditions or exploit sequence are shown.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: privilege-misuse
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: No regression test excerpt demonstrates the pre-patch unauthorized behavior.
- Caution 2: No attacker preconditions or exploit sequence are shown.
