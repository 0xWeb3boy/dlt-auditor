# Validation Card

## Metadata

- ID: `rippled-2025-10-31-rippled-transaction-processing-fa6991812`
- Bug family: `authz_and_role_gates`
- Bug class: `improper-authorization`

## What Confirmed The Issue

- Evidence 1: Commit subject says it addresses a permission delegation vulnerability.
- Evidence 2: Commit body says checkPermission now returns terNO_DELEGATE_PERMISSION when a delegate transaction lacks necessary permissions.

## What Could Have Invalidated It

- Compensating control 1: No full diff or tests are provided to prove the complete exploit scenario.
- Compensating control 2: No evidence shows exploitation in the wild or actual fund loss.

## Severity Guidance

- Expected impact band: security-impact: authorization-bypass, unauthorized-delegated-transaction
- Expected severity band: high

## False-Positive Cautions

- Caution 1: No full diff or tests are provided to prove the complete exploit scenario.
- Caution 2: No evidence shows exploitation in the wild or actual fund loss.
