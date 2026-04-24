# Validation Card

## Metadata

- ID: `optimism-2024-10-21-optimism-storage-4e4687ff75`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `chain-continuity-validation`

## What Confirmed The Issue

- CrossUnsafeUpdate switches candidate selection to crossUnsafe.Number+1 rather than the wrong reference frontier.
- The new bl.ParentHash != crossUnsafe.Hash check rejects promotion of a block that does not build on the current cross-unsafe head.
- The check returns ErrConflict, showing the code now treats frontier discontinuity as an invalid state transition.
- The changed logic is in supervisor cross-chain frontier advancement, a security-sensitive state/integrity path rather than ordinary product UI or maintenance code.

## What Could Have Invalidated It

- No proof that attacker-controlled input can reach and exploit the pre-patch behavior.
- No test, incident, or advisory evidence showing consensus failure, message forgery, fund impact, or production compromise.
- The commit message is generic and does not describe a vulnerability or security incident.
- The added DB/query helper methods are supportive plumbing; the diff alone does not show them fixing an independently exploitable issue.

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that attacker-controlled input can reach and exploit the pre-patch behavior.
- No test, incident, or advisory evidence showing consensus failure, message forgery, fund impact, or production compromise.
- The commit message is generic and does not describe a vulnerability or security incident.
