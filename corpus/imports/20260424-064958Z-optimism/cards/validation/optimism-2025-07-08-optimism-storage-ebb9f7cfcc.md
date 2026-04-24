# Validation Card

## Metadata

- ID: `optimism-2025-07-08-optimism-storage-ebb9f7cfcc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `derivation-state-consistency`

## What Confirmed The Issue

- Production logic now rejects inconsistent non-newer derived block pairs by loading the stored pair at the same derived height.
- The changed code is in supervisor derivation/reset state handling, which is an integrity-sensitive path for chain state.
- Tests were strengthened to require reset paths to return errors on authentication/RPC failures instead of merely avoiding panics.
- The evidence points to a state-validation bug in derivation replay/reset handling: non-newer incoming derived pairs were checked against the latest state rather than the stored pair at the same derived height.

## What Could Have Invalidated It

- No evidence shows attacker control over the incoming derived pair or reset inputs.
- No patch evidence demonstrates concrete exploitation, privilege gain, auth bypass, or direct fund impact.
- The authentication-themed changes shown are test-only and do not prove a production authentication flaw was fixed.
- an earlier boundary already rejects the same malformed field under all reachable modes

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No evidence shows attacker control over the incoming derived pair or reset inputs.
- No patch evidence demonstrates concrete exploitation, privilege gain, auth bypass, or direct fund impact.
- The authentication-themed changes shown are test-only and do not prove a production authentication flaw was fixed.
