# Validation Card

## Metadata

- ID: `optimism-2025-02-06-optimism-storage-6fb1a6d8e0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `proof-validation-hardening`

## What Confirmed The Issue

- The code runs in an interop fault-proof client state-transition function, a security-sensitive claim-validation path.
- mod.rs adds an explicit boundary check and returns InvalidClaim when a no-op transition's claimed post-state does not equal the agreed pre-state commitment.
- transition.rs changes derivation from claimed_l2_block_number to disputed_l2_block_number, tightening validation to the exact disputed step.
- The patch removes a separate timestamp mismatch rejection and instead relies on corrected transition semantics plus commitment equality, indicating stricter invariant enforcement rather than product work or refactoring.

## What Could Have Invalidated It

- No test or advisory evidence shows the old code could actually be exploited to win a false dispute or finalize an invalid state.
- The diff does not show whether the pre-fix behavior accepted invalid claims, rejected valid claims, or both.
- No deployment impact, reachable attacker conditions, or real-world exploit scenario is provided.
- an earlier boundary already rejects the same malformed field under all reachable modes

## Severity Guidance

- Expected impact band: consensus-or-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No test or advisory evidence shows the old code could actually be exploited to win a false dispute or finalize an invalid state.
- The diff does not show whether the pre-fix behavior accepted invalid claims, rejected valid claims, or both.
- No deployment impact, reachable attacker conditions, or real-world exploit scenario is provided.
