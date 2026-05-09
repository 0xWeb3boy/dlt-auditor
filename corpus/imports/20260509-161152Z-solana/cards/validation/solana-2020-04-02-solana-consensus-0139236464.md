# Validation Card

## Metadata

- ID: `solana-2020-04-02-solana-consensus-0139236464`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-vote-guard-hardening`

## What Confirmed The Issue

- Patch changes Solana `ReplayStage` fork-selection and vote-decision logic, a consensus-sensitive validator path.
- Final voting predicate changes from requiring lockout, vote threshold, and propagation confirmation to also requiring `switch_threshold`.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: integrity_or_funds
- Expected severity band: High
- Rationale: The impact can affect funds, consensus safety, authorization boundaries, or runtime integrity when reachable.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
