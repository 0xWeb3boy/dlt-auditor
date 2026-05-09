# Validation Card

## Metadata

- ID: `nibiru-2026-04-27-nibiru-transaction-processing-224de766`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## What Confirmed The Issue

- Evidence 1: The patch changes the runtime path at the named sensitive sink: FunToken mapping registry and fee/registration flow.
- Evidence 2: The validated finding ties the change to this invariant: Creation of mainnet asset mappings that bind external token contracts to native denominations must be restricted to governance, authority, or explicitly permissioned accounts.

## What Could Have Invalidated It

- Compensating control 1: Non-mainnet permissionless mapping may be intentional
- Compensating control 2: Creation fees do not replace authorization for privileged registries

## Severity Guidance

- Expected impact band: `access_control`
- Expected severity band: `high`

## False-Positive Cautions

- Caution 1: Distinguish proven issues from likely hardening; this case is `likely` and `security-hardening`.
- Caution 2: Unauthorized mainnet asset mapping can become a launch point for bridge abuse, but direct asset compromise was not proven in the validation output.
