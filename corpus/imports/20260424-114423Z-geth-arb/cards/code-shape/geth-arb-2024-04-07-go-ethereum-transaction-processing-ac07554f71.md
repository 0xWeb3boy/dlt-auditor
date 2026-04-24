# Code-Shape Card

## Metadata

- ID: `geth-arb-2024-04-07-go-ethereum-transaction-processing-ac07554f71`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control-error-handling`

## Code Shape Summary

- The owner branch in an access predicate accepted the wrong error condition, inverting the success/error handling for chain-owner access.

## Search Motifs

- authorization branch checks err != nil with owner true
- role lookup error is treated as permission
- access predicate combines boolean result and error incorrectly
- authorization predicate combines boolean result and error handling unsafely
- policy warning is advisory where fail-closed behavior is expected
- privileged sink accepts caller-controlled authority or destination parameter

## Typical Asymmetry

- The vulnerable asymmetry is fail-open authorization: policy, role, or trusted-parameter state was weaker at the entrypoint than at the privileged sink privileged cache mutation or chain-owner-only operation.

## Patch Pattern

- Require both ownership and a nil lookup error before granting access; treat errors as denial.

## False Match Warnings

- a separate mandatory role check guards the sink
- errors fail closed before privilege is granted
- the changed path only affects local diagnostics and not authorization or privilege
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
