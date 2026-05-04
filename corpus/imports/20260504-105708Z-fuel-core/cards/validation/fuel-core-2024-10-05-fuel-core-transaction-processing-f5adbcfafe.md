# Validation Card

## Metadata

- ID: `fuel-core-2024-10-05-fuel-core-transaction-processing-f5adbcfafe`
- Bug family: `resource_accounting_and_limits`
- Bug class: `graphql-query-complexity-accounting`
- Security verdict: `likely`
- Validated as: `security-hardening`

## What Confirmed The Issue

- Patch updates complexity annotations in block and tx GraphQL schemas.
- Raw finding notes multiple resolver formulas were adjusted for block/header/transaction status paths.

## What Could Have Invalidated It

- A gateway enforces independent request budgets below the expensive threshold.
- The changed fields are not exposed in production schema.

## Severity Guidance

- Expected impact band: `medium`
- Expected severity band: `medium`
- Rationale: Underpriced query complexity can allow expensive API work within nominal limits. It is likely hardening because a concrete exhaustion threshold was not shown.

## False-Positive Cautions

- No issue if the endpoint is private and separately rate-limited.
- No issue if the resolver ignores child selection or always performs constant work.
