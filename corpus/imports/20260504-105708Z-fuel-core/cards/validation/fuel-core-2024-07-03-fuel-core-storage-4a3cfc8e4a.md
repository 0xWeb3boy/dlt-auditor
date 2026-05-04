# Validation Card

## Metadata

- ID: `fuel-core-2024-07-03-fuel-core-storage-4a3cfc8e4a`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `stale-consensus-parameter-validation`
- Security verdict: `likely`
- Validated as: `security-hardening`

## What Confirmed The Issue

- Patch adds ConsensusParametersVersion to checked transaction variants.
- Executor now reads block_header.consensus_parameters_version before accepting checked transactions.

## What Could Have Invalidated It

- Txpool flushed on parameter changes.
- Checked transactions are used only for local hints and never for block inclusion.

## Severity Guidance

- Expected impact band: `high`
- Expected severity band: `high`
- Rationale: Stale cached validation can admit transactions under obsolete rules. That is plausibly consensus-relevant even though exploitability was not fully proven.

## False-Positive Cautions

- No issue if cached validation is invalidated on every parameter update.
- No issue if executor always revalidates against block header parameters before inclusion.
