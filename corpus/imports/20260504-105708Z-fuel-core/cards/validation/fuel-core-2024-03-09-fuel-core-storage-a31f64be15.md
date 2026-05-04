# Validation Card

## Metadata

- ID: `fuel-core-2024-03-09-fuel-core-storage-a31f64be15`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `txpool-blacklist-enforcement`
- Security verdict: `likely`
- Validated as: `security-hardening`

## What Confirmed The Issue

- Patch adds check_blacklisting on PoolTransaction before insert_inner.
- Regression test asserts insertion fails for a transaction using a blacklisted UTXO id.

## What Could Have Invalidated It

- All submit paths already enforce the same denylist before reaching txpool.
- The blacklist is not enabled or not intended to affect admission.

## Severity Guidance

- Expected impact band: `medium`
- Expected severity band: `medium`
- Rationale: Bypassing a local blacklist can undermine node policy and propagate unwanted transactions, but the evidence does not show consensus corruption or asset loss.

## False-Positive Cautions

- A blacklist feature that is purely informational is not security-relevant.
- Consensus-valid transactions should not be rejected globally unless this is explicitly local policy.
