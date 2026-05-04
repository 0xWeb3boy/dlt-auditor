# Validation Card

## Metadata

- ID: `fuel-core-2026-03-07-fuel-core-consensus-6bf947e26d`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `consensus-safety`
- Security verdict: `likely`
- Validated as: `security-fix`

## What Confirmed The Issue

- Patch changes read_stream_entries_on_node return type to anyhow::Result<Vec<...>>.
- Added test documents fork risk when Redis read calls fail on a quorum.

## What Could Have Invalidated It

- A separate durable local log always repairs the missing Redis data before production.
- Leader election cannot proceed unless all required backend reads succeed.

## Severity Guidance

- Expected impact band: `high`
- Expected severity band: `high`
- Rationale: Treating unavailable committed state as empty can let a leader skip blocks and fork. Evidence cites commit/test context, so high is warranted even if active attacker control is not proven.

## False-Positive Cautions

- No issue if quorum reconciliation independently requires successful reads.
- No issue if an empty stream cannot authorize production or state advancement.
