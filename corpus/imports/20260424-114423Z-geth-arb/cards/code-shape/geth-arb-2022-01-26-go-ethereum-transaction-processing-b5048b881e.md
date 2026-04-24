# Code-Shape Card

## Metadata

- ID: `geth-arb-2022-01-26-go-ethereum-transaction-processing-b5048b881e`
- Bug family: `authz_and_role_gates`
- Bug class: `sequencer-fee-policy-bypass`

## Code Shape Summary

- The sequencer needed to reject transactions whose preferred aggregator did not match the configured sequencer fee recipient.

## Search Motifs

- sequencer accepts transaction before fee-recipient preference check
- admission policy depends on account metadata but is not enforced
- privileged ordering path ignores user-selected aggregator mismatch
- authorization predicate combines boolean result and error handling unsafely
- policy warning is advisory where fail-closed behavior is expected
- privileged sink accepts caller-controlled authority or destination parameter

## Typical Asymmetry

- The vulnerable asymmetry is fail-open authorization: policy, role, or trusted-parameter state was weaker at the entrypoint than at the privileged sink sequencer ordering and fee-routing decision.

## Patch Pattern

- Read the sender preference at admission and reject transactions whose aggregator does not match the sequencer address.

## False Match Warnings

- a separate mandatory role check guards the sink
- errors fail closed before privilege is granted
- the changed path only affects local diagnostics and not authorization or privilege
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
