# Validation Card

## Metadata

- ID: `optimism-2025-01-10-optimism-storage-77ece638bd`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-validation`

## What Confirmed The Issue

- ChainsDB.Check now requires an expected timestamp and rejects mismatched includedIn.Timestamp.
- CrossUnsafeHazards adds an explicit conflict when the located block timestamp differs from the message timestamp.
- Iterator handling preserves stop-state on ErrStop, avoiding loss of the matched sealed-block position.
- Contains now errors if traversal stops without a real sealed block, removing an ambiguous success path.

## What Could Have Invalidated It

- No proof that untrusted or adversarial input could reach and exploit the pre-fix behavior.
- No demonstrated consensus break, fund loss, privilege gain, or remote attack path.
- No evidence that the old behavior was used to bypass authorization or forge messages in production.
- Test details are not specific enough to prove concrete exploitability.

## Severity Guidance

- Expected impact band: consensus-or-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that untrusted or adversarial input could reach and exploit the pre-fix behavior.
- No demonstrated consensus break, fund loss, privilege gain, or remote attack path.
- No evidence that the old behavior was used to bypass authorization or forge messages in production.
