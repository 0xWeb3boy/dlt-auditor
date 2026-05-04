# Code-Shape Card

## Metadata

- ID: `snarkos-2020-08-15-snarkos-transaction-processing-8b5ad567b`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-authentication`

## Code Shape Summary

- Record RPC handlers sit on a public implementation surface instead of protected wrappers that call validate_auth before processing request parameters.

## Search Motifs

- protected wrapper added around previously public RPC method
- validate_auth(meta) inserted before Params matching
- record/decrypt/decode handler removed from public trait impl

## Typical Asymmetry

- The code has a validation, authentication, sizing, correlation, or peer-enforcement concept nearby, but the specific inbound path either does not call it, ignores its result, signs too little data, or maps failure to a log/return instead of a state-changing rejection.

## Patch Pattern

- Move record methods to protected RPC wrappers and call validate_auth(meta) before parsing params or invoking record logic.

## False Match Warnings

- Read-only public record metadata may be intentionally unauthenticated
- External RPC auth can compensate if it is mandatory
- Do not infer private-key compromise from record API movement alone
