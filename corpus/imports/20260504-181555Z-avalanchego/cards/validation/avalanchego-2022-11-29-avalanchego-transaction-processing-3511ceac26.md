# Validation Card

## Metadata

- ID: `avalanchego-2022-11-29-avalanchego-transaction-processing-3511ceac26`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-replay-policy-hardening`

## What Confirmed The Issue

- Evidence: UnprotectedAllowed now receives the transaction and can make per-transaction decisions.
- Evidence: The new logic preserves the global allowUnprotectedTxs override but otherwise only allows hashes present in allowUnprotectedTxHashes.
- Evidence: Backend initialization builds a read-only allowUnprotectedTxHashes map from configuration.

## What Could Have Invalidated It

- Compensating control: No full transaction submission or RPC admission path is shown.
- Compensating control: No evidence shows arbitrary replayed transactions were accepted under default configuration before the patch.
- Compensating control: No exploit scenario, advisory, CVE, or demonstrated attacker impact is provided.

## Severity Guidance

- Expected impact band: medium_or_low_hardening
- Expected severity band: medium_or_low
- Severity rationale: The change narrows a risky compatibility exception, but the finding does not prove arbitrary replay acceptance in the default configuration.

## False-Positive Cautions

- Caution: Classify as security hardening rather than a confirmed security fix.
- Caution: Do not claim arbitrary replay, fund loss, or remote exploitability from the supplied patch alone.
- Caution: Do not claim the patch removes all unprotected transaction risk because the global override remains.
