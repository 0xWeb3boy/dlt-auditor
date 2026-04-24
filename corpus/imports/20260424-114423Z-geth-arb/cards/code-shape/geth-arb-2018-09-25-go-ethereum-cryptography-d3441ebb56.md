# Code-Shape Card

## Metadata

- ID: `geth-arb-2018-09-25-go-ethereum-cryptography-d3441ebb56`
- Bug family: `authz_and_role_gates`
- Bug class: `signer-boundary-policy-hardening`

## Code Shape Summary

- The signer boundary treated validation warnings as continuable by default instead of rejecting before UI-mediated signing.

## Search Motifs

- signer validation warning defaults to continue
- policy result is advisory before key use
- UI signing prompt appears after validation failure
- authorization predicate combines boolean result and error handling unsafely
- policy warning is advisory where fail-closed behavior is expected
- privileged sink accepts caller-controlled authority or destination parameter

## Typical Asymmetry

- The vulnerable asymmetry is fail-open authorization: policy, role, or trusted-parameter state was weaker at the entrypoint than at the privileged sink user-mediated or policy-mediated signature generation.

## Patch Pattern

- Make warning or policy rejection fail closed by default, with explicit handling for warning-only flows.

## False Match Warnings

- a separate mandatory role check guards the sink
- errors fail closed before privilege is granted
- the changed path only affects local diagnostics and not authorization or privilege
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
