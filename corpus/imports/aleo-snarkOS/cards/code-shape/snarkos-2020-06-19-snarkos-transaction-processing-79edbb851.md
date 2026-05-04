# Code-Shape Card

## Metadata

- ID: `snarkos-2020-06-19-snarkos-transaction-processing-79edbb851`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rpc-attack-surface-reduction`

## Code Shape Summary

- Sensitive or experimental RPC methods remain exported while nearby code indicates password/auth guarding is incomplete.

## Search Motifs

- comment indicating password guard missing near RPC method
- record or raw transaction helper in public RpcFunctions trait
- method removed from public API rather than validation logic changed

## Typical Asymmetry

- The code has a validation, authentication, sizing, correlation, or peer-enforcement concept nearby, but the specific inbound path either does not call it, ignores its result, signs too little data, or maps failure to a log/return instead of a state-changing rejection.

## Patch Pattern

- Remove the methods from the exported RPC trait/implementation surface pending a real protected wrapper or authentication scheme.

## False Match Warnings

- Private-loopback-only RPC deployments reduce exploitability
- Methods that only return public chain data may not be sensitive
- A reverse proxy or RPC auth layer may already enforce access
