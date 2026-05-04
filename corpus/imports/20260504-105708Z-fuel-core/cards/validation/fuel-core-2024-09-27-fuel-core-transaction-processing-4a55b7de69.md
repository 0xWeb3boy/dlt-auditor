# Validation Card

## Metadata

- ID: `fuel-core-2024-09-27-fuel-core-transaction-processing-4a55b7de69`
- Bug family: `resource_accounting_and_limits`
- Bug class: `consensus-resource-limit-enforcement`
- Security verdict: `likely`
- Validated as: `security-hardening`

## What Confirmed The Issue

- Patch wires block_transaction_size_limit into executor remaining-resource logic.
- Patch updates transaction selector tests and accounting around selected transaction size.

## What Could Have Invalidated It

- The parameter is advisory only.
- Block validation independently enforces the same size limit and producer-side over-selection cannot affect availability.

## Severity Guidance

- Expected impact band: `medium`
- Expected severity band: `medium`
- Rationale: Unenforced consensus limits can create oversized blocks or wasted execution work. Evidence supports hardening rather than a demonstrated exploit.

## False-Positive Cautions

- No issue if the limit is feature-gated and not active on any network.
- No issue if another consensus check rejects oversized blocks before propagation or commit.
