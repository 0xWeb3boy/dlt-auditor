# Validation Card

## Metadata

- ID: `rippled-2013-02-26-rippled-consensus-bd3d28c2f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`

## What Confirmed The Issue

- Evidence 1: Commit subject identifies a race window affecting consensus entry with the wrong last closed ledger.
- Evidence 2: Patch modifies NetworkOPs consensus startup logic, including haveConsensusObject(), checkState(), and beginConsensus() flow.

## What Could Have Invalidated It

- Compensating control 1: No proof that an untrusted peer can reliably trigger the race.
- Compensating control 2: No tests, traces, or incident notes demonstrating practical exploitation.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: consensus-failure
- Expected severity band: high

## False-Positive Cautions

- Caution 1: No proof that an untrusted peer can reliably trigger the race.
- Caution 2: No tests, traces, or incident notes demonstrating practical exploitation.
