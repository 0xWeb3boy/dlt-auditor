# Code-Shape Card

## Metadata

- ID: `snarkos-2026-01-27-snarkos-rpc-client-api-7cdc93d7d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-peer-penalty-for-invalid-consensus-version`

## Code Shape Summary

- Consensus-version block-response errors are detected but not consistently escalated into peer penalties, so invalid or forked peers can remain available.

## Search Motifs

- NoConsensusVersion or ConsensusVersionMismatch without ban
- invalid block response error arm logs and returns
- ban peer when insert_block_responses returns consensus-version error

## Typical Asymmetry

- The code has a validation, authentication, sizing, correlation, or peer-enforcement concept nearby, but the specific inbound path either does not call it, ignores its result, signs too little data, or maps failure to a log/return instead of a state-changing rejection.

## Patch Pattern

- Add peer penalties at block-response ingress points for missing or mismatched consensus-version InsertBlockResponseError cases.

## False Match Warnings

- During planned upgrades, temporary mismatch may be handled by softer policy
- This does not imply invalid block insertion if validation already rejects
- Trusted static peers may use different enforcement policy
