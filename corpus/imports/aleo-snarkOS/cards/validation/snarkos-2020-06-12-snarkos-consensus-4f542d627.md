# Validation Card

## Metadata

- ID: `snarkos-2020-06-12-snarkos-consensus-4f542d627`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-difficulty-validation`

## What Confirmed The Issue

- The raw finding was validated by phase 4 as `security-fix` with verdict `likely` and kept in the security corpus.
- The patch pattern matches the missing property: Recompute expected difficulty inside header verification, add a mismatch error, and cover the rejection path with a regression test.
- Root-cause evidence from the finding: The header validation path appears to have failed to enforce that the header-supplied difficulty target matched the difficulty value computed by consensus rules. 1. A block header reaches `ConsensusParameters::verify_header` with a supplied `difficulty_target`. 2. The commit message says headers with invalid difficulty could previously be accepted because the supplied difficulty was not checked against the expected one. 3. The patch computes a single `now` timestamp and derives `expected_difficu

## What Could Have Invalidated It

- Later validation stage rejects mismatched difficulty before insertion.
- Header cannot be peer supplied in the affected deployment.

## Severity Guidance

- Expected impact band: `consensus-integrity`
- Expected severity band: `high`
- Rationale: High severity is appropriate when the affected boundary is reachable and the sink controls invalid header acceptance; reduce severity when the change is only hardening or a compensating control already enforces the invariant.

## False-Positive Cautions

- If downstream consensus validation repeats the same check, this path may be redundant
- Test-only header constructors are not security sinks
- Difficulty fields that are metadata only do not carry consensus impact
