# Code-Shape Card

## Metadata

- ID: `rippled-2023-03-20-rippled-transaction-processing-305c9a8d6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `identifier-collision`

## Code Shape Summary

- Confirmed protocol security fix for duplicate NFTokenID creation. The provided commit message and changed code show that the old mint and account deletion rules could allow an issuer to burn an NFT, delete and recreate the account, then mint another NFT with matching ID inputs... Reusable shape: check for input-and-state-invariant-validation was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: transaction-handler missing exact input-and-state-invariant-validation check before ledger state, balance/reserve accounting, or transaction authorization outcome
- Motif 2: security-sensitive path reaches ledger state, balance/reserve accounting, or transaction authorization outcome before rejecting malformed, stale, or unauthorized input
- Motif 3: Persist the lifecycle state needed for protocol identifier uniqueness and prevent destructive lifecycle transitions until their sequence ranges cannot collide after account recreation.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger state, balance/reserve accounting, or transaction authorization outcome unless the input-and-state-invariant-validation gate runs before the state-changing branch.

## Patch Pattern

- Persist the lifecycle state needed for protocol identifier uniqueness and prevent destructive lifecycle transitions until their sequence ranges cannot collide after account recreation.

## False Match Warnings

- No supplied evidence proves asset theft, direct monetary loss, or marketplace exploitation.
- No supplied evidence proves consensus failure beyond duplicate NFT identity/state integrity risk.
