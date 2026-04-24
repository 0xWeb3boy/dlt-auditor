# Validation Card

## Metadata

- ID: `optimism-2024-02-02-optimism-transaction-processing-e9172f60bb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `preimage-representation-confusion`

## What Confirmed The Issue

- Commit message explicitly says to exclude the length prefix for large preimage uploads and make OracleData private to avoid accidental misuse.
- Tests change claimedSize from len(data.OracleData) to len(data.GetPreimageWithoutSize()), showing size accounting now uses canonical raw bytes.
- Tests change uploaded payload expectations from data.OracleData to data.GetPreimageWithoutSize(), showing protocol-facing data no longer uses the prefixed form.
- Caller construction changes from direct struct field access to types.NewPreimageOracleData(...), which hardens the API against unsafe representation mixing.

## What Could Have Invalidated It

- No production-code hunk is shown from large.go, split.go, split.go, or types.go to prove the exact runtime bug and fix path.
- No evidence shows the old behavior caused accepted invalid uploads, failed dispute resolution, or another concrete exploitable outcome.
- No demonstrated impact such as fund loss, consensus break, privilege bypass, or attacker-controlled trigger is provided.
- an earlier boundary already rejects the same malformed field under all reachable modes

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: low_or_informational

## False-Positive Cautions

- No production-code hunk is shown from large.go, split.go, split.go, or types.go to prove the exact runtime bug and fix path.
- No evidence shows the old behavior caused accepted invalid uploads, failed dispute resolution, or another concrete exploitable outcome.
- No demonstrated impact such as fund loss, consensus break, privilege bypass, or attacker-controlled trigger is provided.
