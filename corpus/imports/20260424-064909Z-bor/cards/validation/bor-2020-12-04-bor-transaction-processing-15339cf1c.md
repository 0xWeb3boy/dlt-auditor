# Validation Card

## Metadata

- ID: `bor-2020-12-04-bor-transaction-processing-15339cf1c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsigned-advisory-feed`

## What Confirmed The Issue

- Commit body explicitly says the vulnerability feed is verified with Minisign.
- New files include version_check.go, tests, signature fixtures, and public-key fixtures, consistent with signed-feed verification.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No behavioral code excerpt from version_check.go shows exactly how verification is enforced.
- No evidence shows a pre-existing production path that accepted unsigned or untrusted advisory data.
