# Validation Card

## Metadata

- ID: `sui-2023-04-08-sui-storage-e0c1591d99`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rpc-object-digest-validation`

## What Confirmed The Issue

- Commit message explicitly frames the change as hardening and improving trustworthiness of balanceChanges.
- fetch_coins now accepts optional ObjectDigest values alongside object id and version.
- The patch adds assert_eq! comparing the expected digest with o.digest() before coin data is used.
- get_balance_changes_from_effect preserves digests from changed object refs instead of dropping them.

## What Could Have Invalidated It

- No exploit scenario or attacker-controlled path is shown.
- No evidence of consensus or validator acceptance logic being fixed.
- No proof of direct fund loss, double spend, or balance mutation.
- No tests or incident report are provided in the supplied input.

## Severity Guidance

- Expected impact band: rpc-reporting-integrity_or_client-view-divergence
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Valid as RPC balance reporting integrity hardening only.
- Do not claim this fixes core on-chain state transition correctness.
- Do not claim validators previously accepted forged or mismatched objects.
- Do not claim direct theft, double spend, or asset loss from the supplied evidence.
