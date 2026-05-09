# Validation Card

## Metadata

- ID: `nibiru-2024-08-14-nibiru-transaction-processing-e54ce5ce`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `accounting-or-state-drift`

## What Confirmed The Issue

- Evidence 1: The patch changes the runtime path at the named sensitive sink: bank mint/burn and module-to-user bank transfer.
- Evidence 2: The validated finding ties the change to this invariant: A token bridge must conserve value according to the origin of the mapped asset: returning a wrapped representation should release existing backing or burn representation, not mint new backing supply.

## What Could Have Invalidated It

- Compensating control 1: Do not flag ERC20-origin mappings that legitimately mint/burn native representation
- Compensating control 2: Need evidence of runtime mint/burn path, not only metadata setup

## Severity Guidance

- Expected impact band: `economic_integrity`
- Expected severity band: `high`

## False-Positive Cautions

- Caution 1: Distinguish proven issues from likely hardening; this case is `likely` and `security-hardening`.
- Caution 2: Incorrect mint-versus-release behavior in a bridge can inflate or desynchronize supply, though direct attacker profit was not proven.
