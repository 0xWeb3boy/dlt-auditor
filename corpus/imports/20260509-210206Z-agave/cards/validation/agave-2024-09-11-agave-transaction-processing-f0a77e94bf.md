# Validation Card

## Metadata

- ID: `agave-2024-09-11-agave-transaction-processing-f0a77e94bf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `durable-nonce-consumption`

## What Confirmed The Issue

- The fix changes durable nonce fallback from check-and-load to check-load-and-advance.
- Rollback comments and code preserve already-advanced nonce data when nonce and fee payer are the same account.

## What Could Have Invalidated It

- A compensating check proves the old nonce could never be reused after rollback.
- The rollback path is unreachable for durable-nonce fee-only or failed transactions.

## Severity Guidance

- Expected impact band: `localized replay-protection failure`
- Expected severity band: `medium`
- Rationale: Nonce reuse can undermine replay protection for affected durable-nonce transactions, but the source evidence did not prove successful production replay, fund theft, or consensus divergence.

## False-Positive Cautions

- Do not classify ordinary nonce refactors as security unless rollback or fee-only handling can preserve stale nonce state.
- Do not infer signature bypass or fund theft without an end-to-end replay or authorization proof.
