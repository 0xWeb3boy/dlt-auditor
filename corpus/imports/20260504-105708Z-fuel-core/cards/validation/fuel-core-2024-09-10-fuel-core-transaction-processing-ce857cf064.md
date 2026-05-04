# Validation Card

## Metadata

- ID: `fuel-core-2024-09-10-fuel-core-transaction-processing-ce857cf064`
- Bug family: `resource_accounting_and_limits`
- Bug class: `resource-limit-enforcement`
- Security verdict: `likely`
- Validated as: `security-hardening`

## What Confirmed The Issue

- Patch adds try_fold accounting in GraphQL dry_run.
- Executor now checks transaction.max_gas against remaining_gas_limit before processing.

## What Could Have Invalidated It

- All expensive execution happens only after lower-layer gas checks.
- The path is unreachable by untrusted users and used only in tests.

## Severity Guidance

- Expected impact band: `medium`
- Expected severity band: `medium`
- Rationale: Missing max_gas checks can waste local execution resources or admit over-budget work. The finding is hardening because no concrete exhaustion threshold was proven.

## False-Positive Cautions

- No issue if the VM enforces the same limit before expensive work.
- A pure error-message cleanup around gas accounting is not enough.
